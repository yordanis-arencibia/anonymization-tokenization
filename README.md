# Microsoft Presidio Anonymization Tutorial

This project demonstrates how to use Microsoft Presidio for text anonymization and deanonymization. Presidio is a powerful data protection library that automatically detects and anonymizes personally identifiable information (PII) in text data.

## What is Microsoft Presidio?

Microsoft Presidio is an open-source data protection and de-identification SDK that helps you:
- **Detect** sensitive information in text (PII detection)
- **Anonymize** sensitive data using various techniques
- **Deanonymize** certain types of encrypted data (when possible)

## Setup and Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download SpaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

## Quick Start Example

Run the main demonstration script to see Presidio in action:

```bash
python anonymization_deanonymization.py
```

## How Presidio Works: Step-by-Step Tutorial

### Step 1: Entity Detection (Analysis)

Presidio first analyzes your text to detect sensitive information. Let's see what it finds in a sample text:

**Original Text:**
```
My name is Yordan Arencibia,
my email is yordan.arencibia@gmail.com and 
my phone number is +34 912 345 678. My ID is 12345678Z.
my computer IP is 10.18.1.1 and my credit card is 4111 1111 1111 1111.
I was born on 01/01/1985 and my SSN is 232323.
```

**Detected Entities:**
```
Entity: EMAIL_ADDRESS, Score: 1.00, Start: 58, End: 84, Text: 'yordan.arencibia@gmail.com'
Entity: CREDIT_CARD, Score: 1.00, Start: 212, End: 231, Text: '4111 1111 1111 1111'
Entity: IP_ADDRESS, Score: 0.95, Start: 180, End: 189, Text: '10.18.1.1'
Entity: PERSON, Score: 0.85, Start: 20, End: 36, Text: 'Yordan Arencibia'
Entity: PHONE_NUMBER, Score: 0.75, Start: 117, End: 132, Text: '+34 912 345 678'
Entity: DATE_TIME, Score: 0.60, Start: 255, End: 265, Text: '01/01/1990'
Entity: US_DRIVER_LICENSE, Score: 0.30, Start: 143, End: 152, Text: '12345678Z'
```

### Step 2: Anonymization Process

Presidio applies different anonymization strategies based on entity type:

- **Email addresses**: Replaced with `[HIDDEN_EMAIL]`
- **Phone numbers**: Partially masked (e.g., `+34 91XXXXXXXXX`)
- **Credit cards**: Encrypted (reversible) - `71jWOzL6NWUXXFc-kT4vVXiLgcbo0A6VzW2MTjlEsdMV2o5108McOhV5sJ9ogQLi`
- **Driver licenses**: Replaced with `[HIDDEN_DRIVER_LICENSE]`
- **IP addresses**: Replaced with generic tags `<IP_ADDRESS>`
- **Organizations**: Replaced with `<ORGANIZATION>`
- **Dates**: Replaced with `<DATE_TIME>`

**Anonymized Result:**
```
My name is Yordan Arencibia,
my email is [HIDDEN_EMAIL] and 
my phone number is +34 91XXXXXXXXX. My ID is [HIDDEN_DRIVER_LICENSE].
my computer <ORGANIZATION> is <IP_ADDRESS> and my credit card is 71jWOzL6NWUXXFc-kT4vVXiLgcbo0A6VzW2MTjlEsdMV2o5108McOhV5sJ9ogQLi.
I was born on <DATE_TIME> and my <ORGANIZATION> is <DATE_TIME>.
```

### Step 3: Deanonymization (Limited Cases)

**Important Note:** Deanonymization is only possible for entities that were **encrypted** rather than replaced or masked. In our example, only the credit card was encrypted.

**Deanonymized Result:**
```
My name is Yordan Arencibia,
my email is [HIDDEN_EMAIL] and 
my phone number is +34 91XXXXXXXXX. My ID is [HIDDEN_DRIVER_LICENSE].
my computer <ORGANIZATION> is <IP_ADDRESS> and my credit card is 4111 1111 1111 1111
I was born on <DATE_TIME> and my <ORGANIZATION> is <DATE_TIME>.
```

Notice that only the credit card number was restored to its original value.

## Understanding Anonymization Strategies

### Irreversible Operations (Cannot be deanonymized):
- **Replacement**: `[HIDDEN_EMAIL]`, `[HIDDEN_DRIVER_LICENSE]`
- **Masking**: `+34 91XXXXXXXXX`
- **Generic Tags**: `<ORGANIZATION>`, `<IP_ADDRESS>`, `<DATE_TIME>`

### Reversible Operations (Can be deanonymized):
- **Encryption**: Credit card numbers are encrypted and can be decrypted back to original values

## Project Structure

```
├── anonymization_deanonymization.py  # Main demonstration script
├── config/
│   ├── __init__.py
│   └── config.py                     # Configuration for anonymization rules
├── utils/
│   ├── __init__.py
│   └── anonymizer_utils.py          # Presidio wrapper utilities
├── requirements.txt                  # Python dependencies
└── README.md                        # This tutorial
```

## Key Components

### 1. PresidioAnonymizer Class (`utils/anonymizer_utils.py`)
- Wraps Presidio's analyzer and anonymizer engines
- Provides convenient methods for text processing
- Handles configuration and rule management

### 2. Configuration (`config/config.py`)
- Defines anonymization rules for different entity types
- Specifies NLP engine configuration
- Sets up deanonymization rules for reversible operations

### 3. Main Script (`anonymization_deanonymization.py`)
- Demonstrates the complete workflow
- Shows entity detection, anonymization, and deanonymization
- Provides clear output for understanding each step

## Common Use Cases

1. **Data Privacy Compliance**: Remove PII before storing or sharing data
2. **Development/Testing**: Use anonymized production data safely in development
3. **Analytics**: Perform data analysis while protecting individual privacy
4. **Data Sharing**: Share datasets with partners while maintaining privacy
5. **Audit Trails**: Keep reversible encryption for certain data that may need recovery

## Advanced Features

- **Custom Entity Recognition**: Add your own entity types
- **Multiple Language Support**: Process text in different languages
- **Configurable Rules**: Customize anonymization strategies per entity type
- **Score Thresholds**: Adjust confidence levels for entity detection
- **Batch Processing**: Handle multiple documents efficiently

## Next Steps

To extend this example:
1. Modify `config/config.py` to add custom anonymization rules
2. Add new entity types in the analyzer configuration
3. Implement custom operators for specific anonymization needs
4. Add support for different file formats (PDF, Word, etc.)
5. Integrate with databases or data pipelines

## Resources

- [Microsoft Presidio Documentation](https://microsoft.github.io/presidio/)
- [Presidio GitHub Repository](https://github.com/microsoft/presidio)
- [SpaCy Documentation](https://spacy.io/)