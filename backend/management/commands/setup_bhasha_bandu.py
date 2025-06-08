# ============ backend/management/commands/setup_bhasha_bandu.py ============
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from apps.legal_forms.models import FormTemplate, ApplicationField
from apps.legal_forms.form_templates.templates import LEGAL_TEMPLATES
from apps.notifications.models import NotificationTemplate
import json
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Set up BhashaBandu platform with initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Create admin user',
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@bhashabandu.com',
            help='Admin email address',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Admin password',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up BhashaBandu platform...')
        )

        try:
            # Run migrations
            self.stdout.write('Running migrations...')
            call_command('migrate', verbosity=0)

            # Create form templates
            self.create_form_templates()

            # Create notification templates
            self.create_notification_templates()

            # Create admin user if requested
            if options['create_admin']:
                self.create_admin_user(
                    options['admin_email'],
                    options['admin_password']
                )

            # Collect static files
            self.stdout.write('Collecting static files...')
            call_command('collectstatic', verbosity=0, interactive=False)

            self.stdout.write(
                self.style.SUCCESS('BhashaBandu setup completed successfully!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Setup failed: {str(e)}')
            )
            logger.error(f"Setup failed: {str(e)}")

    def create_form_templates(self):
        """Create initial form templates"""
        self.stdout.write('Creating form templates...')
        
        for template_data in LEGAL_TEMPLATES:
            template, created = FormTemplate.objects.get_or_create(
                name=template_data['name'],
                form_type=template_data['form_type'],
                defaults={
                    'description': template_data['description'],
                    'template_json': template_data,
                    'legal_requirements': template_data['legal_requirements'],
                    'court_types': template_data['court_types'],
                    'language': 'en',
                    'is_active': True
                }
            )

            if created:
                # Create template fields
                for field_data in template_data['fields']:
                    ApplicationField.objects.create(
                        template=template,
                        **field_data
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                self.stdout.write(f'Template already exists: {template.name}')

    def create_notification_templates(self):
        """Create notification templates"""
        self.stdout.write('Creating notification templates...')
        
        templates = [
            {
                'name': 'application_status_update',
                'notification_type': 'status_update',
                'subject_template': 'Application Status Update - {{application.application_id}}',
                'body_template': '''
                Dear {{user.first_name}},
                
                Your application {{application.application_id}} status has been updated to: {{status}}.
                
                Application Title: {{application.title}}
                Updated On: {{current_date}}
                
                You can view your application details at: {{application_url}}
                
                Best regards,
                BhashaBandu Team
                ''',
                'sms_template': 'Application {{application.application_id}} status: {{status}}. Check BhashaBandu app for details.',
            },
            {
                'name': 'application_reminder',
                'notification_type': 'reminder',
                'subject_template': 'Application Pending Review - {{application.application_id}}',
                'body_template': '''
                Dear {{user.first_name}},
                
                Your application {{application.application_id}} has been under review for {{days_pending}} days.
                
                We are processing your application and will update you soon.
                
                Application Title: {{application.title}}
                Submitted On: {{application.submitted_at}}
                
                Best regards,
                BhashaBandu Team
                ''',
                'sms_template': 'Application {{application.application_id}} under review for {{days_pending}} days.',
            },
            {
                'name': 'welcome_user',
                'notification_type': 'welcome',
                'subject_template': 'Welcome to BhashaBandu!',
                'body_template': '''
                Dear {{user.first_name}},
                
                Welcome to BhashaBandu - Voice-Enabled Legal Documentation Platform!
                
                You can now:
                - Create legal applications using voice input
                - Generate legal documents automatically
                - Track your application status in real-time
                
                Get started: {{platform_url}}
                
                Best regards,
                BhashaBandu Team
                ''',
                'sms_template': 'Welcome to BhashaBandu! Start creating legal applications with voice input.',
            }
        ]

        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created notification template: {template.name}')
                )

    def create_admin_user(self, email, password):
        """Create admin user"""
        self.stdout.write('Creating admin user...')
        
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Admin user already exists')
            return

        admin_user = User.objects.create_superuser(
            username='admin',
            email=email,
            password=password,
            first_name='Admin',
            last_name='User',
            preferred_language='en'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created admin user: {admin_user.username}')
        )
