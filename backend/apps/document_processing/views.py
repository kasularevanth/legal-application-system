

# ============ apps/document_processing/views.py ============
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from apps.legal_forms.models import LegalApplication
from .pdf_generator import PDFGenerator
from .document_analyzer import DocumentAnalyzer
import os
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_application_pdf(request, application_id):
    """Download application as PDF"""
    try:
        application = get_object_or_404(
            LegalApplication, 
            id=application_id, 
            user=request.user
        )
        
        pdf_generator = PDFGenerator()
        pdf_content = pdf_generator.generate_application_pdf(application, return_content=True)
        
        response = HttpResponse(
            pdf_content,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{application.application_id}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to download PDF: {e}")
        return Response(
            {'error': 'Failed to generate PDF'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_all_applications(request):
    """Download all user applications as single PDF"""
    try:
        applications = LegalApplication.objects.filter(
            user=request.user,
            status__in=['submitted', 'under_review', 'approved', 'completed']
        ).order_by('-created_at')
        
        if not applications.exists():
            return Response(
                {'error': 'No applications found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        pdf_generator = PDFGenerator()
        file_path = pdf_generator.generate_bulk_applications_pdf(applications)
        
        with open(file_path, 'rb') as pdf_file:
            response = HttpResponse(
                pdf_file.read(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="all_applications.pdf"'
        
        # Clean up temporary file
        os.unlink(file_path)
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to download all applications: {e}")
        return Response(
            {'error': 'Failed to generate PDF'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_document(request, application_id):
    """Analyze document for completeness and compliance"""
    try:
        application = get_object_or_404(
            LegalApplication, 
            id=application_id, 
            user=request.user
        )
        
        analyzer = DocumentAnalyzer()
        analysis_result = analyzer.analyze_application(application)
        
        return Response(analysis_result)
        
    except Exception as e:
        logger.error(f"Failed to analyze document: {e}")
        return Response(
            {'error': 'Document analysis failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
