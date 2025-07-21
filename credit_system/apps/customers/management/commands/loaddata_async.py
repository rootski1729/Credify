from django.core.management.base import BaseCommand
from apps.core.tasks import load_all_data


class Command(BaseCommand):
    help = 'Load customer and loan data from Excel files using background tasks'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting background data loading...'))
        
        task = load_all_data.delay()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Data loading task started with ID: {task.id}\n'
                'You can monitor the progress in Celery logs or Django admin.'
            )
        )