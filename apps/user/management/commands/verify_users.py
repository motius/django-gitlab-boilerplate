from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from allauth.account.models import EmailAddress


class Command(BaseCommand):
    help = 'Verify all users\'s email addresses'

    def handle(self, *args, **options):
        EmailAddress.objects.all().delete()
        users = get_user_model().objects.exclude(email__isnull=True, emailaddress__isnull=False)
        emails = []
        for user in users:
            emails.append(EmailAddress(user=user, email=user.email, verified=True, primary=True))
        EmailAddress.objects.bulk_create(emails, batch_size=200)
        self.stdout.write("Verified %i email addresses.\n" % len(emails))
