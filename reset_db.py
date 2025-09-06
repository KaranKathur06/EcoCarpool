#!/usr/bin/env python
"""
Script to reset the database and fix schema issues
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EcoCarpool.settings')
django.setup()

def reset_database():
    """Reset the database by deleting and recreating it"""
    import subprocess
    
    # Delete existing database
    db_path = BASE_DIR / 'db.sqlite3'
    if db_path.exists():
        db_path.unlink()
        print("✓ Deleted existing database")
    
    # Delete migration files (except __init__.py)
    apps = ['users', 'rides', 'vehicles', 'payments', 'reviews', 'dashboard']
    for app in apps:
        migrations_dir = BASE_DIR / app / 'migrations'
        if migrations_dir.exists():
            for file in migrations_dir.glob('*.py'):
                if file.name != '__init__.py':
                    file.unlink()
                    print(f"✓ Deleted {file}")
    
    # Create fresh migrations
    print("\n📝 Creating fresh migrations...")
    subprocess.run([sys.executable, 'manage.py', 'makemigrations'], cwd=BASE_DIR)
    
    # Apply migrations
    print("\n🔄 Applying migrations...")
    subprocess.run([sys.executable, 'manage.py', 'migrate'], cwd=BASE_DIR)
    
    print("\n✅ Database reset complete!")
    print("Now you can run: python manage.py createsuperuser")
    print("Then: python manage.py runserver")

if __name__ == '__main__':
    reset_database()
