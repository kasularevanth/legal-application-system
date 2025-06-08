
# ============ backend/tests/test_voice_processing.py (Enhanced) ============
import pytest
from django.test import TestCase, override_settings
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.speech_processing.views import speech_to_text, analyze_speech_for_form
from apps.speech_processing.bhashini_client import BhashiniClient
from apps.speech_processing.azure_openai_client import EnhancedAzureOpenAIClient
from apps.legal_cases.models import LegalCase
import tempfile
import json

User = get_user_model()

@override_settings(USE_MOCK_APIS=True)
class VoiceProcessingTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            preferred_language='hi'
        )
        self.client.force_authenticate(user=self.user)

    @patch('apps.speech_processing.views.BhashiniClient')
    def test_speech_to_text_success(self, mock_bhashini):
        """Test successful speech to text conversion"""
        # Mock BHASHINI response
        mock_instance = Mock()
        mock_instance.speech_to_text.return_value = {
            'text': 'मैं एक कानूनी मुद्दे के बारे में बात करना चाहता हूं',
            'confidence': 0.95,
            'language': 'hi'
        }
        mock_bhashini.return_value = mock_instance

        # Create a temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio.write(b'fake audio data')
            temp_audio.seek(0)

            with open(temp_audio.name, 'rb') as audio_file:
                response = self.client.post('/api/speech/speech-to-text/', {
                    'audio': audio_file,
                    'language': 'hi'
                })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('transcription', response.data)
        self.assertEqual(response.data['transcription'], 'मैं एक कानूनी मुद्दे के बारे में बात करना चाहता हूं')

    @patch('apps.speech_processing.views.EnhancedAzureOpenAIClient')
    def test_voice_legal_analysis(self, mock_openai):
        """Test voice legal case analysis"""
        # Mock OpenAI response
        mock_instance = Mock()
        mock_instance.analyze_voice_for_legal_case.return_value = {
            'case_analysis': {
                'primary_case_type': 'civil',
                'confidence_score': 0.85,
                'legal_complexity': 'medium'
            },
            'extracted_information': {
                'key_facts': ['Property dispute', 'Neighbor conflict']
            }
        }
        mock_openai.return_value = mock_instance

        response = self.client.post('/api/voice-legal/process-voice/', {
            'transcribed_text': 'My neighbor has encroached on my property',
            'user_context': json.dumps({'location': 'Delhi'})
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('analysis', response.data)
        self.assertEqual(response.data['analysis']['case_analysis']['primary_case_type'], 'civil')

    def test_case_creation_from_voice(self):
        """Test creating legal case from voice input"""
        # This would test the full workflow from voice to case creation
        with patch('apps.speech_processing.views.BhashiniClient') as mock_bhashini, \
             patch('apps.speech_processing.views.EnhancedAzureOpenAIClient') as mock_openai:

            # Setup mocks
            mock_bhashini_instance = Mock()
            mock_bhashini_instance.speech_to_text.return_value = {
                'text': 'Property dispute with neighbor',
                'confidence': 0.9,
                'language': 'en'
            }
            mock_bhashini.return_value = mock_bhashini_instance

            mock_openai_instance = Mock()
            mock_openai_instance.analyze_voice_for_legal_case.return_value = {
                'case_analysis': {
                    'primary_case_type': 'property',
                    'confidence_score': 0.88
                }
            }
            mock_openai.return_value = mock_openai_instance

            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(b'fake audio data')

                with open(temp_audio.name, 'rb') as audio_file:
                    response = self.client.post('/api/voice-legal/process-voice-for-case/', {
                        'audio': audio_file,
                        'language': 'en'
                    })

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn('case_id', response.data)

            # Verify case was created
            case = LegalCase.objects.get(case_id=response.data['case_id'])
            self.assertEqual(case.user, self.user)
            self.assertEqual(case.case_type, 'property')

class BhashiniClientTestCase(TestCase):
    def setUp(self):
        self.client = BhashiniClient()

    @patch('apps.speech_processing.bhashini_client.requests.Session.post')
    def test_get_auth_token(self, mock_post):
        """Test BHASHINI authentication"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelineResponseConfig': [
                {
                    'config': [
                        {
                            'serviceId': 'test-service',
                            'inferenceEndPoint': {
                                'callbackUrl': 'https://test-inference.com'
                            }
                        }
                    ]
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client.get_auth_token()
        self.assertIn('pipelineResponseConfig', result)

    @patch('apps.speech_processing.bhashini_client.BhashiniClient.get_auth_token')
    @patch('apps.speech_processing.bhashini_client.requests.Session.post')
    def test_speech_to_text(self, mock_post, mock_auth):
        """Test speech to text conversion"""
        # Mock auth response
        mock_auth.return_value = {
            'pipelineResponseConfig': [
                {
                    'config': [
                        {
                            'serviceId': 'test-asr-service',
                            'inferenceEndPoint': {
                                'callbackUrl': 'https://test-asr.com'
                            }
                        }
                    ]
                }
            ]
        }

        # Mock inference response
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelineResponse': [
                {
                    'output': [
                        {
                            'source': 'Test transcription',
                            'confidence': 0.95
                        }
                    ]
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client.speech_to_text(b'fake audio data', 'hi')
        self.assertEqual(result['text'], 'Test transcription')
        self.assertEqual(result['confidence'], 0.95)