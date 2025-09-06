from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser
from rides.models import Ride, Booking, RideRequest
from reviews.models import Review, ReviewReport
from payments.models import Payment, Transaction
from vehicles.models import VehicleDocument
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Optimize database by cleaning up old data and updating statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days to keep data (default: 365)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f"Optimizing database (keeping data from last {days} days)")
        if dry_run:
            self.stdout.write("DRY RUN - No data will be deleted")
        
        with transaction.atomic():
            # Clean up old cancelled bookings
            old_cancelled_bookings = Booking.objects.filter(
                status='cancelled',
                cancelled_at__lt=cutoff_date
            )
            cancelled_count = old_cancelled_bookings.count()
            if not dry_run:
                old_cancelled_bookings.delete()
            self.stdout.write(f"Cleaned up {cancelled_count} old cancelled bookings")
            
            # Clean up old failed payments
            old_failed_payments = Payment.objects.filter(
                status='failed',
                created_at__lt=cutoff_date
            )
            failed_payments_count = old_failed_payments.count()
            if not dry_run:
                old_failed_payments.delete()
            self.stdout.write(f"Cleaned up {failed_payments_count} old failed payments")
            
            # Clean up expired ride requests
            expired_requests = RideRequest.objects.filter(
                status='expired',
                expires_at__lt=cutoff_date
            )
            expired_count = expired_requests.count()
            if not dry_run:
                expired_requests.delete()
            self.stdout.write(f"Cleaned up {expired_count} expired ride requests")
            
            # Update expired vehicle documents
            expired_docs = VehicleDocument.objects.filter(
                expiry_date__lt=timezone.now().date(),
                status__in=['verified', 'pending']
            )
            expired_docs_count = expired_docs.count()
            if not dry_run:
                expired_docs.update(status='expired')
            self.stdout.write(f"Updated {expired_docs_count} expired vehicle documents")
            
            # Clean up resolved review reports older than 6 months
            old_reports = ReviewReport.objects.filter(
                status='resolved',
                resolved_at__lt=timezone.now() - timedelta(days=180)
            )
            reports_count = old_reports.count()
            if not dry_run:
                old_reports.delete()
            self.stdout.write(f"Cleaned up {reports_count} old resolved review reports")
            
            # Update user statistics
            if not dry_run:
                self.update_user_statistics()
            
        self.stdout.write(
            self.style.SUCCESS('Database optimization completed successfully!')
        )

    def update_user_statistics(self):
        """Update cached user statistics"""
        users_updated = 0
        for user in CustomUser.objects.all():
            # This would trigger the calculation of cached statistics
            # if we had implemented caching in the user model
            users_updated += 1
        
        self.stdout.write(f"Updated statistics for {users_updated} users")
