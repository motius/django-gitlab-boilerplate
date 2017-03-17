from time import sleep

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.utils import ConnectionDoesNotExist, OperationalError


class Command(BaseCommand):
    help = 'Returns when database is ready'

    def add_arguments(self, parser):
        parser.add_argument('--database',
                            action='store',
                            dest='database',
                            default='default',
                            help='Database connection name')
        parser.add_argument('--retries',
                            action='store',
                            dest='retries',
                            type=int,
                            default=20,
                            help='Number of retries')
        parser.add_argument('--sleep-time',
                            action='store',
                            dest='sleep_time',
                            type=int,
                            default=5,
                            help='Seconds between retries')

    def handle(self, *args, **options):
        try:
            connection = connections[options['database']]
        except ConnectionDoesNotExist:
            raise CommandError('Database "%s" does not exist in settings' % options['database'])

        for i in range(0, options['retries']):
            try:
                connection.cursor()
            except OperationalError:
                i += 1
                self.stdout.write('{} / {}: Waiting for database...'.format(i, options['retries']))
                sleep(options['sleep_time'])
            else:
                self.stdout.write(self.style.SUCCESS('Successfully connected to database'))
                return

        raise CommandError('Number of retries reached, exiting')
