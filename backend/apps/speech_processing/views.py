# apps/speech_processing/views.py (Enhanced)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tempfile
import os
import json
from .bhashini_client import BhashiniClient
from .azure_openai_client import AzureOpenAIClient
from apps.legal_forms.models import LegalCase, CaseTypeMapping
from apps.legal_forms.services.case_processor import CaseProcessor
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def speech_to_text_legal(request):
    """Enhanced speech to text specifically for legal case processing"""
    try:
        audio_file = request.FILES.get('audio')
        source_language = request.data.get('language', 'hi')
        case_id = request.data.get('case_id')  # Optional: for context-aware processing
        
        if not audio_file:
            return Response(
                {'error': 'Audio file is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Use BHASHINI for speech recognition
            bhashini_client = BhashiniClient()
            result = bhashini_client.speech_to_text(temp_file_path, source_language)
            
            transcribed_text = result['text']
            confidence = result['confidence']
            
            # Enhanced processing for legal context
            enhanced_result = {
                'success': True,
                'transcription': transcribed_text,
                'confidence': confidence,
                'language': result['language'],
                'word_count': len(transcribed_text.split()),
                'processing_metadata': {
                    'audio_duration_estimate': _estimate_audio_duration(temp_file_path),
                    'language_detected': source_language,
                    'bhashini_service_used': True
                }
            }
            
            # If case_id provided, add legal context analysis
            if case_id:
                try:
                    case = LegalCase.objects.get(case_id=case_id, user=request.user)
                    legal_analysis = _analyze_legal_context(transcribed_text, case)
                    enhanced_result['legal_analysis'] = legal_analysis
                except LegalCase.DoesNotExist:
                    pass
            
            # Detect potential legal keywords
            legal_keywords = _detect_legal_keywords(transcribed_text)
            if legal_keywords:
                enhanced_result['detected_legal_keywords'] = legal_keywords
                enhanced_result['suggested_case_types'] = _suggest_case_types(legal_keywords)
            
            return Response(enhanced_result)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"Enhanced speech to text conversion failed: {e}")
        return Response(
            {'error': 'Speech recognition failed', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_voice_legal_input(request):
    """Process voice input directly for legal case creation"""
    try:
        audio_file = request.FILES.get('audio')
        source_language = request.data.get('language', 'hi')
        
        if not audio_file:
            return Response(
                {'error': 'Audio file is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convert speech to text
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Speech recognition
            bhashini_client = BhashiniClient()
            speech_result = bhashini_client.speech_to_text(temp_file_path, source_language)
            transcribed_text = speech_result['text']
            
            # Process as legal case input
            case_processor = CaseProcessor()
            case = case_processor.process_initial_input(
                user=request.user,
                input_text=transcribed_text,
                mode='voice',
                language=source_language
            )
            
            # Prepare comprehensive response
            response_data = {
                'success': True,
                'transcription': transcribed_text,
                'speech_confidence': speech_result['confidence'],
                'case_id': str(case.case_id),
                'case_status': case.status,
                'requires_questions': len(case.questions_asked) > 0
            }

            if case.detected_case_type:
                response_data.update({
                    'case_type': case.detected_case_type.case_type,
                    'detection_confidence': case.detection_confidence,
                    'detected_keywords': case.detected_keywords,
                    'questions': case.questions_asked,
                    'next_question': case.get_current_question()
                })
                
                # Generate voice prompt for first question if needed
                if case.questions_asked:
                    voice_prompt = _generate_voice_prompt(case.get_current_question(), source_language)
                    response_data['voice_prompt'] = voice_prompt
            else:
                response_data.update({
                    'error': case.error_details or 'Could not determine case type',
                    'suggestions': _get_voice_suggestions(source_language)
                })

            return Response(response_data)
            
        finally:
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"Voice legal input processing failed: {e}")
        return Response(
            {'error': 'Failed to process voice input', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def answer_question_by_voice(request):
    """Answer a legal case question using voice input"""
    try:
        audio_file = request.FILES.get('audio')
        case_id = request.data.get('case_id')
        source_language = request.data.get('language', 'hi')
        
        if not audio_file or not case_id:
            return Response(
                {'error': 'Audio file and case_id are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get case
        try:
            case = LegalCase.objects.get(case_id=case_id, user=request.user)
        except LegalCase.DoesNotExist:
            return Response(
                {'error': 'Case not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Convert speech to text
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Speech recognition
            bhashini_client = BhashiniClient()
            speech_result = bhashini_client.speech_to_text(temp_file_path, source_language)
            answer_text = speech_result['text']
            
            # Validate answer based on question context
            current_question = case.get_current_question()
            validated_answer = _validate_voice_answer(current_question, answer_text, case)
            
            # Submit answer
            case_processor = CaseProcessor()
            success = case_processor.submit_answer(case, validated_answer, 'voice')
            
            if not success:
                return Response(
                    {'error': 'Failed to submit answer'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Prepare response
            response_data = {
                'success': True,
                'transcribed_answer': answer_text,
                'validated_answer': validated_answer,
                'speech_confidence': speech_result['confidence'],
                'question_answered': current_question,
                'questioning_complete': case.is_questioning_complete()
            }

            # Get next question if available
            if not case.is_questioning_complete():
                next_question = case.get_current_question()
                response_data['next_question'] = next_question
                
                # Generate voice prompt for next question
                voice_prompt = _generate_voice_prompt(next_question, source_language)
                response_data['voice_prompt'] = voice_prompt
            else:
                # All questions answered
                response_data['ready_for_generation'] = True
                completion_message = _generate_completion_message(source_language)
                response_data['completion_message'] = completion_message

            return Response(response_data)
            
        finally:
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"Voice answer processing failed: {e}")
        return Response(
            {'error': 'Failed to process voice answer', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_voice_guidance(request):
    """Generate voice guidance for legal processes"""
    try:
        text = request.data.get('text')
        target_language = request.data.get('language', 'hi')
        guidance_type = request.data.get('type', 'general')  # general, question, instruction
        
        if not text:
            return Response(
                {'error': 'Text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Enhance text based on guidance type
        enhanced_text = _enhance_guidance_text(text, guidance_type, target_language)
        
        # Convert to speech using BHASHINI
        bhashini_client = BhashiniClient()
        audio_data = bhashini_client.text_to_speech(enhanced_text, target_language)
        
        # Save audio file
        file_name = f"guidance_{request.user.id}_{target_language}_{guidance_type}.wav"
        file_path = default_storage.save(file_name, ContentFile(audio_data))
        
        return Response({
            'success': True,
            'audio_url': default_storage.url(file_path),
            'text': enhanced_text,
            'language': target_language,
            'guidance_type': guidance_type
        })
        
    except Exception as e:
        logger.error(f"Voice guidance generation failed: {e}")
        return Response(
            {'error': 'Voice guidance generation failed', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Helper functions

def _estimate_audio_duration(file_path):
    """Estimate audio duration from file size"""
    try:
        file_size = os.path.getsize(file_path)
        # Rough estimate: 16kHz, 16-bit mono WAV ≈ 32KB per second
        estimated_duration = file_size / 32000
        return round(estimated_duration, 2)
    except:
        return 0.0

def _analyze_legal_context(text, case):
    """Analyze text in the context of the legal case"""
    analysis = {
        'relevance_score': 0.0,
        'confidence_boost': 0.0,
        'context_keywords': []
    }
    
    if case.detected_case_type:
        case_keywords = case.detected_case_type.keywords
        text_lower = text.lower()
        
        # Check for case-type specific keywords
        matching_keywords = [kw for kw in case_keywords if kw.lower() in text_lower]
        
        if matching_keywords:
            analysis['confidence_boost'] = min(0.2, len(matching_keywords) * 0.05)
            analysis['context_keywords'] = matching_keywords
            analysis['relevance_score'] = len(matching_keywords) / len(case_keywords)
    
    return analysis

def _detect_legal_keywords(text):
    """Detect legal keywords in text"""
    legal_keywords = [
        'complaint', 'petition', 'case', 'court', 'legal', 'law', 'judge', 'lawyer',
        'damage', 'injury', 'accident', 'contract', 'agreement', 'breach', 'violation',
        'property', 'rent', 'tenant', 'landlord', 'money', 'payment', 'compensation',
        # Add Hindi/regional language keywords
        'शिकायत', 'न्यायालय', 'कानून', 'न्यायाधीश', 'वकील', 'नुकसान', 'चोट', 'दुर्घटना',
        'अनुबंध', 'समझौता', 'उल्लंघन', 'संपत्ति', 'किराया', 'किरायेदार', 'मकान मालिक',
    ]
    
    text_lower = text.lower()
    detected = [kw for kw in legal_keywords if kw in text_lower]
    return detected

def _suggest_case_types(keywords):
    """Suggest case types based on detected keywords"""
    suggestions = []
    
    # Simple keyword-based suggestions
    keyword_mappings = {
        'property': ['Property Damage', 'Property Dispute'],
        'rent': ['Rental Issues', 'Tenant Rights'],
        'contract': ['Contract Dispute', 'Breach of Contract'],
        'accident': ['Personal Injury', 'Accident Claim'],
        'money': ['Money Recovery', 'Payment Dispute']
    }
    
    for keyword in keywords:
        if keyword.lower() in keyword_mappings:
            suggestions.extend(keyword_mappings[keyword.lower()])
    
    return list(set(suggestions))

def _generate_voice_prompt(question, language):
    """Generate voice prompt for a question"""
    prompts = {
        'hi': f"कृपया निम्नलिखित प्रश्न का उत्तर दें: {question}",
        'en': f"Please answer the following question: {question}",
        'te': f"దయచేసి ఈ ప్రశ్నకు సమాధానం ఇవ్వండి: {question}",
        'ta': f"தயவுசெய்து பின்வரும் கேள்விக்கு பதிலளிக்கவும்: {question}",
    }
    
    return prompts.get(language, prompts['en'])

def _get_voice_suggestions(language):
    """Get voice suggestions for unclear input"""
    suggestions = {
        'hi': [
            "कृपया अपनी समस्या को स्पष्ट रूप से बताएं",
            "आप किस प्रकार की कानूनी सहायता चाहते हैं?",
            "क्या यह संपत्ति, किराया, या अनुबंध से संबंधित है?"
        ],
        'en': [
            "Please describe your problem clearly",
            "What type of legal help do you need?",
            "Is this related to property, rent, or contract?"
        ]
    }
    
    return suggestions.get(language, suggestions['en'])

def _validate_voice_answer(question, answer, case):
    """Validate voice answer for a specific question"""
    # Basic validation - can be enhanced based on question type
    answer = answer.strip()
    
    # Check for common voice recognition errors
    if len(answer) < 2:
        raise ValueError("Answer too short, please speak more clearly")
    
    # Enhanced validation based on question context could be added here
    
    return answer

def _enhance_guidance_text(text, guidance_type, language):
    """Enhance guidance text based on type and language"""
    prefixes = {
        'question': {
            'hi': "प्रश्न: ",
            'en': "Question: ",
        },
        'instruction': {
            'hi': "निर्देश: ",
            'en': "Instruction: ",
        },
        'general': {
            'hi': "",
            'en': "",
        }
    }
    
    prefix = prefixes.get(guidance_type, {}).get(language, "")
    return prefix + text

def _generate_completion_message(language):
    """Generate completion message"""
    messages = {
        'hi': "सभी प्रश्न पूरे हो गए हैं। अब आपका दस्तावेज़ तैयार किया जा रहा है।",
        'en': "All questions completed. Your document is now being prepared.",
        'te': "అన్ని ప్రశ్నలు పూర్తయ్యాయి. మీ పత్రం ఇప్పుడు తయారు చేయబడుతోంది.",
    }
    
    return messages.get(language, messages['en'])