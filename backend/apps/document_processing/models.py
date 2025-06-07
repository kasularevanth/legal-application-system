# ============ apps/document_processing/models.py ============
from django.db import models
from apps.authentication.models import User
from apps.legal_forms.models import LegalApplication

class DocumentTemplate(models.Model):
    """Templates for generating documents"""
    name = models.CharField(max_length=200)
    document_type = models.CharField(max_length=100)
    template_content = models.TextField()  # HTML/Markdown template
    css_styles = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GeneratedDocument(models.Model):
    """Track generated documents"""
    application = models.ForeignKey(LegalApplication, on_delete=models.CASCADE, related_name='documents')
    template = models.ForeignKey(DocumentTemplate, on_delete=models.SET_NULL, null=True)
    file_path = models.CharField(max_length=500)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)
    download_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Document for {self.application.application_id}"

class DocumentAnalysis(models.Model):
    """AI analysis results for documents"""
    document = models.OneToOneField(GeneratedDocument, on_delete=models.CASCADE)
    completeness_score = models.FloatField()  # 0.0 to 1.0
    legal_compliance_score = models.FloatField()
    missing_fields = models.JSONField(default=list)
    recommendations = models.TextField()
    analyzed_at = models.DateTimeField(auto_now_add=True)