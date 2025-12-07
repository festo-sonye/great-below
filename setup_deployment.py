#!/usr/bin/env python
"""
Quick setup script for Great Below deployment
Run: python setup_deployment.py
"""

import os
import sys
from pathlib import Path
from django.core.management.utils import get_random_secret_key

def generate_secret_key():
    """Generate a strong Django SECRET_KEY"""
    return get_random_secret_key()

def create_env_file():
    """Create .env file from example"""
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if env_file.exists():
        print("✓ .env file already exists")
        return
    
    if env_example.exists():
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✓ .env file created from .env.example")
    else:
        print("✗ .env.example not found")

def main():
    print("\n" + "="*50)
    print("Great Below - Deployment Setup")
    print("="*50 + "\n")
    
    # Generate SECRET_KEY
    secret_key = generate_secret_key()
    print("Generated SECRET_KEY:")
    print(f"  {secret_key}\n")
    print("⚠️  Copy this and paste into your .env file as SESSION_SECRET\n")
    
    # Create .env
    print("Creating .env file...")
    create_env_file()
    
    print("\n" + "="*50)
    print("Next Steps:")
    print("="*50)
    print("""
1. Update .env with your values:
   - Paste the SECRET_KEY above
   - Set DEBUG=False
   - Add your database URL
   - Configure other settings

2. Push to GitHub:
   git add .
   git commit -m "Deployment setup"
   git push

3. Deploy on Render.com:
   - Connect GitHub repo
   - Create Web Service
   - Add environment variables
   - Deploy!

4. Create admin user after deployment:
   python manage.py createsuperuser

For detailed instructions, see RENDER_DEPLOYMENT.md
    """)
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
