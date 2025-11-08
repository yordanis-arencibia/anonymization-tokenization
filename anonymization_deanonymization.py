from utils.anonymizer_utils import PresidioAnonymizer

def main():
    # --- Initialize the anonymizer ---
    anonymizer = PresidioAnonymizer()
    
    # --- The Text we want to protect ---
    original_text = """
        My name is John Doe,
        my email is john.doe@gmail.com and 
        my phone number is +34 912 345 678. My ID is 12345678Z.
        my computer IP is 10.18.1.1 and my credit card is 4111 1111 1111 1111.
        I was born on 01/01/1985 and my SSN is 232323.
    """
    
    print(f"--- Original Text ---\n{original_text}\n")
    
    # --- Process the text (analyze and anonymize) ---
    anonymized_result, analyzer_results = anonymizer.process_text(
        text=original_text,
        show_analysis=True
    )

    # --- Show results ---
    print("--- Entities Detected by the Analyzer ---")
    print("The presidio analyzer detects the following entities in the text (internal process):")
    for result in analyzer_results:
        print(f"Entity: {result.entity_type}, Score: {result.score:.2f}, "
              f"Start: {result.start}, End: {result.end}, "
              f"Text: '{original_text[result.start:result.end]}'")
    print()
    
    print("--- Anonymized Text ---")
    print("the process of anonymization is irreversible for most entities (except encrypted ones).")
    print(anonymized_result.text)
    
    # --- Process the text (Deanonymized text) - Only for encrypted entities ---
    try:
        deanonymized_result = anonymizer.deanonymize_with_entities(anonymized_result.text, analyzer_results)
        print()
        print(f"--- Deanonymized Text ---\n{deanonymized_result.text}")
    except Exception as e:
        print(f"\n--- Deanonymization Note ---")
        print(f"Deanonymization only works for entities that were encrypted (reversible operations).")
        print(f"In this example, only CREDIT_CARD was encrypted, other entities used irreversible operations.")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()