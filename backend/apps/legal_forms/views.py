# ============ apps/legal_forms/views.py ============
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid
from .models import FormTemplate, LegalApplication, LegalKnowledgeBase
from .serializers import (
    FormTemplateSerializer, 
    LegalApplicationSerializer, 
    LegalKnowledgeBaseSerializer,
    ApplicationCreateSerializer
)
from apps.document_processing.pdf_generator import PDFGenerator
import logging

logger = logging.getLogger(__name__)

class FormTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for managing form templates"""
    queryset = FormTemplate.objects.filter(is_active=True)
    serializer_class = FormTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['form_type', 'language']
    search_fields = ['name', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by user's preferred language if specified
        user_language = self.request.user.preferred_language
        if user_language and user_language != 'en':
            # First try to get templates in user's language, fallback to English
            language_specific = queryset.filter(language=user_language)
            if language_specific.exists():
                return language_specific
        return queryset.filter(language='en')

class LegalApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing legal applications"""
    serializer_class = LegalApplicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'template__form_type']
    search_fields = ['title', 'application_id']
    ordering_fields = ['created_at', 'updated_at', 'submitted_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return LegalApplication.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ApplicationCreateSerializer
        return LegalApplicationSerializer

    def perform_create(self, serializer):
        # Generate unique application ID
        application_id = f"APP{timezone.now().year}{uuid.uuid4().hex[:8].upper()}"
        serializer.save(
            user=self.request.user,
            application_id=application_id
        )

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit an application for review"""
        application = self.get_object()
        
        if application.status != 'draft':
            return Response(
                {'error': 'Only draft applications can be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate required fields
        template = application.template
        required_fields = template.fields.filter(is_required=True)
        missing_fields = []
        
        for field in required_fields:
            if field.field_name not in application.form_data or not application.form_data[field.field_name]:
                missing_fields.append(field.label)
        
        if missing_fields:
            return Response(
                {
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update status and timestamp
        application.status = 'submitted'
        application.submitted_at = timezone.now()
        application.save()

        # Generate PDF document
        try:
            pdf_generator = PDFGenerator()
            pdf_path = pdf_generator.generate_application_pdf(application)
            logger.info(f"PDF generated for application {application.application_id}: {pdf_path}")
        except Exception as e:
            logger.error(f"Failed to generate PDF for application {application.application_id}: {e}")

        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download application as PDF"""
        application = self.get_object()
        
        try:
            pdf_generator = PDFGenerator()
            pdf_content = pdf_generator.generate_application_pdf(application, return_content=True)
            
            response = Response(
                pdf_content,
                content_type='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename="{application.application_id}.pdf"'
                }
            )
            return response
        except Exception as e:
            logger.error(f"Failed to generate PDF for download: {e}")
            return Response(
                {'error': 'Failed to generate PDF'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Create a duplicate of an existing application"""
        original_application = self.get_object()
        
        # Create new application with same data
        new_application = LegalApplication.objects.create(
            user=request.user,
            template=original_application.template,
            application_id=f"APP{timezone.now().year}{uuid.uuid4().hex[:8].upper()}",
            title=f"Copy of {original_application.title}",
            form_data=original_application.form_data.copy(),
            status='draft'
        )
        
        serializer = self.get_serializer(new_application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LegalKnowledgeBaseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for legal knowledge base"""
    queryset = LegalKnowledgeBase.objects.filter(is_published=True)
    serializer_class = LegalKnowledgeBaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'language']
    search_fields = ['title', 'content', 'tags']

    def get_queryset(self):
        queryset = super().get_queryset()
        user_language = self.request.user.preferred_language
        if user_language:
            return queryset.filter(language=user_language)
        return queryset
