"""
Document analysis using Azure OpenAI for legal compliance checking
"""
import openai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    def __init__(self):
        openai.api_type = "azure"
        openai.api_base = settings.AZURE_OPENAI_ENDPOINT
        openai.api_version = settings.AZURE_OPENAI_API_VERSION
        openai.api_key = settings.AZURE_OPENAI_API_KEY
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME

    def analyze_application(self, application):
        """Analyze legal application for completeness and compliance"""
        try:
            template = application.template
            form_data = application.form_data
            
            prompt = f"""
            You are a legal document analyzer. Please analyze this {template.form_type} for:
            1. Completeness (are all required fields filled adequately?)
            2. Legal compliance (does it meet legal requirements?)
            3. Quality of content (is the information clear and well-structured?)
            
            Template: {template.name}
            Legal Requirements: {template.legal_requirements}
            
            Form Data: {json.dumps(form_data, indent=2)}
            
            Provide analysis in this JSON format:
            {{
                "completeness_score": 0.85,
                "legal_compliance_score": 0.90,
                "overall_score": 0.88,
                "missing_fields": ["field1", "field2"],
                "recommendations": [
                    "Add more specific details about...",
                    "Include documentation for..."
                ],
                "compliance_issues": [
                    "Issue 1 description",
                    "Issue 2 description"
                ],
                "strengths": [
                    "Well-documented facts",
                    "Clear relief sought"
                ]
            }}
            """
            
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a legal document analyst with expertise in Indian law."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return {
                "completeness_score": 0.5,
                "legal_compliance_score": 0.5,
                "overall_score": 0.5,
                "missing_fields": [],
                "recommendations": ["Analysis could not be completed. Please review manually."],
                "compliance_issues": [],
                "strengths": []
            }

    def suggest_improvements(self, application, analysis_result):
        """Suggest specific improvements based on analysis"""
        try:
            prompt = f"""
            Based on the document analysis results, provide specific, actionable suggestions to improve this legal document:
            
            Document Type: {application.template.form_type}
            Analysis Results: {json.dumps(analysis_result, indent=2)}
            Current Form Data: {json.dumps(application.form_data, indent=2)}
            
            Provide suggestions in this format:
            {{
                "field_improvements": {{
                    "field_name": "specific suggestion for this field"
                }},
                "additional_sections": [
                    "Section 1: Description",
                    "Section 2: Description"
                ],
                "legal_citations": [
                    "Relevant law section 1",
                    "Relevant law section 2"
                ],
                "documentation_needed": [
                    "Document 1",
                    "Document 2"
                ]
            }}
            """
            
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a legal advisor providing document improvement suggestions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Improvement suggestion failed: {e}")
            return {
                "field_improvements": {},
                "additional_sections": [],
                "legal_citations": [],
                "documentation_needed": []
            }