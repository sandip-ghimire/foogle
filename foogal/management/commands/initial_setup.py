from django.core.management.base import BaseCommand
from foogal.models import Setting
from django.conf import settings


class Command(BaseCommand):
    help = 'Setup the application for use'

    def handle(self, *args, **options):
        try:
            Setting.objects.get_or_create(name=settings.DEFAULT_CONF_SETTING)
            Setting.objects.get_or_create(name=settings.LOCAL_LINK_SETTING)
            self.stdout.write(self.style.SUCCESS('Application initialization success'))
        except Exception as e:
            self.stdout.write(self.style.ERROR('Application initialization failed'))
