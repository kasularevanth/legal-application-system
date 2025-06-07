

# ============ apps/speech_processing/views.py ============
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tempfile
import os
from .bhashini_client import BhashiniClient
from .azure_openai_client import AzureOpenAIClient
from apps.legal_forms.models import FormTemplate
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def speech_to_text(request):
    """Convert speech audio to text"""
    try:
        audio_file = request.FILES.get('audio')
        source_language = request.data.get('language', 'hi')
        
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
            
            return Response({
                'success': True,
                'transcription': result['text'],
                'confidence': result['confidence'],
                'language': result['language']
            })
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"Speech to text conversion failed: {e}")
        return Response(
            {'error': 'Speech recognition failed', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def text_to_speech(request):
    """Convert text to speech audio"""
    try:
        text = request.data.get('text')
        target_language = request.data.get('language', 'hi')
        
        if not text:
            return Response(
                {'error': 'Text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use BHASHINI for text to speech
        bhashini_client = BhashiniClient()
        audio_data = bhashini_client.text_to_speech(text, target_language)
        
        # Save audio file
        file_name = f"tts_output_{request.user.id}_{target_language}.wav"
        file_path = default_storage.save(file_name, ContentFile(audio_data))
        
        return Response({
            'success': True,
            'audio_url': default_storage.url(file_path),
            'language': target_language
        })
        
    except Exception as e:
        logger.error(f"Text to speech conversion failed: {e}")
        return Response(
            {'error': 'Text to speech conversion failed', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_speech_for_form(request):
    """Analyze speech and extract form field values"""
    try:
        transcribed_text = request.data.get('transcribed_text')
        template_id = request.data.get('template_id')
        
        if not transcribed_text or not template_id:
            return Response(
                {'error': 'Transcribed text and template ID are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get form template
        try:
            template = FormTemplate.objects.get(id=template_id)
        except FormTemplate.DoesNotExist:
            return Response(
                {'error': 'Form template not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Use Azure OpenAI for analysis
        openai_client = AzureOpenAIClient()
        analysis_result = openai_client.analyze_speech_for_form_filling(
            transcribed_text, 
            template.template_json
        )
        
        return Response({
            'success': True,
            'analysis': analysis_result
        })
        
    except Exception as e:
        logger.error(f"Speech analysis failed: {e}")
        return Response(
            {'error': 'Speech analysis failed', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def translate_text(request):
    """Translate text between languages"""
    try:
        text = request.data.get('text')
        source_language = request.data.get('source_language', 'en')
        target_language = request.data.get('target_language', 'hi')
        
        if not text:
            return Response(
                {'error': 'Text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use BHASHINI for translation
        bhashini_client = BhashiniClient()
        translation_result = bhashini_client.translate_text(
            text, source_language, target_language
        )
        
        return Response({
            'success': True,
            'translation': translation_result
        })
        
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return Response(
            {'error': 'Translation failed', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
