# ============ apps/speech_processing/bhashini_client.py ============
import requests
import json
import base64
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class BhashiniClient:
    def __init__(self):
        self.api_key = settings.BHASHINI_API_KEY
        self.user_id = settings.BHASHINI_USER_ID
        self.inference_api_key = settings.BHASHINI_INFERENCE_API_KEY
        self.base_url = settings.BHASHINI_BASE_URL
        self.session = requests.Session()

    def get_auth_token(self):
        """Get authentication token from BHASHINI"""
        url = f"{self.base_url}/ulca/apis/v0/model/getModelsPipeline"
        
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {
                            "sourceLanguage": "hi"
                        }
                    }
                }
            ],
            "pipelineRequestConfig": {
                "pipelineId": "64392f96daac500b55c543cd"
            }
        }
        
        headers = {
            "userID": self.user_id,
            "ulcaApiKey": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get auth token: {e}")
            raise

    def speech_to_text(self, audio_data, source_language="hi"):
        """Convert speech to text using BHASHINI ASR"""
        try:
            # Get model configuration
            auth_response = self.get_auth_token()
            
            if not auth_response.get('pipelineResponseConfig'):
                raise Exception("Failed to get pipeline configuration")

            # Extract service details
            pipeline_config = auth_response['pipelineResponseConfig'][0]
            service_id = pipeline_config['config'][0]['serviceId']
            inference_url = pipeline_config['config'][0]['inferenceEndPoint']['callbackUrl']
            
            # Prepare audio data
            if isinstance(audio_data, bytes):
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            else:
                with open(audio_data, 'rb') as audio_file:
                    audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')

            # Prepare inference request
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "asr",
                        "config": {
                            "language": {
                                "sourceLanguage": source_language
                            },
                            "serviceId": service_id,
                            "audioFormat": "wav",
                            "samplingRate": 16000
                        }
                    }
                ],
                "inputData": {
                    "audio": [
                        {
                            "audioContent": audio_base64
                        }
                    ]
                }
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": self.inference_api_key
            }

            # Make inference request
            response = self.session.post(inference_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('pipelineResponse') and result['pipelineResponse'][0].get('output'):
                return {
                    'text': result['pipelineResponse'][0]['output'][0]['source'],
                    'confidence': result['pipelineResponse'][0]['output'][0].get('confidence', 0.0),
                    'language': source_language
                }
            else:
                raise Exception("No speech recognized")
                
        except Exception as e:
            logger.error(f"Speech to text conversion failed: {e}")
            raise

    def text_to_speech(self, text, target_language="hi"):
        """Convert text to speech using BHASHINI TTS"""
        try:
            # Get TTS model configuration
            url = f"{self.base_url}/ulca/apis/v0/model/getModelsPipeline"
            
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "tts",
                        "config": {
                            "language": {
                                "sourceLanguage": target_language
                            }
                        }
                    }
                ],
                "pipelineRequestConfig": {
                    "pipelineId": "64392f96daac500b55c543cd"
                }
            }
            
            headers = {
                "userID": self.user_id,
                "ulcaApiKey": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            auth_response = response.json()
            
            # Extract TTS service details
            pipeline_config = auth_response['pipelineResponseConfig'][0]
            service_id = pipeline_config['config'][0]['serviceId']
            inference_url = pipeline_config['config'][0]['inferenceEndPoint']['callbackUrl']
            
            # Prepare TTS request
            tts_payload = {
                "pipelineTasks": [
                    {
                        "taskType": "tts",
                        "config": {
                            "language": {
                                "sourceLanguage": target_language
                            },
                            "serviceId": service_id,
                            "gender": "female",
                            "samplingRate": 22050
                        }
                    }
                ],
                "inputData": {
                    "input": [
                        {
                            "source": text
                        }
                    ]
                }
            }

            tts_headers = {
                "Content-Type": "application/json",
                "Authorization": self.inference_api_key
            }

            # Make TTS request
            tts_response = self.session.post(inference_url, json=tts_payload, headers=tts_headers)
            tts_response.raise_for_status()
            
            result = tts_response.json()
            
            if result.get('pipelineResponse') and result['pipelineResponse'][0].get('audio'):
                audio_content = result['pipelineResponse'][0]['audio'][0]['audioContent']
                return base64.b64decode(audio_content)
            else:
                raise Exception("Text to speech conversion failed")
                
        except Exception as e:
            logger.error(f"Text to speech conversion failed: {e}")
            raise

    def translate_text(self, text, source_language, target_language):
        """Translate text between languages using BHASHINI"""
        try:
            # Get translation model configuration
            url = f"{self.base_url}/ulca/apis/v0/model/getModelsPipeline"
            
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": source_language,
                                "targetLanguage": target_language
                            }
                        }
                    }
                ],
                "pipelineRequestConfig": {
                    "pipelineId": "64392f96daac500b55c543cd"
                }
            }
            
            headers = {
                "userID": self.user_id,
                "ulcaApiKey": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            auth_response = response.json()
            
            # Extract translation service details
            pipeline_config = auth_response['pipelineResponseConfig'][0]
            service_id = pipeline_config['config'][0]['serviceId']
            inference_url = pipeline_config['config'][0]['inferenceEndPoint']['callbackUrl']
            
            # Prepare translation request
            translation_payload = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": source_language,
                                "targetLanguage": target_language
                            },
                            "serviceId": service_id
                        }
                    }
                ],
                "inputData": {
                    "input": [
                        {
                            "source": text
                        }
                    ]
                }
            }

            translation_headers = {
                "Content-Type": "application/json",
                "Authorization": self.inference_api_key
            }

            # Make translation request
            translation_response = self.session.post(
                inference_url, 
                json=translation_payload, 
                headers=translation_headers
            )
            translation_response.raise_for_status()
            
            result = translation_response.json()
            
            if result.get('pipelineResponse') and result['pipelineResponse'][0].get('output'):
                return {
                    'translated_text': result['pipelineResponse'][0]['output'][0]['target'],
                    'source_language': source_language,
                    'target_language': target_language
                }
            else:
                raise Exception("Translation failed")
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise