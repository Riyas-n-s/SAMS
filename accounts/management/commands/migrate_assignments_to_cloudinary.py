import os
from django.core.management.base import BaseCommand
from cloudinary.uploader import upload
from accounts.models import Assignment  # adjust if your model is in a different app
from django.conf import settings

class Command(BaseCommand):
    help = 'Migrate local assignment files to Cloudinary'

    def handle(self, *args, **kwargs):
        assignments = Assignment.objects.all()
        for assignment in assignments:
            if assignment.file and not assignment.file.url.startswith('http'):
                local_file_path = os.path.join(settings.BASE_DIR, 'media', assignment.file.name)
                if os.path.exists(local_file_path):
                    result = upload(local_file_path, folder='assignments')
                    assignment.file.name = result['public_id']
                    assignment.save()
                    self.stdout.write(self.style.SUCCESS(f"Uploaded {assignment.title} to Cloudinary"))
                else:
                    self.stdout.write(self.style.WARNING(f"File not found: {assignment.title}"))
        self.stdout.write(self.style.SUCCESS("All assignments migrated!"))
