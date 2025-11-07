from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
from config.config import NLP_CONFIGURATION, ANONYMIZATION_RULES, DEANONYMIZATION_RULES, DEFAULT_LANGUAGE

class PresidioAnonymizer:
    def __init__(self, nlp_config=None, anonymization_rules=None):
        """
        Initialize the Presidio Anonymizer with custom or default configuration.
        
        Args:
            nlp_config: NLP configuration dict (optional)
            anonymization_rules: Custom anonymization rules dict (optional)
        """
        self.nlp_config = nlp_config or NLP_CONFIGURATION
        self.anonymization_rules = anonymization_rules or ANONYMIZATION_RULES
        self.deanonymization_rules = DEANONYMIZATION_RULES
        
        # Initialize analyzer
        nlp_engine_provider = NlpEngineProvider(nlp_configuration=self.nlp_config)
        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine_provider.create_engine())
        
        # Initialize anonymizer
        self.anonymizer = AnonymizerEngine()
        self.deanonymizer = DeanonymizeEngine()
    
    def analyze_text(self, text, language=DEFAULT_LANGUAGE, entities=None):
        """
        Analyze text to detect PII entities.
        
        Args:
            text: Text to analyze
            language: Language code (default: 'en')
            entities: List of specific entities to detect (optional)
        
        Returns:
            List of analyzer results
        """
        return self.analyzer.analyze(
            text=text,
            language=language,
            entities=entities
        )
    
    def anonymize_text(self, text, analyzer_results=None, language=DEFAULT_LANGUAGE, entities=None):
        """
        Anonymize text using the configured rules.
        
        Args:
            text: Text to anonymize
            analyzer_results: Pre-computed analyzer results (optional)
            language: Language code (default: 'en')
            entities: List of specific entities to detect (optional)
        
        Returns:
            Anonymized result object
        """
        if analyzer_results is None:
            analyzer_results = self.analyze_text(text, language, entities)
        
        return self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators=self.anonymization_rules
        )
        
    def deanonymize_text(self, text, entities=None):
        """
        Deanonymize text using the configured rules.
        
        Args:
            text: Anonymized text to deanonymize
            entities: List of entities to deanonymize (optional)
        
        Returns:
            Deanonymized result object
        """
        # For deanonymization to work, we need to provide entities that were encrypted
        if entities is None:
            entities = []
            # Try to find encrypted entities in the text based on our configuration
            for entity_type in self.deanonymization_rules.keys():
                if entity_type in text:
                    entities.append(entity_type)
        
        # Create mock entities for deanonymization
        # This is a simplified approach - in a real scenario, you'd store the original entities
        mock_entities = []
        
        return self.deanonymizer.deanonymize(
            text=text,
            entities=mock_entities,
            operators=self.deanonymization_rules
        )
    
    def deanonymize_with_entities(self, anonymized_text, original_entities):
        """
        Deanonymize text using the original analyzer results.
        
        Args:
            anonymized_text: The anonymized text
            original_entities: The original analyzer results from when text was anonymized
        
        Returns:
            Deanonymized result object
        """
        # Filter entities that can be deanonymized (only encrypted ones)
        deanonymizable_entities = []
        
        for entity in original_entities:
            if entity.entity_type in self.deanonymization_rules:
                # We need to create new entities based on the encrypted text positions
                # This is a simplified approach - finding encrypted values in the anonymized text
                if entity.entity_type == "CREDIT_CARD":
                    # Look for encrypted credit card patterns in the anonymized text
                    import re
                    # Look for encrypted patterns (Presidio encrypted values with dots at the end)
                    encrypted_pattern = r'[A-Za-z0-9_-]{50,}\.?'
                    matches = re.finditer(encrypted_pattern, anonymized_text)
                    
                    for match in matches:
                        # Create a new entity for the encrypted value
                        from presidio_analyzer import RecognizerResult
                        encrypted_entity = RecognizerResult(
                            entity_type="CREDIT_CARD",
                            start=match.start(),
                            end=match.end(),
                            score=1.0
                        )
                        deanonymizable_entities.append(encrypted_entity)
        
        if not deanonymizable_entities:
            # Return the original text if no entities can be deanonymized
            from presidio_anonymizer.entities import EngineResult
            return EngineResult(text=anonymized_text)
        
        try:
            return self.deanonymizer.deanonymize(
                text=anonymized_text,
                entities=deanonymizable_entities,
                operators=self.deanonymization_rules
            )
        except Exception as e:
            # If deanonymization fails, return the original text with an error note
            from presidio_anonymizer.entities import EngineResult
            return EngineResult(text=f"{anonymized_text}\n\n[Note: Deanonymization failed: {str(e)}]")

    def process_text(self, text, language=DEFAULT_LANGUAGE, entities=None, show_analysis=False):
        """
        Complete process: analyze and anonymize text in one step.
        
        Args:
            text: Text to process
            language: Language code (default: 'en')
            entities: List of specific entities to detect (optional)
            show_analysis: Whether to return analysis results (default: False)
        
        Returns:
            Tuple of (anonymized_result, analyzer_results) if show_analysis=True
            Otherwise just anonymized_result
        """
        analyzer_results = self.analyze_text(text, language, entities)
        anonymized_result = self.anonymize_text(text, analyzer_results)
        
        if show_analysis:
            return anonymized_result, analyzer_results
        return anonymized_result
