# apps/legal_forms/management/commands/seed_legal_data.py
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.legal_forms.models import CaseTypeMapping, QuestionMapping, DocumentTemplate
import uuid

class Command(BaseCommand):
    help = 'Seed database with legal case types, questions, and mappings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing data before seeding',
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Path to JSON file with seed data',
            default=None
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('Flushing existing legal data...')
            CaseTypeMapping.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data deleted'))

        # Load seed data
        seed_data = self.load_seed_data(options['file'])
        
        if not seed_data:
            self.stdout.write(self.style.ERROR('Failed to load seed data'))
            return

        # Seed case type mappings
        self.seed_case_type_mappings(seed_data)
        
        # Seed question mappings
        self.seed_question_mappings(seed_data)
        
        # Create sample document templates
        self.create_sample_templates()
        
        self.stdout.write(self.style.SUCCESS('Legal data seeding completed successfully'))

    def load_seed_data(self, file_path):
        """Load seed data from JSON file"""
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Default seed data
        return {
            "case_type_mappings": {
                "property_damage_complaint": [
                    "property damage", "neighbor damage", "wall damage", "house damage",
                    "building damage", "fence damage", "garden damage", "संपत्ति क्षति",
                    "पड़ोसी नुकसान", "घर का नुकसान", "दीवार का नुकसान", "बगीचे का नुकसान"
                ],
                "rental_issues": [
                    "rent problem", "landlord issue", "tenant rights", "eviction notice",
                    "deposit problem", "rent increase", "किराया समस्या", "मकान मालिक समस्या",
                    "किरायेदार अधिकार", "बेदखली नोटिस", "जमा राशि समस्या"
                ],
                "consumer_complaint": [
                    "defective product", "poor service", "refund issue", "warranty problem",
                    "online shopping", "consumer rights", "खराब उत्पाद", "गलत सेवा",
                    "रिफंड समस्या", "वारंटी समस्या", "ऑनलाइन खरीदारी", "उपभोक्ता अधिकार"
                ],
                "money_recovery": [
                    "loan recovery", "debt recovery", "money lent", "borrowed money",
                    "payment due", "unpaid amount", "ऋण वसूली", "कर्ज वसूली",
                    "उधार पैसा", "भुगतान बकाया", "अदत्त राशि"
                ]
            },
            "question_mappings": {
                "property_damage_complaint": [
                    {
                        "question": "What is your full name?",
                        "field_name": "complainant_name",
                        "field_type": "text",
                        "is_required": True,
                        "order": 1,
                        "validation_rules": {"min_length": 2, "max_length": 100},
                        "help_text": "Enter your complete legal name"
                    },
                    {
                        "question": "What is your complete address?",
                        "field_name": "complainant_address",
                        "field_type": "address",
                        "is_required": True,
                        "order": 2,
                        "validation_rules": {"min_length": 10},
                        "help_text": "Include house number, street, city, state, and PIN code"
                    },
                    {
                        "question": "Who caused the damage to your property?",
                        "field_name": "defendant_name",
                        "field_type": "text",
                        "is_required": True,
                        "order": 3,
                        "validation_rules": {"min_length": 2},
                        "help_text": "Name of the person responsible for damage"
                    },
                    {
                        "question": "When did the damage occur?",
                        "field_name": "incident_date",
                        "field_type": "date",
                        "is_required": True,
                        "order": 4,
                        "validation_rules": {"not_future": True},
                        "help_text": "Date when the damage happened"
                    },
                    {
                        "question": "Describe the damage in detail.",
                        "field_name": "damage_description",
                        "field_type": "textarea",
                        "is_required": True,
                        "order": 5,
                        "validation_rules": {"min_length": 20},
                        "help_text": "Detailed description of damage"
                    }
                ],
                "rental_issues": [
                    {
                        "question": "What is your full name?",
                        "field_name": "tenant_name",
                        "field_type": "text",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "question": "What is the rental property address?",
                        "field_name": "property_address",
                        "field_type": "address",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "question": "What is your landlord's name?",
                        "field_name": "landlord_name",
                        "field_type": "text",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "question": "What rental issue are you facing?",
                        "field_name": "issue_description",
                        "field_type": "textarea",
                        "is_required": True,
                        "order": 4,
                        "validation_rules": {"min_length": 20},
                        "help_text": "Describe your rental problem"
                    }
                ]
            },
            "template_field_mappings": {
                "property_damage_complaint": {
                    "complainant_name": "complainant_name",
                    "complainant_address": "complainant_address",
                    "defendant_name": "defendant_name",
                    "incident_date": "incident_date",
                    "damage_description": "damage_description"
                }
            }
        }

    def seed_case_type_mappings(self, seed_data):
        """Seed case type mappings"""
        case_mappings = seed_data.get('case_type_mappings', {})
        
        for case_type, keywords in case_mappings.items():
            # Convert case_type to readable format
            readable_name = case_type.replace('_', ' ').title()
            
            mapping, created = CaseTypeMapping.objects.get_or_create(
                case_type=readable_name,
                defaults={
                    'keywords': keywords,
                    'confidence_threshold': 0.6,
                    'is_active': True,
                    'priority': self.get_priority_for_case_type(case_type)
                }
            )
            
            if created:
                self.stdout.write(f'Created case type mapping: {readable_name}')
            else:
                # Update keywords if mapping exists
                mapping.keywords = keywords
                mapping.save()
                self.stdout.write(f'Updated case type mapping: {readable_name}')

    def seed_question_mappings(self, seed_data):
        """Seed question mappings"""
        question_mappings = seed_data.get('question_mappings', {})
        template_mappings = seed_data.get('template_field_mappings', {})
        
        for case_type, questions in question_mappings.items():
            try:
                readable_name = case_type.replace('_', ' ').title()
                case_type_mapping = CaseTypeMapping.objects.get(case_type=readable_name)
                
                # Delete existing questions for this case type
                QuestionMapping.objects.filter(case_type_mapping=case_type_mapping).delete()
                
                # Create new questions
                for question_data in questions:
                    QuestionMapping.objects.create(
                        case_type_mapping=case_type_mapping,
                        question=question_data['question'],
                        field_name=question_data['field_name'],
                        field_type=question_data['field_type'],
                        is_required=question_data['is_required'],
                        order=question_data['order'],
                        validation_rules=question_data.get('validation_rules', {}),
                        help_text=question_data.get('help_text', '')
                    )
                
                self.stdout.write(f'Created {len(questions)} questions for {readable_name}')
                
            except CaseTypeMapping.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Case type mapping not found: {readable_name}')
                )

    def create_sample_templates(self):
        """Create sample document templates"""
        templates_data = [
            {
                'case_type': 'Property Damage Complaint',
                'name': 'Property Damage Complaint Template',
                'blob_name': 'property_damage_template.docx',
                'field_mappings': {
                    'complainant_name': 'complainant_name',
                    'complainant_address': 'complainant_address',
                    'defendant_name': 'defendant_name',
                    'incident_date': 'incident_date',
                    'damage_description': 'damage_description',
                    'current_date': 'current_date',
                    'case_id': 'case_id'
                }
            },
            {
                'case_type': 'Rental Issues',
                'name': 'Rental Dispute Application Template',
                'blob_name': 'rental_issues_template.docx',
                'field_mappings': {
                    'tenant_name': 'tenant_name',
                    'property_address': 'property_address',
                    'landlord_name': 'landlord_name',
                    'issue_description': 'issue_description',
                    'current_date': 'current_date',
                    'case_id': 'case_id'
                }
            },
            {
                'case_type': 'Consumer Complaint',
                'name': 'Consumer Complaint Template',
                'blob_name': 'consumer_complaint_template.docx',
                'field_mappings': {
                    'consumer_name': 'consumer_name',
                    'consumer_address': 'consumer_address',
                    'seller_name': 'seller_name',
                    'product_service': 'product_service',
                    'complaint_details': 'complaint_details',
                    'current_date': 'current_date',
                    'case_id': 'case_id'
                }
            }
        ]
        
        for template_data in templates_data:
            try:
                case_type_mapping = CaseTypeMapping.objects.get(
                    case_type=template_data['case_type']
                )
                
                template, created = DocumentTemplate.objects.get_or_create(
                    case_type_mapping=case_type_mapping,
                    name=template_data['name'],
                    defaults={
                        'blob_url': f"file://templates/{template_data['blob_name']}",
                        'blob_container': 'legal-documents',
                        'blob_name': template_data['blob_name'],
                        'template_version': '1.0',
                        'field_mappings': template_data['field_mappings'],
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'Created template: {template_data["name"]}')
                else:
                    self.stdout.write(f'Template already exists: {template_data["name"]}')
                    
            except CaseTypeMapping.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Case type not found: {template_data["case_type"]}')
                )

    def get_priority_for_case_type(self, case_type):
        """Get priority value for case type"""
        priorities = {
            'property_damage_complaint': 100,
            'rental_issues': 90,
            'consumer_complaint': 80,
            'money_recovery': 70,
            'family_dispute': 60,
            'employment_issues': 50
        }
        
        return priorities.get(case_type, 10)