from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Student

class Command(BaseCommand):
    help = "Link all Students to User accounts only; do NOT create Profiles."

    def handle(self, *args, **kwargs):
        linked_users = 0
        for student in Student.objects.all():
            if not student.user:
                user, _ = User.objects.get_or_create(username=student.register_number)
                student.user = user
                student.save()  # triggers signal, but signal will skip if no Profile
                linked_users += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Linked {linked_users} Students to Users. Profiles will not be created."
        ))
