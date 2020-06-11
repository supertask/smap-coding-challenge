import os
import sys
import csv
import pandas as pd
from datetime import datetime
from decimal import Decimal
from tqdm import tqdm

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
        if settings.DEBUG:
            User.objects.all().delete()
            ElectricityConsumption.objects.all().delete()

        #
        # Imports user csv.
        #
        print("Reading a user csv file...")
        if not os.path.exists(settings.USER_CSV_PATH):
            #TODO(Tasuku): Should have logging
            print('ERROR: the filename "%s" does not exist.' % settings.USER_CSV_PATH)
            sys.exit(settings.EXIT_FAILURE)

        df = pd.read_csv(settings.USER_CSV_PATH, sep=',')
        User.objects.bulk_create(
            [
                User(user_id=int(row['id']), area=row['area'], tariff=row['tariff'])
                for i, row in df.iterrows()
            ]
        )

        #
        # Imports consumption csv.
        #
        print("Reading electricity consumption csv files...")
        for user in tqdm(User.objects.all()):
            consumption_csv_path = os.path.join(settings.ELECTRICITY_CONSUMPTION_CSV_DIR, str(user.user_id) + '.csv')

            if not os.path.exists(consumption_csv_path):
                print('WARNING: the filename "%s" does not exist.' % consumption_csv_path)
                continue

            #logging
            #print(consumption_csv_path) 

            df = pd.read_csv(consumption_csv_path, sep=',')
            
            ElectricityConsumption.objects.bulk_create(
                [
                    ElectricityConsumption(
                        datetime=datetime.strptime(row['datetime'], settings.CSV_DATETIME_FORMAT),
                        consumption = Decimal(row['consumption']), user_id = user.user_id
                    ) for i, row in df.iterrows()
                ]
            )

        #
        # Puts total and average electricity consumption into the table.
        #
        print("Aggregating total and average electricity consumptions...")
        #ElectricityConsumptionAggregation

        print("Successfully imported all csv files!")
