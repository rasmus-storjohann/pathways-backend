from django.core.management.base import BaseCommand
from bc211.importer import read_records_from_file, save_records_to_database

# invoke as follows:
# python manage.py import_bc211_data path/to/bc211.xml

class Command(BaseCommand):
    help = 'Import BC-211 data from XML file'

    def add_arguments(self, parser):
        parser.add_argument('file', metavar='file', help='Path to XML file containing BC-211 data')

    def handle(self, *args, **options):
        path = options['file']
        records = read_records_from_file(path)
        save_records_to_database(records)

        record_count = len(records)
        status_message = 'Successfully imported {0} record(s)'.format(record_count)
        self.stdout.write(self.style.SUCCESS(status_message))
