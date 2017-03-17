import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.utils import ConnectionDoesNotExist


class Command(BaseCommand):
    help = 'Recreates the database'

    def add_arguments(self, parser):
        parser.add_argument('--database',
                            action='store',
                            dest='database',
                            default='default',
                            help='Database connection name')

    def handle(self, *args, **options):
        try:
            connection = connections[options['database']]
            cursor = connection.cursor()
            database_settings = settings.DATABASES[options['database']]
        except ConnectionDoesNotExist:
            raise CommandError('Database "%s" does not exist in settings' % options['database'])

        if connection.vendor == 'sqlite':
            print("Deleting database %s" % database_settings['NAME'])
            os.remove(database_settings['NAME'])
        elif connection.vendor == 'mysql':
            print("Dropping database %s" % database_settings['NAME'])
            cursor.execute("DROP DATABASE `%s`;" % database_settings['NAME'])

            print("Creating database %s" % database_settings['NAME'])
            cursor.execute("CREATE DATABASE `%s` CHARACTER SET utf8;" % database_settings['NAME'])
            # Should fix some "MySQL has gone away issues"
            cursor.execute("SET GLOBAL max_allowed_packet=32*1024*1024;")
        elif connection.vendor == 'postgresql':
            print("Dropping and recreating schema public")
            cursor.execute("DROP schema public CASCADE; CREATE schema public")
        else:
            raise CommandError('Database vendor not supported')
