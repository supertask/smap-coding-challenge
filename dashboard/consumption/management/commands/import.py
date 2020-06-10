import os
import sys
import csv
from datetime import datetime

from django.conf import settings
from django.core import exceptions
from django.core.management.base import BaseCommand

from consumption.models import User, ElectricityConsumption

class Command(BaseCommand):
    help = 'Try on "python manage.py import"'

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        """Imports user and consumption csv into database(db.sqlite3)
        """
        User.objects.all().delete()
        ElectricityConsumption.objects.all().delete()

        user = User()
        user.user_id = 2
        user.area = "a1"
        user.tariff = "t2"
        user.save()
        e_consumption = ElectricityConsumption()
        e_consumption.datetime = datetime.strptime('2016-07-15 02:00:00', settings.CSV_DATETIME_FORMAT)
        e_consumption.consumption = 28.2
        e_consumption.user_id = user.user_id
        e_consumption.save()

        e_consumption = ElectricityConsumption()
        e_consumption.datetime = datetime.strptime('2016-07-20 14:00:00', settings.CSV_DATETIME_FORMAT)
        e_consumption.consumption = 14.7
        e_consumption.user_id = user.user_id
        e_consumption.save()
        #print(user)
        #print(e_consumption)

        records = ElectricityConsumption.objects.select_related('user').filter(consumption__gt=15)
        for r in records:
            print(r)

        return

        #
        # Imports User csv
        #
        user_csv_path = os.path.join(settings.BASE_DIR, settings.USER_CSV_PATH)
        with open(user_csv_path, 'r') as rf:
            reader = csv.DictReader(rf)
            for row in reader:
                #print(row['id'], row['area'], row['tariff'])
                row = self.format_user_row(row)
                user = User()
                user.user_id = row['id']
                user.area = row['area']
                user.tariff = row['tariff']
                user.save()

        #
        # Imports Consumption csv
        #
        ec_csv_dir = settings.ELECTRICITY_CONSUMPTION_CSV_DIR
        for name in os.listdir(ec_csv_dir):
            if os.path.isfile(os.path.join(ec_csv_dir, name)):
                filename_without_ext, _ = os.path.splitext(name)
                if filename_without_ext.isdigit():
                    #
                    # Start to read csv
                    #
                    user_id = int(filename_without_ext) #NOTE: user_id is validated on model
                    try:
                        user = User.objects.get(user_id=user_id)
                    except exceptions.ObjectDoesNotExist:
                        print("fail") #TODO: Write error logging
                        sys.exit(settings.EXIT_FAILURE)

                    with open(os.path.join(ec_csv_dir, name), 'r') as rf:
                        reader = csv.DictReader(rf)
                        for row in reader:
                            row = self.format_electricity_consumption_row(row)
                            e_consumption = ElectricityConsumption()
                            e_consumption.datetime = row['datetime']
                            e_consumption.consumption = row['consumption']
                            e_consumption.user_id = user.user_id
                            e_consumption.save()
                else:
                    #
                    # Put log if consumption dir has garbage files we haven't expected
                    #
                    # TODO(Tasuku): Should have logging
                    print('WARNING: the filename "%s".csv is not digit (Should be "<number>.csv").' % filename_without_ext)

    def format_user_row(self, *row):
        """Formats a row on a user table."""
        try:
            row['id'] = int(row['id'])
        except ValueError as e:
            # TODO(Tasuku): Should have logging
            print('The id is not integer (e.g. 3001). value: ' + row['datetime'], file=sys.stderr)
            sys.exit(settings.EXIT_FAILURE)
        return row
    
    def format_electricity_consumption_row(self, *row):
        """Formats a row on a electricity consumption table."""
        try:
            row['datetime'] = datetime.strptime(row['datetime'], settings.CSV_DATETIME_FORMAT)
        except ValueError as e:
            # TODO(Tasuku): Should have logging
            print('The datetime is not correct format (e.g. 2016-07-15 03:00:00). value: ' + row['datetime'], file=sys.stderr)
            sys.exit(settings.EXIT_FAILURE)
        return row
    