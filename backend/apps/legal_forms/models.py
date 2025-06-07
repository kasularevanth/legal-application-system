
# ============ apps/legal_forms/models.py ============
from django.db import models
from apps.authentication.models import User

class FormTemplate(models.Model):
    FORM_TYPES = [
        ('petition', 'Petition'),
        ('application', 'Application'),
        ('appeal', 'Appeal'),
        ('complaint', 'Complaint'),
        ('affidavit', 'Affidavit'),
        ('notice', 'Notice'),
    ]
    
    name = models.CharField(max_length=200)
    form_type = models.CharField(max_length=50, choices=FORM_TYPES)
    description = models.TextField()
    template_json = models.JSONField()  # Form structure
    legal_requirements = models.TextField()
    court_types = models.JSONField(default=list)  # Applicable court types
    language = models.CharField(max_length=5, default='en')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.form_type})"

class LegalApplication(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE)
    application_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    form_data = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application_id} - {self.title}"

class ApplicationField(models.Model):
    template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='fields')
    field_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=50)  # text, number, date, select, etc.
    label = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=False)
    validation_rules = models.JSONField(default=dict)
    options = models.JSONField(default=list)  # For select fields
    order = models.IntegerField(default=0)

class LegalKnowledgeBase(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=100)
    language = models.CharField(max_length=5, default='en')
    tags = models.JSONField(default=list)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)