# apps/legal_forms/tasks.py
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from apps.notifications.services import NotificationService
from apps.legal_forms.models import LegalCase, CaseProcessingLog
from apps.legal_forms.services.case_processor import CaseProcessor
from apps.document_processing.document_generator import WordDocumentGenerator
import logging
import json

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_case_async(self, case_id):
    """Asynchronously process a legal case"""
    try:
        case = LegalCase.objects.get(case_id=case_id)
        case_processor = CaseProcessor()
        
        case.add_processing_step("Async processing started")
        
        # Re-analyze case if needed
        if case.status == 'input_received':
            # Detect case type again with more thorough analysis
            case_type, confidence, keywords = case_processor.detector.detect_case_type(
                case.initial_input, 
                case.input_language
            )
            
            if case_type and confidence > case.detection_confidence:
                case.detected_case_type = case_type
                case.detection_confidence = confidence
                case.detected_keywords = keywords
                case.status = 'case_type_detected'
                case.save()
                case.add_processing_step(f"Enhanced case type detection: {case_type.case_type}")
        
        # Send notification to user about progress
        send_case_update_notification.delay(case_id, 'processing_update')
        
        return {
            'success': True,
            'case_id': str(case_id),
            'status': case.status,
            'confidence': case.detection_confidence
        }
        
    except LegalCase.DoesNotExist:
        logger.error(f"Case {case_id} not found for async processing")
        return {'success': False, 'error': 'Case not found'}
    
    except Exception as e:
        logger.error(f"Async case processing failed for {case_id}: {e}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying case processing for {case_id}, attempt {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        
        # Mark case as error after max retries
        try:
            case = LegalCase.objects.get(case_id=case_id)
            case.status = 'error'
            case.error_details = f"Async processing failed: {str(e)}"
            case.save()
            case.add_processing_step(f"Async processing failed after {self.max_retries} retries")
        except:
            pass
        
        return {'success': False, 'error': str(e)}

@shared_task(bind=True, max_retries=2)
def generate_document_async(self, case_id):
    """Asynchronously generate legal document"""
    try:
        case = LegalCase.objects.get(case_id=case_id)
        
        # Validate case is ready for document generation
        if not case.is_questioning_complete():
            return {
                'success': False, 
                'error': 'Case not ready for document generation'
            }
        
        case.status = 'generating_document'
        case.save()
        case.add_processing_step("Document generation started")
        
        # Generate document
        document_generator = WordDocumentGenerator()
        result = document_generator.generate_document(case)
        
        if result['success']:
            # Send success notification
            send_case_update_notification.delay(case_id, 'document_ready')
            
            # Log success
            CaseProcessingLog.objects.create(
                case=case,
                step='generate_document_async',
                status='completed',
                details={
                    'document_url': result['document_url'],
                    'template_used': result['template_used']
                }
            )
            
            return result
        else:
            # Handle generation failure
            case.status = 'error'
            case.error_details = result['error']
            case.save()
            
            # Send error notification
            send_case_update_notification.delay(case_id, 'error')
            
            return result
            
    except LegalCase.DoesNotExist:
        logger.error(f"Case {case_id} not found for document generation")
        return {'success': False, 'error': 'Case not found'}
    
    except Exception as e:
        logger.error(f"Document generation failed for {case_id}: {e}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying document generation for {case_id}")
            raise self.retry(countdown=120, exc=e)
        
        # Mark as error after retries
        try:
            case = LegalCase.objects.get(case_id=case_id)
            case.status = 'error'
            case.error_details = f"Document generation failed: {str(e)}"
            case.save()
            send_case_update_notification.delay(case_id, 'error')
        except:
            pass
        
        return {'success': False, 'error': str(e)}

@shared_task
def send_case_update_notification(case_id, notification_type):
    """Send notification about case status update"""
    try:
        case = LegalCase.objects.get(case_id=case_id)
        notification_service = NotificationService()
        
        # Determine notification content based on type
        if notification_type == 'processing_update':
            template_name = 'case_processing_update'
            subject = f"Legal Case {case.case_id[:8]} - Processing Update"
            
        elif notification_type == 'document_ready':
            template_name = 'case_document_ready'
            subject = f"Legal Case {case.case_id[:8]} - Document Ready"
            
        elif notification_type == 'error':
            template_name = 'case_processing_error'
            subject = f"Legal Case {case.case_id[:8]} - Processing Error"
            
        else:
            template_name = 'case_status_update'
            subject = f"Legal Case {case.case_id[:8]} - Status Update"
        
        # Prepare context data
        context_data = {
            'case': case,
            'user': case.user,
            'case_id': str(case.case_id),
            'status': case.status,
            'case_type': case.detected_case_type.case_type if case.detected_case_type else 'Unknown',
            'progress': _calculate_progress(case),
            'document_url': case.generated_document_url,
            'error_details': case.error_details,
            'created_at': case.created_at,
            'support_email': settings.DEFAULT_FROM_EMAIL
        }
        
        # Send email notification
        success = notification_service.send_notification(
            user=case.user,
            notification_type='email',
            template_name=template_name,
            context_data=context_data
        )
        
        # Also send SMS for important updates
        if notification_type in ['document_ready', 'error'] and case.user.phone_number:
            sms_success = notification_service.send_notification(
                user=case.user,
                notification_type='sms',
                template_name=template_name,
                context_data=context_data
            )
            
        logger.info(f"Sent {notification_type} notification for case {case_id}")
        return {'success': True, 'notification_type': notification_type}
        
    except LegalCase.DoesNotExist:
        logger.error(f"Case {case_id} not found for notification")
        return {'success': False, 'error': 'Case not found'}
    
    except Exception as e:
        logger.error(f"Failed to send notification for case {case_id}: {e}")
        return {'success': False, 'error': str(e)}

@shared_task
def cleanup_stale_cases():
    """Clean up cases that have been stuck in processing for too long"""
    try:
        # Find cases stuck in processing for more than 2 hours
        cutoff_time = timezone.now() - timezone.timedelta(hours=2)
        
        stale_cases = LegalCase.objects.filter(
            status__in=['input_received', 'case_type_detected', 'gathering_info', 'generating_document'],
            updated_at__lt=cutoff_time
        )
        
        cleanup_count = 0
        for case in stale_cases:
            case.status = 'error'
            case.error_details = 'Processing timeout - case was stuck in processing state'
            case.save()
            case.add_processing_step("Marked as error due to processing timeout")
            
            # Send notification to user
            send_case_update_notification.delay(str(case.case_id), 'error')
            cleanup_count += 1
        
        logger.info(f"Cleaned up {cleanup_count} stale cases")
        return {'cleaned_up': cleanup_count}
        
    except Exception as e:
        logger.error(f"Stale case cleanup failed: {e}")
        return {'error': str(e)}

@shared_task
def generate_analytics_report():
    """Generate analytics report for legal case processing"""
    try:
        from django.db.models import Count, Avg
        from datetime import datetime, timedelta
        
        # Calculate metrics for the last 24 hours
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=24)
        
        # Basic metrics
        total_cases = LegalCase.objects.filter(created_at__gte=start_time).count()
        completed_cases = LegalCase.objects.filter(
            created_at__gte=start_time,
            status='completed'
        ).count()
        
        # Case type distribution
        case_types = LegalCase.objects.filter(
            created_at__gte=start_time,
            detected_case_type__isnull=False
        ).values('detected_case_type__case_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Processing times
        processing_logs = CaseProcessingLog.objects.filter(
            timestamp__gte=start_time,
            processing_time_ms__isnull=False
        )
        
        avg_processing_time = processing_logs.aggregate(
            avg_time=Avg('processing_time_ms')
        )['avg_time'] or 0
        
        # Success rates
        success_rate = (completed_cases / total_cases * 100) if total_cases > 0 else 0
        
        # Error analysis
        error_cases = LegalCase.objects.filter(
            created_at__gte=start_time,
            status='error'
        ).count()
        
        report = {
            'period': f"{start_time.isoformat()} to {end_time.isoformat()}",
            'total_cases': total_cases,
            'completed_cases': completed_cases,
            'error_cases': error_cases,
            'success_rate': round(success_rate, 2),
            'avg_processing_time_ms': round(avg_processing_time, 2),
            'case_type_distribution': list(case_types),
            'generated_at': timezone.now().isoformat()
        }
        
        # Store report (could be saved to database or sent to monitoring system)
        logger.info(f"Generated analytics report: {json.dumps(report, indent=2)}")
        
        return report
        
    except Exception as e:
        logger.error(f"Analytics report generation failed: {e}")
        return {'error': str(e)}

@shared_task
def batch_process_pending_cases():
    """Process cases that are pending in the system"""
    try:
        # Find cases that need processing
        pending_cases = LegalCase.objects.filter(
            status__in=['input_received', 'case_type_detected']
        ).order_by('created_at')
        
        processed_count = 0
        for case in pending_cases[:10]:  # Process maximum 10 cases at a time
            try:
                # Queue for async processing
                process_case_async.delay(str(case.case_id))
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to queue case {case.case_id} for processing: {e}")
        
        logger.info(f"Queued {processed_count} cases for batch processing")
        return {'queued_cases': processed_count}
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        return {'error': str(e)}

@shared_task
def optimize_case_detection_models():
    """Optimize case detection models based on recent data"""
    try:
        from apps.legal_forms.services.case_processor import CaseTypeDetector
        
        # Get recent successful cases for training data
        recent_cases = LegalCase.objects.filter(
            status='completed',
            detected_case_type__isnull=False,
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).select_related('detected_case_type')
        
        if recent_cases.count() < 10:
            logger.info("Not enough recent cases for model optimization")
            return {'message': 'Insufficient data for optimization'}
        
        # Re-initialize detector with fresh data
        detector = CaseTypeDetector()
        detector._initialize_models()
        
        # Test accuracy on recent cases
        correct_predictions = 0
        total_tests = min(recent_cases.count(), 50)  # Test on up to 50 cases
        
        for case in recent_cases[:total_tests]:
            predicted_type, confidence, _ = detector.detect_case_type(
                case.initial_input,
                case.input_language
            )
            
            if predicted_type and predicted_type.id == case.detected_case_type.id:
                correct_predictions += 1
        
        accuracy = (correct_predictions / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"Model optimization completed. Accuracy: {accuracy:.2f}%")
        
        return {
            'accuracy': round(accuracy, 2),
            'total_tests': total_tests,
            'correct_predictions': correct_predictions,
            'optimization_completed': True
        }
        
    except Exception as e:
        logger.error(f"Model optimization failed: {e}")
        return {'error': str(e)}

def _calculate_progress(case):
    """Calculate case completion progress"""
    if case.status == 'completed':
        return 100.0
    elif case.status == 'error':
        return 0.0
    elif case.status == 'input_received':
        return 10.0
    elif case.status == 'case_type_detected':
        return 25.0
    elif case.status == 'gathering_info':
        if case.questions_asked:
            question_progress = (case.current_question_index / len(case.questions_asked)) * 50
            return 25.0 + question_progress
        return 50.0
    elif case.status == 'generating_document':
        return 80.0
    elif case.status == 'document_ready':
        return 95.0
    
    return 0.0