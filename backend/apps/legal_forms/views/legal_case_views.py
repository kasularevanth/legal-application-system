# apps/legal_forms/views/legal_case_views.py
import json
import logging
from typing import Dict, Any

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ValidationError

from ..models import LegalCase, CaseTypeMapping, QuestionMapping, DocumentTemplate
from ..services.case_processor import CaseProcessor
from ..document_generator import WordDocumentGenerator
from ..serializers import LegalCaseSerializer, CaseTypeMappingSerializer

logger = logging.getLogger(__name__)

# Initialize services
case_processor = CaseProcessor()
document_generator = WordDocumentGenerator()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_initial_input(request):
    """Process initial user input to detect case type and start questioning"""
    try:
        data = request.data
        input_text = data.get('text', '').strip()
        mode = data.get('mode', 'text')  # 'voice' or 'text'
        language = data.get('language', 'hi')

        if not input_text:
            return Response(
                {'error': 'Input text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process input using case processor
        case = case_processor.process_initial_input(
            user=request.user,
            input_text=input_text,
            mode=mode,
            language=language
        )

        # Prepare response
        response_data = {
            'case_id': str(case.case_id),
            'status': case.status,
            'requires_questions': len(case.questions_asked) > 0
        }

        if case.detected_case_type:
            response_data.update({
                'case_type': case.detected_case_type.case_type,
                'confidence': case.detection_confidence,
                'keywords': case.detected_keywords,
                'questions': case.questions_asked,
                'template_id': case.detected_case_type.uuid
            })
        else:
            response_data.update({
                'error': case.error_details or 'Could not determine case type',
                'suggestions': _get_case_type_suggestions()
            })

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Failed to process initial input: {e}")
        return Response(
            {'error': 'Failed to process input', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    """Submit answer to a specific question"""
    try:
        data = request.data
        case_id = data.get('case_id')
        answer = data.get('answer', '').strip()
        mode = data.get('mode', 'text')

        if not case_id or not answer:
            return Response(
                {'error': 'case_id and answer are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get case
        case = get_object_or_404(LegalCase, case_id=case_id, user=request.user)

        # Submit answer
        success = case_processor.submit_answer(case, answer, mode)
        
        if not success:
            return Response(
                {'error': 'Failed to submit answer'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare response
        response_data = {
            'case_id': str(case.case_id),
            'question_index': case.current_question_index - 1,  # Previous question index
            'answer': answer,
            'next_question': None,
            'questioning_complete': case.is_questioning_complete()
        }

        # Get next question if available
        if not case.is_questioning_complete():
            next_question = case.get_current_question()
            response_data['next_question'] = next_question
        else:
            # All questions answered, ready for document generation
            response_data['ready_for_generation'] = True

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Failed to submit answer: {e}")
        return Response(
            {'error': 'Failed to submit answer', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_document(request):
    """Generate the final legal document"""
    try:
        data = request.data
        case_id = data.get('case_id')

        if not case_id:
            return Response(
                {'error': 'case_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get case
        case = get_object_or_404(LegalCase, case_id=case_id, user=request.user)

        # Validate case is ready for document generation
        if not case.is_questioning_complete():
            return Response(
                {'error': 'All questions must be answered before generating document'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate document
        result = document_generator.generate_document(case)

        if result['success']:
            return Response({
                'success': True,
                'document_url': result['document_url'],
                'document_id': result['document_id'],
                'template_used': result['template_used'],
                'preview': result['preview_text'],
                'case_status': case.status
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"Failed to generate document: {e}")
        return Response(
            {'error': 'Failed to generate document', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_case_status(request, case_id):
    """Get current status of a case"""
    try:
        case = get_object_or_404(LegalCase, case_id=case_id, user=request.user)
        
        status_info = case_processor.get_case_status(case_id)
        
        # Add additional case details
        status_info.update({
            'created_at': case.created_at.isoformat(),
            'updated_at': case.updated_at.isoformat(),
            'processing_steps': case.processing_steps,
            'current_question': case.get_current_question(),
            'answers': case.answers_received,
            'document_url': case.generated_document_url
        })

        return Response(status_info, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Failed to get case status: {e}")
        return Response(
            {'error': 'Failed to get case status', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_case_type_mappings(request):
    """Get all available case type mappings"""
    try:
        mappings = CaseTypeMapping.objects.filter(is_active=True).order_by('-priority')
        
        mappings_data = {}
        for mapping in mappings:
            mappings_data[str(mapping.uuid)] = mapping.keywords

        return Response({
            'mappings': mappings_data,
            'last_updated': mappings.first().updated_at.isoformat() if mappings.exists() else None
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Failed to get case type mappings: {e}")
        return Response(
            {'error': 'Failed to get case type mappings'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_question_mappings(request, case_type):
    """Get questions for a specific case type"""
    try:
        # Find case type mapping
        case_type_mapping = CaseTypeMapping.objects.filter(
            case_type__iexact=case_type,
            is_active=True
        ).first()

        if not case_type_mapping:
            return Response(
                {'error': f'Case type "{case_type}" not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get questions
        questions = QuestionMapping.objects.filter(
            case_type_mapping=case_type_mapping
        ).order_by('order')

        questions_data = {
            'questions': [q.question for q in questions],
            'required': [q.is_required for q in questions],
            'field_types': [q.field_type for q in questions],
            'field_names': [q.field_name for q in questions],
            'validation_rules': {q.field_name: q.validation_rules for q in questions}
        }

        return Response(questions_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Failed to get question mappings: {e}")
        return Response(
            {'error': 'Failed to get question mappings'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def preview_document(request):
    """Preview document before final generation"""
    try:
        data = request.data
        case_id = data.get('case_id')

        if not case_id:
            return Response(
                {'error': 'case_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        case = get_object_or_404(LegalCase, case_id=case_id, user=request.user)
        
        # Generate preview
        result = document_generator.preview_document(case)
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Failed to preview document: {e}")
        return Response(
            {'error': 'Failed to preview document', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_document(request, document_id):
    """Download generated document"""
    try:
        case = get_object_or_404(LegalCase, case_id=document_id, user=request.user)
        
        if not case.generated_document_url:
            return Response(
                {'error': 'Document not yet generated'},
                status=status.HTTP_404_NOT_FOUND
            )

        # For Azure Blob URLs, redirect to the blob
        if case.generated_document_url.startswith('http'):
            from django.shortcuts import redirect
            return redirect(case.generated_document_url)
        
        # For local files, serve directly
        if case.document_blob_name:
            file_path = os.path.join(settings.MEDIA_ROOT, 'documents', case.document_blob_name)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    response = HttpResponse(
                        f.read(),
                        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    )
                    response['Content-Disposition'] = f'attachment; filename="{case.document_blob_name}"'
                    return response

        return Response(
            {'error': 'Document file not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        logger.error(f"Failed to download document: {e}")
        return Response(
            {'error': 'Failed to download document'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_case_history(request):
    """Get case history for the user"""
    try:
        cases = LegalCase.objects.filter(user=request.user).order_by('-created_at')
        
        cases_data = []
        for case in cases:
            case_data = {
                'case_id': str(case.case_id),
                'status': case.status,
                'case_type': case.detected_case_type.case_type if case.detected_case_type else None,
                'created_at': case.created_at.isoformat(),
                'completed_at': case.completed_at.isoformat() if case.completed_at else None,
                'has_document': bool(case.generated_document_url),
                'progress': case_processor._calculate_progress(case)
            }
            cases_data.append(case_data)

        return Response({
            'cases': cases_data,
            'total_count': len(cases_data)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Failed to get case history: {e}")
        return Response(
            {'error': 'Failed to get case history'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _get_case_type_suggestions():
    """Get suggestions for available case types"""
    try:
        case_types = CaseTypeMapping.objects.filter(is_active=True).values_list('case_type', flat=True)
        return list(case_types)
    except Exception:
        return ['Property Damage', 'Contract Dispute', 'Rental Issues', 'Consumer Complaint']