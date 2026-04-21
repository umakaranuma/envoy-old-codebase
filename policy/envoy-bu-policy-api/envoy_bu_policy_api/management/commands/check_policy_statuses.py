from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from datetime import datetime, date

class Command(BaseCommand):
    help = 'Check current policy status distribution and identify issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed breakdown of policies by status'
        )

    def handle(self, *args, **options):
        detailed = options['detailed']
        
        self.stdout.write(self.style.SUCCESS('=== Policy Status Analysis ==='))
        
        with connection.cursor() as cursor:
            # Check if required statuses exist
            self.stdout.write('\n1. Checking required statuses...')
            cursor.execute("""
                SELECT name, id, description 
                FROM core_status 
                WHERE module = 'policy' 
                AND type IN ('policy_active', 'pol_due_renewal', 'policy_expired', 'policy_renewed')
                ORDER BY name
            """)
            
            statuses = cursor.fetchall()
            if statuses:
                for status in statuses:
                    self.stdout.write(f"   ✓ {status[0]} (ID: {status[1]}) - {status[2]}")
            else:
                self.stdout.write(self.style.ERROR("   ✗ No policy statuses found!"))
            
            # Current status distribution
            self.stdout.write('\n2. Current status distribution...')
            cursor.execute("""
                SELECT 
                    COALESCE(cs.name, 'NULL') as status_name,
                    COUNT(*) as count,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM crmp_policy_base), 2) as percentage
                FROM crmp_policy_base pb
                LEFT JOIN core_status cs ON pb.status_id = cs.id
                GROUP BY cs.name
                ORDER BY count DESC
            """)
            
            status_dist = cursor.fetchall()
            for status in status_dist:
                self.stdout.write(f"   {status[0]}: {status[1]} policies ({status[2]}%)")
            
            # Policies that should be EXPIRED but aren't
            self.stdout.write('\n3. Policies that should be EXPIRED...')
            cursor.execute("""
                SELECT 
                    COUNT(*) as should_be_expired,
                    COUNT(CASE WHEN cs.type = 'policy_expired' THEN 1 END) as already_expired,
                    COUNT(CASE WHEN cs.type != 'policy_expired' OR cs.type IS NULL THEN 1 END) as need_update
                FROM crmp_policy_base pb
                LEFT JOIN core_status cs ON pb.status_id = cs.id
                WHERE pb.policy_expiry_date < CURDATE()
            """)
            
            expired_data = cursor.fetchone()
            if expired_data[0] > 0:
                self.stdout.write(f"   Total policies past expiry: {expired_data[0]}")
                self.stdout.write(f"   Already marked EXPIRED: {expired_data[1]}")
                self.stdout.write(f"   Need to update to EXPIRED: {expired_data[2]}")
                
                if expired_data[2] > 0:
                    self.stdout.write(self.style.WARNING(f"   ⚠️  {expired_data[2]} policies need EXPIRED status update"))
            else:
                self.stdout.write("   No policies past their expiry date")
            
            # Policies that should be DUE_FOR_RENEWAL but aren't
            self.stdout.write('\n4. Policies that should be DUE_FOR_RENEWAL...')
            cursor.execute("""
                SELECT 
                    COUNT(*) as should_be_due_renewal,
                    COUNT(CASE WHEN cs.type = 'pol_due_renewal' THEN 1 END) as already_due_renewal,
                    COUNT(CASE WHEN cs.type != 'pol_due_renewal' OR cs.type IS NULL THEN 1 END) as need_update
                FROM crmp_policy_base pb
                LEFT JOIN core_status cs ON pb.status_id = cs.id
                WHERE pb.policy_expiry_date >= CURDATE()
                  AND DATE_SUB(pb.policy_expiry_date, INTERVAL 30 DAY) <= CURDATE()
            """)
            
            due_renewal_data = cursor.fetchone()
            if due_renewal_data[0] > 0:
                self.stdout.write(f"   Total policies due for renewal: {due_renewal_data[0]}")
                self.stdout.write(f"   Already marked DUE_FOR_RENEWAL: {due_renewal_data[1]}")
                self.stdout.write(f"   Need to update to DUE_FOR_RENEWAL: {due_renewal_data[2]}")
                
                if due_renewal_data[2] > 0:
                    self.stdout.write(self.style.WARNING(f"   ⚠️  {due_renewal_data[2]} policies need DUE_FOR_RENEWAL status update"))
            else:
                self.stdout.write("   No policies due for renewal (within 30 days)")
            
            # Recent updates (check if there are any status changes)
            self.stdout.write('\n5. Recent status updates...')
            cursor.execute("""
                SELECT 
                    COUNT(*) as recent_updates
                FROM crmp_policy_base 
                WHERE status_id IS NOT NULL
            """)
            
            recent_updates = cursor.fetchone()[0]
            self.stdout.write(f"   Policies with status set: {recent_updates}")
            
            # Check if we have any NULL statuses that should be updated
            cursor.execute("""
                SELECT COUNT(*) as null_statuses
                FROM crmp_policy_base 
                WHERE status_id IS NULL
            """)
            
            null_statuses = cursor.fetchone()[0]
            if null_statuses > 0:
                self.stdout.write(self.style.WARNING(f"   ⚠️  {null_statuses} policies have NULL status - may need task execution"))
            
            # Show detailed breakdown if requested
            if detailed:
                self.stdout.write('\n6. Detailed breakdown...')
                
                # Show some examples of policies that need updates
                cursor.execute("""
                    SELECT 
                        pb.id,
                        pb.policy_expiry_date,
                        COALESCE(cs.name, 'NULL') as current_status,
                        DATEDIFF(NOW(), pb.policy_expiry_date) as days_expired,
                        pb.policy_start_date
                    FROM crmp_policy_base pb
                    LEFT JOIN core_status cs ON pb.status_id = cs.id
                    WHERE pb.policy_expiry_date < CURDATE()
                      AND (cs.type != 'policy_expired' OR cs.type IS NULL)
                    ORDER BY pb.policy_expiry_date DESC
                    LIMIT 5
                """)
                
                expired_examples = cursor.fetchall()
                if expired_examples:
                    self.stdout.write('\n   Examples of policies that should be EXPIRED:')
                    for policy in expired_examples:
                        self.stdout.write(f"     ID {policy[0]}: Expired {policy[3]} days ago, Status: {policy[2]}")
                
                cursor.execute("""
                    SELECT 
                        pb.id,
                        pb.policy_expiry_date,
                        COALESCE(cs.name, 'NULL') as current_status,
                        DATEDIFF(pb.policy_expiry_date, NOW()) as days_until_expiry,
                        pb.policy_start_date
                    FROM crmp_policy_base pb
                    LEFT JOIN core_status cs ON pb.status_id = cs.id
                    WHERE pb.policy_expiry_date >= CURDATE()
                      AND DATE_SUB(pb.policy_expiry_date, INTERVAL 30 DAY) <= CURDATE()
                      AND (cs.type != 'pol_due_renewal' OR cs.type IS NULL)
                    ORDER BY pb.policy_expiry_date ASC
                    LIMIT 5
                """)
                
                due_renewal_examples = cursor.fetchall()
                if due_renewal_examples:
                    self.stdout.write('\n   Examples of policies that should be DUE_FOR_RENEWAL:')
                    for policy in due_renewal_examples:
                        self.stdout.write(f"     ID {policy[0]}: Expires in {policy[3]} days, Status: {policy[2]}")
        
        self.stdout.write('\n=== Recommendations ===')
        
        if expired_data and expired_data[2] > 0 or due_renewal_data and due_renewal_data[2] > 0:
            self.stdout.write('1. Run the policy status update task manually:')
            self.stdout.write('   python manage.py test_celery_tasks --task=test-direct')
            self.stdout.write('')
            self.stdout.write('2. Check if Celery Beat is running:')
            self.stdout.write('   ps aux | grep celery')
            self.stdout.write('')
            self.stdout.write('3. Consider using Kubernetes CronJob instead of Celery Beat')
        else:
            self.stdout.write('✓ All policies appear to have correct statuses')
            self.stdout.write('✓ The task may be working correctly')
            
        self.stdout.write('\n=== Next Steps ===')
        self.stdout.write('1. Run: python manage.py test_celery_tasks --task=test-direct')
        self.stdout.write('2. Check application logs for task execution messages')
        self.stdout.write('3. Verify Celery Beat is running in production')
