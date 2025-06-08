# apps/legal_forms/models.py (Enhanced)
from django.db import models
from apps.authentication.models import User
import uuid
import json

class CaseTypeMapping(models.Model):
    """Mapping between keywords and case types"""
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    case_type = models.CharField(max_length=200)
    keywords = models.JSONField(default=list)  # List of keywords
    confidence_threshold = models.FloatField(default=0.7)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)  # Higher priority takes precedence
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'case_type']

    def __str__(self):
        return f"{self.case_type} - {len(self.keywords)} keywords"

class QuestionMapping(models.Model):
    """Questions for each case type"""
    case_type_mapping = models.ForeignKey(CaseTypeMapping, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    field_name = models.CharField(max_length=100)  # Field name in template
    field_type = models.CharField(max_length=50, choices=[
        ('text', 'Text'),
        ('date', 'Date'),
        ('number', 'Number'),
        ('address', 'Address'),
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('select', 'Select'),
        ('textarea', 'Long Text'),
    ], default='text')
    is_required = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    validation_rules = models.JSONField(default=dict)
    help_text = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.case_type_mapping.case_type} - {self.question[:50]}"

class DocumentTemplate(models.Model):
    """Document templates stored in Azure Blob"""
    case_type_mapping = models.ForeignKey(CaseTypeMapping, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=200)
    blob_url = models.URLField()  # Azure Blob Storage URL
    blob_container = models.CharField(max_length=100)
    blob_name = models.CharField(max_length=200)
    template_version = models.CharField(max_length=20, default='1.0')
    field_mappings = models.JSONField(default=dict)  # Map question fields to template placeholders
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} v{self.template_version}"

class LegalCase(models.Model):
    """Enhanced legal case with voice processing"""
    STATUS_CHOICES = [
        ('input_received', 'Input Received'),
        ('case_type_detected', 'Case Type Detected'),
        ('gathering_info', 'Gathering Information'),
        ('generating_document', 'Generating Document'),
        ('document_ready', 'Document Ready'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    case_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Input processing
    initial_input = models.TextField()
    input_mode = models.CharField(max_length=10, choices=[('voice', 'Voice'), ('text', 'Text')])
    input_language = models.CharField(max_length=10, default='hi')
    
    # Case type detection
    detected_case_type = models.ForeignKey(CaseTypeMapping, on_delete=models.SET_NULL, null=True, blank=True)
    detection_confidence = models.FloatField(default=0.0)
    detected_keywords = models.JSONField(default=list)
    
    # Questions and answers
    questions_asked = models.JSONField(default=list)
    answers_received = models.JSONField(default=dict)
    current_question_index = models.IntegerField(default=0)
    
    # Document generation
    template_used = models.ForeignKey(DocumentTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    generated_document_url = models.URLField(blank=True)
    document_blob_name = models.CharField(max_length=200, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='input_received')
    processing_steps = models.JSONField(default=list)
    error_details = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Case {self.case_id} - {self.status}"

    def add_processing_step(self, step: str):
        """Add a processing step to track progress"""
        if not self.processing_steps:
            self.processing_steps = []
        self.processing_steps.append({
            'step': step,
            'timestamp': timezone.now().isoformat()
        })
        self.save(update_fields=['processing_steps'])

    def get_current_question(self):
        """Get the current question to ask"""
        if (self.detected_case_type and 
            self.current_question_index < len(self.questions_asked)):
            return self.questions_asked[self.current_question_index]
        return None

    def submit_answer(self, answer: str):
        """Submit an answer and move to next question"""
        current_question = self.get_current_question()
        if current_question:
            if not self.answers_received:
                self.answers_received = {}
            self.answers_received[current_question] = answer
            self.current_question_index += 1
            self.save(update_fields=['answers_received', 'current_question_index'])

    def is_questioning_complete(self):
        """Check if all questions have been answered"""
        return (self.detected_case_type and 
                self.current_question_index >= len(self.questions_asked))

class CaseProcessingLog(models.Model):
    """Log all processing steps for debugging and analytics"""
    case = models.ForeignKey(LegalCase, on_delete=models.CASCADE, related_name='logs')
    step = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    details = models.JSONField(default=dict)
    processing_time_ms = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class DocumentFeedback(models.Model):
    """User feedback on generated documents"""
    case = models.ForeignKey(LegalCase, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    accuracy_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    completeness_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    clarity_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField(blank=True)
    suggested_improvements = models.JSONField(default=list)
    would_recommend = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.case.case_id} - {self.rating}/5 stars"