# apps/speech_processing/azure_openai_client.py (Enhanced)
import openai
from django.conf import settings
import json
import logging
from typing import Dict, List, Optional, Any
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class AzureOpenAIClient:
    def __init__(self):
        openai.api_type = "azure"
        openai.api_base = settings.AZURE_OPENAI_ENDPOINT
        openai.api_version = settings.AZURE_OPENAI_API_VERSION
        openai.api_key = settings.AZURE_OPENAI_API_KEY
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME

    def analyze_speech_for_form_filling(self, transcribed_text: str, form_template: Dict) -> Dict:
        """Enhanced analysis for legal form filling with better context understanding"""
        try:
            # Prepare legal context prompt
            prompt = self._create_legal_analysis_prompt(transcribed_text, form_template)
            
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {
                        "role": "system", 
                        "content": self._get_legal_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=1200,
                temperature=0.2,
                top_p=0.95
            )

            result = json.loads(response.choices[0].message.content)
            
            # Post-process and validate the result
            return self._post_process_analysis_result(result, transcribed_text)

        except Exception as e:
            logger.error(f"Azure OpenAI legal analysis failed: {e}")
            return self._get_fallback_analysis_result(transcribed_text)

    def detect_case_type_advanced(self, transcribed_text: str, available_case_types: List[str]) -> Dict:
        """Advanced case type detection using GPT-4"""
        try:
            prompt = f"""
            Analyze the following legal problem statement and classify it into one of the available case types.
            
            Available case types:
            {', '.join(available_case_types)}
            
            User's problem (in Hindi/English mixed): "{transcribed_text}"
            
            Consider:
            1. Legal terminology and context
            2. Nature of the dispute or issue
            3. Parties involved (individuals, businesses, government)
            4. Type of relief sought
            5. Jurisdiction and applicable laws
            
            Respond with JSON in this exact format:
            {{
                "detected_case_type": "most_appropriate_case_type",
                "confidence": 0.85,
                "reasoning": "detailed explanation of why this case type was selected",
                "keywords_found": ["list", "of", "relevant", "keywords"],
                "legal_context": "brief legal context and applicable laws",
                "suggested_questions": ["additional question 1", "additional question 2"],
                "complexity_level": "simple|moderate|complex",
                "estimated_time": "expected time to resolve this type of case"
            }}
            
            If no case type matches well, use "other" and explain in reasoning.
            """
            
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert legal advisor specializing in Indian law and legal procedures. You help citizens understand their legal issues and determine the appropriate legal remedies."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)
            return self._validate_case_type_result(result, available_case_types)

        except Exception as e:
            logger.error(f"Advanced case type detection failed: {e}")
            return {
                "detected_case_type": "other",
                "confidence": 0.1,
                "reasoning": "Could not analyze due to technical error",
                "keywords_found": [],
                "legal_context": "Unable to determine legal context",
                "suggested_questions": [],
                "complexity_level": "moderate",
                "estimated_time": "Unknown"
            }

    def generate_legal_questions(self, case_type: str, initial_context: str) -> List[Dict]:
        """Generate contextual questions based on case type and initial input"""
        try:
            prompt = f"""
            Generate specific, legally relevant questions for a {case_type} case based on this initial context:
            "{initial_context}"
            
            Generate 5-8 questions that:
            1. Are essential for preparing legal documents
            2. Follow Indian legal requirements
            3. Are easy to understand for common citizens
            4. Capture all necessary details for court filing
            5. Are specific to this case type
            
            For each question, provide:
            - The question text (in simple Hindi/English)
            - Field type (text, date, number, address, phone, email, textarea)
            - Whether it's required or optional
            - Validation requirements
            - Help text for the user
            
            Respond with JSON array:
            [
                {{
                    "question": "What is your complete name as per official documents?",
                    "field_name": "applicant_name",
                    "field_type": "text",
                    "is_required": true,
                    "validation_rules": {{"min_length": 2, "max_length": 100}},
                    "help_text": "Enter your name exactly as it appears on your Aadhaar card or other ID",
                    "legal_importance": "Required for legal identification",
                    "hindi_question": "आपका पूरा नाम क्या है जैसा कि आधिकारिक दस्तावेजों में है?"
                }}
            ]
            """
            
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a legal expert who creates comprehensive questionnaires for legal document preparation in India."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.4
            )

            questions = json.loads(response.choices[0].message.content)
            return self._validate_and_enhance_questions(questions, case_type)

        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return self._get_fallback_questions(case_type)

    def analyze_answer_quality(self, question: str, answer: str, field_type: str) -> Dict:
        """Analyze the quality and completeness of an answer"""
        try:
            prompt = f"""
            Evaluate this answer to a legal question:
            
            Question: "{question}"
            Answer: "{answer}"
            Expected field type: {field_type}
            
            Analyze:
            1. Is the answer complete and relevant?
            2. Does it contain the required information?
            3. Are there any obvious errors or inconsistencies?
            4. Is additional clarification needed?
            5. Does it follow the expected format for {field_type}?
            
            Respond with JSON:
            {{
                "quality_score": 0.85,
                "is_complete": true,
                "is_relevant": true,
                "has_errors": false,
                "error_details": [],
                "suggestions": ["suggestion if any improvement needed"],
                "clarification_needed": false,
                "clarification_question": "follow-up question if needed",
                "formatted_answer": "cleaned and formatted version of the answer",
                "confidence": 0.9
            }}
            """
            
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a legal assistant who evaluates the quality and completeness of answers to legal questions."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=600,
                temperature=0.2
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Answer quality analysis failed: {e}")
            return {
                "quality_score": 0.7,
                "is_complete": True,
                "is_relevant": True,
                "has_errors": False,
                "error_details": [],
                "suggestions": [],
                "clarification_needed": False,
                "clarification_question": "",
                "formatted_answer": answer.strip(),
                "confidence": 0.5
            }

    def generate_document_review(self, document_data: Dict, case_type: str) -> Dict:
        """Generate a comprehensive review of the generated document"""
        try:
            prompt = f"""
            Review this {case_type} legal document data for completeness and accuracy:
            
            {json.dumps(document_data, indent=2)}
            
            Evaluate:
            1. Legal completeness - are all required elements present?
            2. Factual consistency - do all facts align?
            3. Legal accuracy - are legal references correct?
            4. Missing information - what critical details are missing?
            5. Potential improvements - how can this be strengthened?
            6. Compliance with Indian legal standards
            
            Provide specific, actionable feedback:
            {{
                "overall_score": 0.85,
                "completeness_score": 0.9,
                "accuracy_score": 0.8,
                "legal_compliance_score": 0.85,
                "missing_critical_info": ["list of missing items"],
                "factual_inconsistencies": ["list of inconsistencies"],
                "legal_suggestions": ["improvement suggestions"],
                "strengths": ["document strengths"],
                "weaknesses": ["areas for improvement"],
                "next_steps": ["recommended actions"],
                "estimated_success_probability": 0.75,
                "additional_documents_needed": ["list of additional docs"],
                "legal_precedents": ["relevant case laws if applicable"]
            }}
            """
            
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a senior legal reviewer with expertise in Indian civil and criminal law, specializing in document review and legal compliance."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Document review failed: {e}")
            return {
                "overall_score": 0.7,
                "completeness_score": 0.7,
                "accuracy_score": 0.7,
                "legal_compliance_score": 0.7,
                "missing_critical_info": [],
                "factual_inconsistencies": [],
                "legal_suggestions": ["Manual review recommended due to technical error"],
                "strengths": [],
                "weaknesses": [],
                "next_steps": ["Consult with a legal professional"],
                "estimated_success_probability": 0.5,
                "additional_documents_needed": [],
                "legal_precedents": []
            }

    def translate_legal_content(self, content: str, source_lang: str, target_lang: str) -> Dict:
        """Translate legal content while preserving legal terminology"""
        try:
            prompt = f"""
            Translate this legal content from {source_lang} to {target_lang}, preserving:
            1. Legal terminology accuracy
            2. Formal legal language style
            3. Important legal concepts
            4. Official document structure
            
            Content: "{content}"
            
            Provide:
            {{
                "translated_content": "translated text",
                "legal_terms_preserved": ["list of legal terms kept in original"],
                "translation_notes": ["important notes about translation choices"],
                "confidence": 0.95
            }}
            """
            
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a legal translator specializing in Indian legal documents and terminology."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.2
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Legal translation failed: {e}")
            return {
                "translated_content": content,
                "legal_terms_preserved": [],
                "translation_notes": ["Translation failed, original content returned"],
                "confidence": 0.1
            }

    # Helper methods
    def _create_legal_analysis_prompt(self, text: str, template: Dict) -> str:
        """Create a comprehensive prompt for legal analysis"""
        template_fields = template.get('fields', [])
        field_descriptions = []
        
        for field in template_fields:
            field_descriptions.append(f"- {field.get('field_name', '')}: {field.get('label', '')} ({field.get('field_type', 'text')})")
        
        prompt = f"""
        Analyze this legal case description and extract relevant information for form filling:
        
        Case Description: "{text}"
        
        Available form fields:
        {chr(10).join(field_descriptions)}
        
        Extract information for each field if available in the description. Consider:
        1. Direct mentions of information
        2. Implied information that can be reasonably inferred
        3. Legal context and standard practices
        4. Regional language variations and common expressions
        
        Also identify:
        - Missing critical information that needs to be asked
        - Potential legal issues or warnings
        - Suggested clarifying questions
        - Confidence level for each extracted field
        
        Respond with comprehensive JSON following the specified format.
        """
        
        return prompt

    def _get_legal_system_prompt(self) -> str:
        """Get the system prompt for legal analysis"""
        return """You are an expert legal assistant specializing in Indian legal procedures and documentation. 
        You help citizens understand their legal issues, extract relevant information from their descriptions, 
        and ensure proper legal document preparation. You are familiar with:
        
        - Indian Civil and Criminal Procedure Codes
        - Consumer Protection Laws
        - Property and Rental Laws
        - Employment and Labor Laws
        - Regional legal variations across Indian states
        - Common legal terminology in Hindi and English
        
        Always prioritize accuracy and legal compliance in your analysis."""

    def _post_process_analysis_result(self, result: Dict, original_text: str) -> Dict:
        """Post-process and validate the analysis result"""
        # Ensure required fields are present
        required_fields = ['extracted_fields', 'confidence_scores', 'missing_information', 'legal_warnings']
        
        for field in required_fields:
            if field not in result:
                result[field] = {} if field in ['extracted_fields', 'confidence_scores'] else []
        
        # Validate confidence scores
        for field, score in result.get('confidence_scores', {}).items():
            if not isinstance(score, (int, float)) or score < 0 or score > 1:
                result['confidence_scores'][field] = 0.5
        
        # Add metadata
        result['analysis_metadata'] = {
            'original_text_length': len(original_text),
            'analysis_timestamp': datetime.now().isoformat(),
            'processing_method': 'azure_openai_gpt4'
        }
        
        return result

    def _get_fallback_analysis_result(self, text: str) -> Dict:
        """Provide fallback analysis when AI fails"""
        return {
            "extracted_fields": {},
            "confidence_scores": {},
            "missing_information": ["Unable to analyze input due to technical error"],
            "clarification_needed": {},
            "legal_warnings": ["Please review all information manually"],
            "analysis_metadata": {
                "fallback_used": True,
                "original_text_length": len(text),
                "analysis_timestamp": datetime.now().isoformat()
            }
        }

    def _validate_case_type_result(self, result: Dict, available_types: List[str]) -> Dict:
        """Validate and ensure case type result is properly formatted"""
        detected_type = result.get('detected_case_type', 'other')
        
        # Check if detected type is in available types
        if detected_type not in available_types and detected_type != 'other':
            result['detected_case_type'] = 'other'
            result['confidence'] = max(0.1, result.get('confidence', 0.5) * 0.5)
            result['reasoning'] += f" (Original detection '{detected_type}' not in available types)"
        
        # Ensure confidence is in valid range
        confidence = result.get('confidence', 0.5)
        result['confidence'] = max(0.0, min(1.0, confidence))
        
        return result

    def _validate_and_enhance_questions(self, questions: List[Dict], case_type: str) -> List[Dict]:
        """Validate and enhance generated questions"""
        validated_questions = []
        
        for i, question in enumerate(questions):
            # Ensure required fields
            validated_question = {
                'question': question.get('question', f'Question {i+1}'),
                'field_name': question.get('field_name', f'field_{i+1}'),
                'field_type': question.get('field_type', 'text'),
                'is_required': question.get('is_required', True),
                'validation_rules': question.get('validation_rules', {}),
                'help_text': question.get('help_text', ''),
                'order': i + 1
            }
            
            # Add Hindi translation if not present
            if 'hindi_question' not in question:
                validated_question['hindi_question'] = self._get_hindi_translation(question.get('question', ''))
            
            validated_questions.append(validated_question)
        
        return validated_questions

    def _get_fallback_questions(self, case_type: str) -> List[Dict]:
        """Provide fallback questions when AI generation fails"""
        basic_questions = [
            {
                'question': 'What is your full name?',
                'field_name': 'applicant_name',
                'field_type': 'text',
                'is_required': True,
                'validation_rules': {'min_length': 2},
                'help_text': 'Enter your complete legal name',
                'order': 1
            },
            {
                'question': 'What is your address?',
                'field_name': 'applicant_address',
                'field_type': 'address',
                'is_required': True,
                'validation_rules': {'min_length': 10},
                'help_text': 'Provide your complete address',
                'order': 2
            },
            {
                'question': 'Please describe your issue in detail.',
                'field_name': 'issue_description',
                'field_type': 'textarea',
                'is_required': True,
                'validation_rules': {'min_length': 20},
                'help_text': 'Explain your legal issue clearly',
                'order': 3
            }
        ]
        
        return basic_questions

    def _get_hindi_translation(self, english_text: str) -> str:
        """Get basic Hindi translation for common legal questions"""
        translations = {
            'What is your full name?': 'आपका पूरा नाम क्या है?',
            'What is your address?': 'आपका पता क्या है?',
            'Please describe your issue in detail.': 'कृपया अपनी समस्या का विस्तार से वर्णन करें।',
            'When did this incident occur?': 'यह घटना कब हुई?',
            'What compensation are you seeking?': 'आप क्या मुआवजा चाहते हैं?'
        }
        
        return translations.get(english_text, english_text)