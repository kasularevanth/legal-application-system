# apps/legal_forms/services/case_processor.py
import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.utils import timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from ..models import CaseTypeMapping, QuestionMapping, LegalCase, CaseProcessingLog
from apps.speech_processing.bhashini_client import BhashiniClient
from apps.speech_processing.azure_openai_client import AzureOpenAIClient

logger = logging.getLogger(__name__)

class CaseTypeDetector:
    """Detect case type from user input using keyword matching and AI"""
    
    def __init__(self):
        self.bhashini_client = BhashiniClient()
        self.openai_client = AzureOpenAIClient()
        self.vectorizer = None
        self.case_type_vectors = None
        self.case_types = []
        self._initialize_models()

    def _initialize_models(self):
        """Initialize ML models for case type detection"""
        try:
            # Get all active case type mappings
            mappings = CaseTypeMapping.objects.filter(is_active=True).order_by('-priority')
            
            if not mappings.exists():
                logger.warning("No case type mappings found")
                return

            # Prepare training data
            documents = []
            self.case_types = []
            
            for mapping in mappings:
                # Combine keywords into a document
                keywords_text = ' '.join(mapping.keywords)
                documents.append(keywords_text)
                self.case_types.append(mapping)

            # Create TF-IDF vectors
            self.vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=1000
            )
            
            if documents:
                self.case_type_vectors = self.vectorizer.fit_transform(documents)
                logger.info(f"Initialized case type detector with {len(documents)} case types")

        except Exception as e:
            logger.error(f"Failed to initialize case type detector: {e}")

    def detect_case_type(self, input_text: str, language: str = 'hi') -> Tuple[Optional[CaseTypeMapping], float, List[str]]:
        """
        Detect case type from input text
        Returns: (detected_case_type, confidence, detected_keywords)
        """
        try:
            # Translate to English if needed for better processing
            processed_text = self._preprocess_text(input_text, language)
            
            # Method 1: Keyword-based detection
            keyword_result = self._detect_by_keywords(processed_text)
            
            # Method 2: ML-based detection
            ml_result = self._detect_by_similarity(processed_text)
            
            # Method 3: AI-based detection
            ai_result = self._detect_by_ai(processed_text)
            
            # Combine results and select best match
            final_result = self._combine_detection_results(
                keyword_result, ml_result, ai_result
            )
            
            return final_result

        except Exception as e:
            logger.error(f"Case type detection failed: {e}")
            return None, 0.0, []

    def _preprocess_text(self, text: str, language: str) -> str:
        """Preprocess and translate text if needed"""
        try:
            # Clean text
            text = re.sub(r'[^\w\s]', ' ', text.lower())
            text = ' '.join(text.split())  # Remove extra whitespace
            
            # Translate to English if not already
            if language != 'en':
                try:
                    translation_result = self.bhashini_client.translate_text(
                        text, language, 'en'
                    )
                    translated_text = translation_result.get('translated_text', text)
                    return translated_text
                except Exception as e:
                    logger.warning(f"Translation failed, using original text: {e}")
                    return text
            
            return text

        except Exception as e:
            logger.error(f"Text preprocessing failed: {e}")
            return text

    def _detect_by_keywords(self, text: str) -> Tuple[Optional[CaseTypeMapping], float, List[str]]:
        """Detect case type using keyword matching"""
        best_match = None
        best_score = 0.0
        matched_keywords = []

        try:
            for case_type in CaseTypeMapping.objects.filter(is_active=True):
                score = 0.0
                current_keywords = []
                
                for keyword in case_type.keywords:
                    if keyword.lower() in text.lower():
                        score += 1.0
                        current_keywords.append(keyword)
                
                # Normalize score by number of keywords
                if case_type.keywords:
                    score = score / len(case_type.keywords)
                
                if score > best_score and score >= case_type.confidence_threshold:
                    best_match = case_type
                    best_score = score
                    matched_keywords = current_keywords

        except Exception as e:
            logger.error(f"Keyword detection failed: {e}")

        return best_match, best_score, matched_keywords

    def _detect_by_similarity(self, text: str) -> Tuple[Optional[CaseTypeMapping], float]:
        """Detect case type using TF-IDF similarity"""
        if not self.vectorizer or self.case_type_vectors is None:
            return None, 0.0

        try:
            # Vectorize input text
            input_vector = self.vectorizer.transform([text])
            
            # Calculate similarities
            similarities = cosine_similarity(input_vector, self.case_type_vectors)[0]
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            
            if best_score > 0.3:  # Minimum similarity threshold
                return self.case_types[best_idx], best_score
            
        except Exception as e:
            logger.error(f"Similarity detection failed: {e}")

        return None, 0.0

    def _detect_by_ai(self, text: str) -> Tuple[Optional[str], float]:
        """Detect case type using AI/OpenAI"""
        try:
            # Get available case types
            case_types = [ct.case_type for ct in CaseTypeMapping.objects.filter(is_active=True)]
            
            prompt = f"""
            Analyze the following legal case description and classify it into one of these categories:
            {', '.join(case_types)}
            
            Case description: "{text}"
            
            Respond with JSON in this format:
            {{
                "case_type": "most_likely_case_type",
                "confidence": 0.85,
                "reasoning": "brief explanation"
            }}
            
            If none of the categories fit well, use "other" as the case_type.
            """
            
            result = self.openai_client.analyze_text(prompt)
            
            if result and 'case_type' in result:
                case_type_name = result['case_type']
                confidence = result.get('confidence', 0.0)
                
                # Find matching case type
                try:
                    case_type = CaseTypeMapping.objects.get(
                        case_type__iexact=case_type_name,
                        is_active=True
                    )
                    return case_type, confidence
                except CaseTypeMapping.DoesNotExist:
                    pass

        except Exception as e:
            logger.error(f"AI detection failed: {e}")

        return None, 0.0

    def _combine_detection_results(self, keyword_result, ml_result, ai_result) -> Tuple[Optional[CaseTypeMapping], float, List[str]]:
        """Combine results from different detection methods"""
        results = []
        
        # Add keyword result
        if keyword_result[0]:
            results.append({
                'case_type': keyword_result[0],
                'confidence': keyword_result[1] * 0.4,  # Weight: 40%
                'keywords': keyword_result[2],
                'method': 'keyword'
            })
        
        # Add ML result
        if ml_result[0]:
            results.append({
                'case_type': ml_result[0],
                'confidence': ml_result[1] * 0.3,  # Weight: 30%
                'keywords': [],
                'method': 'similarity'
            })
        
        # Add AI result
        if ai_result[0]:
            results.append({
                'case_type': ai_result[0],
                'confidence': ai_result[1] * 0.3,  # Weight: 30%
                'keywords': [],
                'method': 'ai'
            })
        
        if not results:
            return None, 0.0, []
        
        # Select result with highest weighted confidence
        best_result = max(results, key=lambda x: x['confidence'])
        
        # Combine keywords from all methods
        all_keywords = []
        for result in results:
            if result['case_type'] == best_result['case_type']:
                all_keywords.extend(result['keywords'])
        
        return best_result['case_type'], best_result['confidence'], list(set(all_keywords))


