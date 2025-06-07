
# ============ apps/legal_forms/serializers.py ============
from rest_framework import serializers
from .models import FormTemplate, LegalApplication, ApplicationField, LegalKnowledgeBase

class ApplicationFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationField
        fields = '__all__'

class FormTemplateSerializer(serializers.ModelSerializer):
    fields = ApplicationFieldSerializer(many=True, read_only=True)
    
    class Meta:
        model = FormTemplate
        fields = ['id', 'name', 'form_type', 'description', 'template_json', 
                 'legal_requirements', 'court_types', 'language', 'fields']

class LegalApplicationSerializer(serializers.ModelSerializer):
    template = FormTemplateSerializer(read_only=True)
    
    class Meta:
        model = LegalApplication
        fields = ['id', 'application_id', 'title', 'form_data', 'status', 
                 'template', 'submitted_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'application_id', 'created_at', 'updated_at']

class ApplicationCreateSerializer(serializers.ModelSerializer):
    template_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = LegalApplication
        fields = ['template_id', 'title', 'form_data']
    
    def validate_template_id(self, value):
        try:
            template = FormTemplate.objects.get(id=value, is_active=True)
        except FormTemplate.DoesNotExist:
            raise serializers.ValidationError("Invalid template ID")
        return value
    
    def create(self, validated_data):
        template_id = validated_data.pop('template_id')
        template = FormTemplate.objects.get(id=template_id)
        validated_data['template'] = template
        return super().create(validated_data)

class LegalKnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalKnowledgeBase
        fields = ['id', 'title', 'content', 'category', 'language', 'tags', 'created_at']