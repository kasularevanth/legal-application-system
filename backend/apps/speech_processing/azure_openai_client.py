







# ============ apps/speech_processing/azure_openai_client.py ============
import openai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class AzureOpenAIClient:
    def __init__(self):
        openai.api_type = "azure"
        openai.api_base = settings.AZURE_OPENAI_ENDPOINT
        openai.api_version = settings.AZURE_OPENAI_API_VERSION
        openai.api_key = settings.AZURE_OPENAI_API_KEY
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME

    def analyze_speech_for_form_filling(self, transcribed_text, form_template):
        """Analyze transcribed speech and extract form field values"""
        try:
            prompt = f"""
            You are an AI assistant helping users fill legal forms using speech recognition.
            
            Form Template: {json.dumps(form_template, indent=2)}
            
            User's Speech (transcribed): "{transcribed_text}"
            
            Please analyze the speech and extract relevant information for the form fields.
            Return a JSON response with the following structure:
            {{
                "extracted_fields": {{
                    "field_name": "extracted_value",
                    ...
                }},
                "confidence_scores": {{
                    "field_name": 0.95,
                    ...
                }},
                "missing_information": ["list", "of", "missing", "required", "fields"],
                "clarification_needed": {{
                    "field_name": "question to ask user for clarification"
                }},
                "legal_warnings": ["any legal warnings or important notices"]
            }}
            
            Consider:
            1. Legal terminology and its proper interpretation
            2. Date formats and legal date requirements
            3. Names, addresses, and contact information
            4. Legal relationships (plaintiff, defendant, etc.)
            5. Monetary amounts and their proper formatting
            6. Regional language nuances if applicable
            """

            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a legal document assistant specializing in Indian legal forms and procedures."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"Azure OpenAI analysis failed: {e}")
            raise

    def generate_legal_suggestions(self, form_type, user_input):
        """Generate legal suggestions and guidance"""
        try:
            prompt = f"""
            Provide legal guidance for a {form_type} based on user input: "{user_input}"
            
            Please provide:
            1. Relevant legal provisions or sections
            2. Required documents or evidence
            3. Procedural requirements
            4. Common mistakes to avoid
            5. Timeline considerations
            
            Keep the response practical and user-friendly while being legally accurate.
            Focus on Indian legal system and procedures.
            """

            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a legal advisor specialized in Indian law and court procedures."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.4
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Legal suggestion generation failed: {e}")
            raise

    def validate_legal_document(self, document_content, document_type):
        """Validate legal document for completeness and accuracy"""
        try:
            prompt = f"""
            Please review this {document_type} for legal completeness and accuracy:
            
            {document_content}
            
            Provide analysis on:
            1. Missing required information
            2. Formatting issues
            3. Legal terminology accuracy
            4. Compliance with Indian legal standards
            5. Suggestions for improvement
            
            Return a structured response with validation results.
            """

            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a legal document reviewer with expertise in Indian legal procedures."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Document validation failed: {e}")
            raise