class CaseProcessor:
    """Main service for processing legal cases"""
    
    def __init__(self):
        self.detector = CaseTypeDetector()
        self.bhashini_client = BhashiniClient()
        self.openai_client = AzureOpenAIClient()

    def process_initial_input(self, user, input_text: str, mode: str, language: str = 'hi') -> LegalCase:
        """Process initial user input and detect case type"""
        
        # Create new case
        case = LegalCase.objects.create(
            user=user,
            initial_input=input_text,
            input_mode=mode,
            input_language=language,
            status='input_received'
        )
        
        try:
            case.add_processing_step("Input received")
            
            # Detect case type
            case_type, confidence, keywords = self.detector.detect_case_type(input_text, language)
            
            if case_type:
                case.detected_case_type = case_type
                case.detection_confidence = confidence
                case.detected_keywords = keywords
                case.status = 'case_type_detected'
                
                # Get questions for this case type
                questions = QuestionMapping.objects.filter(
                    case_type_mapping=case_type
                ).order_by('order')
                
                case.questions_asked = [q.question for q in questions]
                case.status = 'gathering_info' if questions.exists() else 'generating_document'
                
                case.add_processing_step(f"Case type detected: {case_type.case_type}")
                
            else:
                case.status = 'error'
                case.error_details = "Could not determine case type from input"
                case.add_processing_step("Case type detection failed")
            
            case.save()
            
            self._log_processing_step(case, "process_initial_input", "completed")
            
        except Exception as e:
            logger.error(f"Failed to process initial input: {e}")
            case.status = 'error'
            case.error_details = str(e)
            case.save()
            self._log_processing_step(case, "process_initial_input", "failed", str(e))
        
        return case

    def submit_answer(self, case: LegalCase, answer: str, mode: str) -> bool:
        """Submit answer to current question"""
        try:
            current_question = case.get_current_question()
            if not current_question:
                return False
            
            # Validate and clean answer
            cleaned_answer = self._validate_answer(case, current_question, answer)
            
            # Submit answer
            case.submit_answer(cleaned_answer)
            
            self._log_processing_step(case, "submit_answer", "completed", {
                'question': current_question,
                'answer': cleaned_answer,
                'mode': mode
            })
            
            # Check if questioning is complete
            if case.is_questioning_complete():
                case.status = 'generating_document'
                case.save()
                case.add_processing_step("All questions answered")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit answer: {e}")
            self._log_processing_step(case, "submit_answer", "failed", str(e))
            return False

    def _validate_answer(self, case: LegalCase, question: str, answer: str) -> str:
        """Validate and clean answer based on question type"""
        try:
            # Find question mapping for validation rules
            question_mapping = QuestionMapping.objects.filter(
                case_type_mapping=case.detected_case_type,
                question=question
            ).first()
            
            if not question_mapping:
                return answer.strip()
            
            # Apply field-specific validation
            if question_mapping.field_type == 'date':
                # Parse and format date
                return self._parse_date(answer)
            elif question_mapping.field_type == 'phone':
                # Clean phone number
                return self._clean_phone(answer)
            elif question_mapping.field_type == 'email':
                # Validate email
                return self._validate_email(answer)
            else:
                return answer.strip()
                
        except Exception as e:
            logger.warning(f"Answer validation failed: {e}")
            return answer.strip()

    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats"""
        # Implementation for date parsing
        return date_str.strip()

    def _clean_phone(self, phone_str: str) -> str:
        """Clean and format phone number"""
        # Remove non-digits
        phone = re.sub(r'[^\d+]', '', phone_str)
        return phone

    def _validate_email(self, email_str: str) -> str:
        """Validate email format"""
        email = email_str.strip().lower()
        if '@' in email and '.' in email:
            return email
        raise ValueError("Invalid email format")

    def _log_processing_step(self, case: LegalCase, step: str, status: str, details=None, processing_time=None):
        """Log processing step for debugging"""
        try:
            CaseProcessingLog.objects.create(
                case=case,
                step=step,
                status=status,
                details=details or {},
                processing_time_ms=processing_time,
                error_message=details if status == 'failed' else ''
            )
        except Exception as e:
            logger.error(f"Failed to log processing step: {e}")

    def get_case_status(self, case_id: str) -> Dict:
        """Get current status of a case"""
        try:
            case = LegalCase.objects.get(case_id=case_id)
            return {
                'case_id': str(case.case_id),
                'status': case.status,
                'progress': self._calculate_progress(case),
                'current_step': case.processing_steps[-1] if case.processing_steps else None,
                'questions_total': len(case.questions_asked),
                'questions_answered': case.current_question_index,
                'case_type': case.detected_case_type.case_type if case.detected_case_type else None,
                'confidence': case.detection_confidence
            }
        except LegalCase.DoesNotExist:
            return {'error': 'Case not found'}

    def _calculate_progress(self, case: LegalCase) -> float:
        """Calculate case completion progress (0-100)"""
        if case.status == 'completed':
            return 100.0
        elif case.status == 'error':
            return 0.0
        elif case.status == 'input_received':
            return 10.0
        elif case.status == 'case_type_detected':
            return 25.0
        elif case.status == 'gathering_info':
            if case.questions_asked:
                question_progress = (case.current_question_index / len(case.questions_asked)) * 50
                return 25.0 + question_progress
            return 50.0
        elif case.status == 'generating_document':
            return 80.0
        elif case.status == 'document_ready':
            return 95.0
        
        return 0.0