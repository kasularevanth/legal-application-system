# ============ backend/tests/test_legal_forms.py ============
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.legal_forms.models import FormTemplate, LegalApplication

User = get_user_model()

class LegalFormsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a form template
        self.template = FormTemplate.objects.create(
            name='Test Petition',
            form_type='petition',
            description='Test template',
            template_json={'fields': []},
            legal_requirements='Test requirements',
            court_types=['District Court']
        )

    def test_get_form_templates(self):
        """Test retrieving form templates"""
        response = self.client.get('/api/forms/templates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_application(self):
        """Test creating a new application"""
        application_data = {
            'template_id': self.template.id,
            'title': 'Test Application',
            'form_data': {
                'petitioner_name': 'John Doe',
                'case_facts': 'Test case facts'
            }
        }
        
        response = self.client.post('/api/forms/applications/', application_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('application_id', response.data)

    def test_submit_application(self):
        """Test submitting an application"""
        # Create application first
        application = LegalApplication.objects.create(
            user=self.user,
            template=self.template,
            application_id='TEST123',
            title='Test Application',
            form_data={'petitioner_name': 'John Doe'},
            status='draft'
        )
        
        response = self.client.post(f'/api/forms/applications/{application.id}/submit/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check status changed
        application.refresh_from_db()
        self.assertEqual(application.status, 'submitted')