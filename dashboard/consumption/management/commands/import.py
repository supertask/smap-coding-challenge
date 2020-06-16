import os
import sys
import csv
import time
import pytz
from decimal import Decimal
from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm
from django.conf import settings
from django.core import exceptions
from django.core.management.base import BaseCommand
from django.utils.timezone import datetime

from consumption.models import User
from consumption.models import ElectricityConsumption
from consumption.models import EConsumptionDayAggregation
from consumption.models import UserEConsumptionDayAggregation

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

        # NOTE(Tasuku): If this command is executed as a batch or
        # the machine has enough CPU cores and RAM, you shoud increate this rate.
        self.concurrent_exec_users_len = 10

    def handle(self, *args, **options):
        """Imports user and consumption csv into database(db.sqlite3)
        """

        if settings.DEBUG:
            User.objects.all().delete()
            ElectricityConsumption.objects.all().delete()
            UserEConsumptionDayAggregation.objects.all().delete()
            EConsumptionDayAggregation.objects.all().delete()

        print("Reading a user csv file...")
        self.import_user_csv()
        print("Putting electricity consumption csv files into DB...")
        self.import_electricity_consumption_csv()

        print("Aggregating total and average electricity consumptions on each user...")
        UserEConsumptionDayAggregation.calc_consumptions()
        print("Aggregating total and average electricity consumptions for all users...")
        EConsumptionDayAggregation.calc_consumptions()
        print("Successfully imported all csv files!")

    def import_user_csv(self):
        """Import user csv.
        """
        if not os.path.exists(settings.USER_CSV_PATH):
            # TODO(Tasuku): Should have logging
            print('ERROR: the filename "%s" does not exist.' % settings.USER_CSV_PATH, file=sys.stderr)
            sys.exit(settings.EXIT_FAILURE)

        data_frame = pd.read_csv(settings.USER_CSV_PATH, sep=settings.CSV_SEPARATION_CHAR)
        User.objects.bulk_create(
            [
                User(user_id=int(row['id']), area=row['area'], tariff=row['tariff'])
                for row in data_frame.to_dict('records')
            ]
        )

    def import_electricity_consumption_csv(self):
        """Import electricity consumption csv.
        """
        users = User.objects.all()
        for i in tqdm(range(0, len(users), self.concurrent_exec_users_len)):
            with Pool(os.cpu_count()) as pool:
                data_frame = pd.concat(pool.map(read_csv_concurrently, users[i : i + self.concurrent_exec_users_len]))

            # OPTIMIZE(Tasuku): Consider RAM when num of users is increased. And test huge datasets over and over
            # NOTE(Tasuku): Both of creating the list bellow and saving the list on DB(bulk_create) will take a time to exec
            e_consumptions = [
                ElectricityConsumption(
                    datetime = pytz.utc.localize(
                        datetime.strptime(row['datetime'], settings.CSV_DATETIME_FORMAT)
                    ),
                    consumption = Decimal(row['consumption']), user_id = int(row['user_id'])
                )
                for row in data_frame.to_dict('records')
            ]
            ElectricityConsumption.objects.bulk_create(e_consumptions)

