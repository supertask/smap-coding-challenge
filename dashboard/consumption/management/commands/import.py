import os
import sys
import csv
import time
from datetime import datetime
from decimal import Decimal
from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm

from django.conf import settings
from django.core import exceptions
from django.core.management.base import BaseCommand
from django.db.models import Avg, Sum

from consumption.models import User, ElectricityConsumption, ElectricityConsumptionAggregation
from consumption.util import Util

def read_csv_concurrently(user):
    csv_path = os.path.join(settings.ELECTRICITY_CONSUMPTION_CSV_DIR, str(user.user_id) + '.csv')
    if not os.path.exists(csv_path):
        print('WARNING: the filename "%s" does not exist.' % csv_path)
    df = pd.read_csv(csv_path)
    df['user_id'] = user.user_id
    return df

class Command(BaseCommand):
    help = 'Try on "python manage.py import"'

    def __init__(self):
        super(Command, self).__init__()
        self.dataframe_segument_len = 40000

    def handle(self, *args, **options):
        """Imports user and consumption csv into database(db.sqlite3)
        """
        if settings.DEBUG:
            User.objects.all().delete()
            ElectricityConsumption.objects.all().delete()

        #
        # Import user csv.
        #
        print("Reading a user csv file...")
        if not os.path.exists(settings.USER_CSV_PATH):
            #TODO(Tasuku): Should have logging
            print('ERROR: the filename "%s" does not exist.' % settings.USER_CSV_PATH, file=sys.stderr)
            sys.exit(settings.EXIT_FAILURE)

        data_frame = pd.read_csv(settings.USER_CSV_PATH, sep=settings.CSV_SEPARATION_CHAR)
        User.objects.bulk_create(
            [
                User(user_id=int(row['id']), area=row['area'], tariff=row['tariff'])
                for row in data_frame.to_dict('records')
            ]
        )

        #
        # Import electricity consumption csv.
        #
        print("Reading electricity consumption csv files...")
        with Pool(os.cpu_count()) as pool:
            data_frame = pd.concat(pool.map(read_csv_concurrently, User.objects.all()))

        print("Creating a list of ElectricityConsumption..")
        e_consumptions = [
            ElectricityConsumption(
                datetime=datetime.strptime(row['datetime'], settings.CSV_DATETIME_FORMAT),
                consumption = Decimal(row['consumption']), user_id = int(row['user_id'])
            )
            for row in data_frame.to_dict('records')
        ]

        print("Saving a list of ElectricityConsumption on DB..")
        ElectricityConsumption.objects.bulk_create(e_consumptions)

        #
        # Puts total and average electricity consumption into the table.
        #
        print("Aggregating total and average electricity consumptions...")
        self.calc_consumptions()

        print("Successfully imported all csv files!")

    def calc_consumptions(self):

        #NOTE: https://narito.ninja/blog/detail/84/
        tmp = ElectricityConsumption.objects.annotate(total_consumption=Sum('consumption'))
        #print(tmp)

