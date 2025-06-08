
# ============ backend/management/commands/generate_test_data.py ============
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.legal_forms.models import LegalApplication, FormTemplate
from apps.legal_cases.models import LegalCase
import random
import json
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate test data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of test users to create',
        )
        parser.add_argument(
            '--cases',
            type=int,
            default=20,
            help='Number of test cases to create',
        )

    def handle(self, *args, **options):
        self.stdout.write('Generating test data...')

        # Create test users
        self.create_test_users(options['users'])
        
        # Create test legal cases
        self.create_test_cases(options['cases'])

        self.stdout.write(
            self.style.SUCCESS('Test data generation completed!')
        )

    def create_test_users(self, count):
        """Create test users"""
        self.stdout.write(f'Creating {count} test users...')
        
        indian_names = [
            ('Aarav', 'Sharma'), ('Vivaan', 'Verma'), ('Aditya', 'Singh'),
            ('Vihaan', 'Kumar'), ('Arjun', 'Gupta'), ('Sai', 'Patel'),
            ('Reyansh', 'Agarwal'), ('Ayaan', 'Jain'), ('Krishna', 'Reddy'),
            ('Ishaan', 'Nair'), ('Priya', 'Sharma'), ('Ananya', 'Verma'),
            ('Diya', 'Singh'), ('Aadhya', 'Kumar'), ('Kavya', 'Gupta'),
        ]

        languages = ['en', 'hi', 'te', 'ta', 'bn']
        states = ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Telangana']

        for i in range(count):
            first_name, last_name = random.choice(indian_names)
            username = f'user_{i+1}_{first_name.lower()}'
            
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='testpass123',
                first_name=first_name,
                last_name=last_name,
                preferred_language=random.choice(languages),
                state=random.choice(states),
                phone_number=f'+91{random.randint(7000000000, 9999999999)}'
            )
            
            if i == 0:  # Make first user staff
                user.is_staff = True
                user.save()

    def create_test_cases(self, count):
        """Create test legal cases"""
        self.stdout.write(f'Creating {count} test cases...')
        
        users = list(User.objects.filter(is_superuser=False))
        if not users:
            self.stdout.write('No users found to create cases for')
            return

        case_types = ['civil', 'criminal', 'family', 'consumer', 'property']
        statuses = ['draft', 'processing', 'analysis_complete', 'documents_generated']
        
        sample_transcriptions = [
            "मेरे पड़ोसी ने मेरी जमीन पर कब्जा कर लिया है। मैं उनके खिलाफ केस करना चाहता हूं।",
            "My landlord is not returning my security deposit. I need legal help.",
            "నా భర్త నన్ను వేధిస్తున్నాడు। విడాకుల కేసు పెట్టాలి అనుకుంటున్నా।",
            "I bought a defective mobile phone and the company is not replacing it.",
            "Police registered false case against me. I need bail application.",
        ]
        
        sample_analyses = [
            {
                "case_analysis": {
                    "primary_case_type": "property",
                    "confidence_score": 0.9,
                    "legal_complexity": "medium",
                    "urgency_level": "normal"
                },
                "extracted_information": {
                    "key_facts": ["Land dispute with neighbor", "Unauthorized occupation"],
                    "parties_involved": {"plaintiff": "User", "defendant": "Neighbor"}
                }
            },
            {
                "case_analysis": {
                    "primary_case_type": "civil",
                    "confidence_score": 0.8,
                    "legal_complexity": "low",
                    "urgency_level": "normal"
                },
                "extracted_information": {
                    "key_facts": ["Security deposit not returned", "Landlord-tenant dispute"],
                    "amounts_mentioned": [{"amount": 25000, "currency": "INR"}]
                }
            }
        ]

        for i in range(count):
            user = random.choice(users)
            case_type = random.choice(case_types)
            
            case = LegalCase.objects.create(
                user=user,
                case_id=f'CASE{datetime.now().year}{1000+i}',
                case_type=case_type,
                status=random.choice(statuses),
                transcription=random.choice(sample_transcriptions),
                analysis=random.choice(sample_analyses),
                confidence_score=random.uniform(0.7, 0.95),
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )