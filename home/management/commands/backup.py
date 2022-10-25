import datetime
from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        backup_name = "db_backup_" + datetime.datetime.now().strftime("%m_%d_%Y") + ".json"
        management.call_command("dumpdata", output=backup_name, use_natural_foreign_keys=True,
                                exclude=["contenttypes", "auth.permission"], format="json")
