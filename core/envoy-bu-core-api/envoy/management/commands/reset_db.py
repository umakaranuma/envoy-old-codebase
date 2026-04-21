from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Drop all tables from the database'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")  # Disable foreign key checks
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE();")
            tables = cursor.fetchall()
            for table in tables:
                self.stdout.write(f"Dropping table {table[0]}")
                cursor.execute(f"DROP TABLE `{table[0]}`;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  # Re-enable foreign key checks
        self.stdout.write(self.style.SUCCESS("All tables dropped successfully!"))
