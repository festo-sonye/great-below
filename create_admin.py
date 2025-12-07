#!/usr/bin/env python
"""
Auto-create admin user if it doesn't exist
Run during deployment
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crochet_shop.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if admin already exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@greatbelow.com',
        password='Admin@123456'
    )
    print("✓ Admin user created successfully!")
    print("  Username: admin")
    print("  Password: Admin@123456")
else:
    print("✓ Admin user already exists")
