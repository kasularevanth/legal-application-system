# ============ management/commands/backup_data.py ============
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
import gzip
import shutil
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create comprehensive backup of application data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--upload-to-s3',
            action='store_true',
            help='Upload backup to S3 storage',
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress backup files',
        )

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(settings.BASE_DIR, 'backups', timestamp)
        os.makedirs(backup_dir, exist_ok=True)
        
        try:
            # Database backup
            self.stdout.write('Creating database backup...')
            db_backup_file = os.path.join(backup_dir, 'database.json')
            with open(db_backup_file, 'w') as f:
                call_command('dumpdata', '--natural-foreign', '--natural-primary', stdout=f)
            
            # Media files backup
            self.stdout.write('Backing up media files...')
            media_backup_dir = os.path.join(backup_dir, 'media')
            if os.path.exists(settings.MEDIA_ROOT):
                shutil.copytree(settings.MEDIA_ROOT, media_backup_dir)
            
            # Configuration backup
            self.stdout.write('Backing up configuration...')
            config_backup_dir = os.path.join(backup_dir, 'config')
            os.makedirs(config_backup_dir, exist_ok=True)
            
            # Copy important config files
            config_files = ['.env', 'requirements.txt']
            for config_file in config_files:
                src_path = os.path.join(settings.BASE_DIR, config_file)
                if os.path.exists(src_path):
                    dst_path = os.path.join(config_backup_dir, config_file)
                    shutil.copy2(src_path, dst_path)
            
            # Compress if requested
            if options['compress']:
                self.stdout.write('Compressing backup...')
                archive_path = f"{backup_dir}.tar.gz"
                shutil.make_archive(backup_dir, 'gztar', backup_dir)
                shutil.rmtree(backup_dir)
                backup_path = archive_path
            else:
                backup_path = backup_dir
            
            # Upload to S3 if requested
            if options['upload_to_s3']:
                self.stdout.write('Uploading to S3...')
                self._upload_to_s3(backup_path, timestamp)
            
            self.stdout.write(
                self.style.SUCCESS(f'Backup completed successfully: {backup_path}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Backup failed: {str(e)}')
            )
            logger.error(f"Backup failed: {str(e)}")

    def _upload_to_s3(self, backup_path, timestamp):
        """Upload backup to S3"""
        try:
            s3_client = boto3.client('s3')
            bucket_name = settings.BACKUP_S3_BUCKET
            
            if os.path.isfile(backup_path):
                # Single file upload
                key = f"backups/{timestamp}/{os.path.basename(backup_path)}"
                s3_client.upload_file(backup_path, bucket_name, key)
            else:
                # Directory upload
                for root, dirs, files in os.walk(backup_path):
                    for file in files:
                        local_path = os.path.join(root, file)
                        relative_path = os.path.relpath(local_path, backup_path)
                        s3_key = f"backups/{timestamp}/{relative_path}"
                        s3_client.upload_file(local_path, bucket_name, s3_key)
            
            self.stdout.write('S3 upload completed successfully')
            
        except ClientError as e:
            self.stdout.write(f'S3 upload failed: {str(e)}')