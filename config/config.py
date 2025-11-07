from presidio_anonymizer.entities import OperatorConfig

# --- NLP Configuration ---
NLP_CONFIGURATION = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}

# Generate a proper key for encryption/decryption
# Presidio encrypt operator expects a raw key of 128, 192, or 256 bits (16, 24, or 32 bytes)
def generate_encryption_key():
    """Generate a proper encryption key for Presidio"""
    # Use a fixed seed for demonstration (don't do this in production!)
    # This ensures the same key is generated each time for demo purposes
    import hashlib
    seed = "presidio_demo_key_2024"
    key_bytes = hashlib.sha256(seed.encode()).digest()  # 32 bytes = 256 bits
    return key_bytes

encryption_key = generate_encryption_key()

# --- Anonymization Rules ---
ANONYMIZATION_RULES = {
    # Use keep for "PERSON" to leave names unchanged
    "PERSON": OperatorConfig(operator_name="keep"),
    
    # For "PHONE_NUMBER", use "mask"
    # Leave the first 3 characters visible and mask the rest with 'X'
    "PHONE_NUMBER": OperatorConfig(operator_name="mask", params={
        "masking_char": "X",
        "chars_to_mask": 9,
        "from_end": True
    }),
    
    # For "EMAIL_ADDRESS", use "redact" (remove completely)
    # "EMAIL_ADDRESS": OperatorConfig(operator_name="redact"),
    "EMAIL_ADDRESS": OperatorConfig(operator_name="replace", params={"new_value": "[HIDDEN_EMAIL]"}),
    
    # For the ID (NIF_CODE in Presidio), we replace it
    "NIF_CODE": OperatorConfig(operator_name="replace", params={"new_value": "[HIDDEN_ID]"}),
    
    # US Driver License replacement
    "US_DRIVER_LICENSE": OperatorConfig(operator_name="replace", params={"new_value": "[HIDDEN_DRIVER_LICENSE]"}),
    
    "CREDIT_CARD": OperatorConfig(operator_name="encrypt", params={"key": encryption_key}),
    
    "SSN": OperatorConfig(operator_name="replace", params={"new_value": "[HIDDEN_SSN]"}),
}

DEANONYMIZATION_RULES = {
    "CREDIT_CARD": OperatorConfig(operator_name="decrypt", params={"key": encryption_key}),
}

# --- Default Language ---
DEFAULT_LANGUAGE = "en"