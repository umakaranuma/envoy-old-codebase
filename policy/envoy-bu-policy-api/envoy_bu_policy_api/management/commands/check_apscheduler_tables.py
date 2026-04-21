"""
Management command to check APScheduler database tables
"""

from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check if APScheduler database tables exist'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check for APScheduler tables
            cursor.execute("SHOW TABLES LIKE 'django_apscheduler%'")
            tables = cursor.fetchall()
            
            self.stdout.write("=== APScheduler Database Tables Check ===")
            
            if tables:
                self.stdout.write(self.style.SUCCESS(f"✓ Found {len(tables)} APScheduler tables:"))
                for table in tables:
                    self.stdout.write(f"  - {table[0]}")
            else:
                self.stdout.write(self.style.ERROR("✗ No APScheduler tables found!"))
                self.stdout.write("This will cause scheduler issues.")
            
            # Check if tables have data
            if tables:
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    self.stdout.write(f"  - {table_name}: {count} records")
            
            # Check for required tables specifically
            required_tables = [
                'django_apscheduler_djangojob',
                'django_apscheduler_djangojobexecution'
            ]
            
            self.stdout.write("\n=== Required Tables Check ===")
            for table in required_tables:
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                exists = cursor.fetchone()
                if exists:
                    self.stdout.write(self.style.SUCCESS(f"✓ {table} exists"))
                else:
                    self.stdout.write(self.style.ERROR(f"✗ {table} MISSING"))
            
            if not all(cursor.execute(f"SHOW TABLES LIKE '{table}'") and cursor.fetchone() for table in required_tables):
                self.stdout.write(self.style.WARNING("\n⚠️  Missing required tables! Run: python manage.py migrate django_apscheduler"))
