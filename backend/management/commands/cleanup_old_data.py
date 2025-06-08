

# ============ backend/management/commands/cleanup_old_data.py ============
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.legal_cases.models import LegalCase
from apps.notifications.models import Notification
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Clean up old data and files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete data older than specified days',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)

        self.stdout.write(f'Cleaning data older than {days} days...')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be deleted'))

        # Clean old notifications
        old_notifications = Notification.objects.filter(
            created_at__lt=cutoff_date,
            status='delivered'
        )
        
        self.stdout.write(f'Found {old_notifications.count()} old notifications')
        if not dry_run:
            deleted_count = old_notifications.delete()[0]
            self.stdout.write(f'Deleted {deleted_count} old notifications')

        # Clean old temporary files
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        if os.path.exists(temp_dir):
            cleaned_files = 0
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    file_time = timezone.datetime.fromtimestamp(
                        os.path.getctime(file_path)
                    ).replace(tzinfo=timezone.get_current_timezone())
                    
                    if file_time < cutoff_date:
                        if not dry_run:
                            os.remove(file_path)
                        cleaned_files += 1
            
            self.stdout.write(f'Cleaned {cleaned_files} temporary files')

        # Clean old draft cases (never processed)
        old_drafts = LegalCase.objects.filter(
            created_at__lt=cutoff_date,
            status='draft'
        )
        
        self.stdout.write(f'Found {old_drafts.count()} old draft cases')
        if not dry_run:
            deleted_count = old_drafts.delete()[0]
            self.stdout.write(f'Deleted {deleted_count} old draft cases')

        self.stdout.write(self.style.SUCCESS('Cleanup completed!'))