from django.core.management.base import BaseCommand
from vehicles.models import VehicleCompany, VehicleModel
from django.db.models import Count

class Command(BaseCommand):
    help = 'Merge duplicate VehicleCompany entries by company_name.'

    def handle(self, *args, **options):
        duplicates = VehicleCompany.objects.values('company_name').annotate(count=Count('id')).filter(count__gt=1)
        total_merged = 0
        for entry in duplicates:
            name = entry['company_name']
            companies = VehicleCompany.objects.filter(company_name=name).order_by('id')
            main = companies.first()
            dups = companies.exclude(id=main.id)
            for dup in dups:
                updated = VehicleModel.objects.filter(company=dup).update(company=main)
                self.stdout.write(self.style.WARNING(f'Updated {updated} VehicleModel(s) from company {dup.id} to {main.id} ({name})'))
                dup.delete()
                self.stdout.write(self.style.ERROR(f'Deleted duplicate company: {dup.id} ({name})'))
                total_merged += 1
        if total_merged == 0:
            self.stdout.write(self.style.SUCCESS('No duplicate companies found.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Merged and deleted {total_merged} duplicate company entries.')) 