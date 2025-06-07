




# ============ backend/tests/test_speech_processing.py ============
import pytest
from django.test import TestCase
from unittest.mock import Mock, patch
from apps.speech_processing.bhashini_client import BhashiniClient
from apps.speech_processing.azure_openai_client import AzureOpenAIClient

class SpeechProcessingTestCase(TestCase):
    def setUp(self):
        self.bhashini_client = BhashiniClient()
        self.openai_client = AzureOpenAIClient()

    @patch('apps.speech_processing.bhashini_client.requests.Session.post')
    def test_bhashini_auth_token(self, mock_post):
        """Test BHASHINI authentication token retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'pipelineResponseConfig': [
                {'config': [{'serviceId': 'test-service', 'inferenceEndPoint': {'callbackUrl': 'test-url'}}]}
            ]
        }
        mock_post.return_value = mock_response
        
        result = self.bhashini_client.get_auth_token()
        self.assertIn('pipelineResponseConfig', result)

    @patch('openai.ChatCompletion.create')
    def test_azure_openai_analysis(self, mock_create):
        """Test Azure OpenAI document analysis"""
        mock_create.return_value.choices = [
            Mock(message=Mock(content='{"extracted_fields": {}, "confidence_scores": {}}'))
        ]
        
        result = self.openai_client.analyze_speech_for_form_filling(
            "Test speech", 
            {"fields": []}
        )
        self.assertIn('extracted_fields', result)