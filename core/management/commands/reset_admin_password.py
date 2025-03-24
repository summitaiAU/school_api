from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os
import sys

class Command(BaseCommand):
    help = 'Reset admin password from environment variable'

    def handle(self, *args, **options):
        # Try to get password from environment variable
        new_password = os.environ.get('ADMIN_PASSWORD', 'default_secure_password')
        
        try:
            # Try to get existing admin user
            user = User.objects.get(username='admin')
            user.set_password(new_password)
            user.save()
            self.stdout.write(self.style.SUCCESS('Admin password reset successfully'))
        except User.DoesNotExist:
            # Create a new admin user if it doesn't exist
            User.objects.create_superuser('admin', 'admin@example.com', new_password)
            self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
        
        # Print the password to stdout so it can be captured
        print(f"ADMIN_PASSWORD: {new_password}", file=sys.stderr)
