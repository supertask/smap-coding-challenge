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
from django.db.models import Avg, Sum
from django.db.models.functions import TruncMonth, TruncDay
from django.utils.timezone import datetime

from consumption.models import User, ElectricityConsumption, ElectricityConsumptionDayAggregation
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

        # NOTE(Tasuku): If this command is executed as a batch or
        # the machine has enough CPU cores and RAM, you shoud increate this rate.
        self.concurrent_exec_users_len = 10

    def handle(self, *args, **options):
        """Imports user and consumption csv into database(db.sqlite3)
        """

        if settings.DEBUG:
            User.objects.all().delete()
            ElectricityConsumption.objects.all().delete()

        print("Reading a user csv file...")
        self.import_user_csv()
        print("Putting electricity consumption csv files into DB...")
        self.import_electricity_consumption_csv()

        print("Aggregating total and average electricity consumptions...")
        self.calc_consumptions()
        print("Successfully imported all csv files!")

    def import_user_csv(self):
        """Import user csv.
        """
        if not os.path.exists(settings.USER_CSV_PATH):
            #TODO(Tasuku): Should have logging
            print('ERROR: the filename "%s" does not exist.' % settings.USER_CSV_PATH, file=sys.stderr)
            sys.exit(settings.EXIT_FAILURE)

        data_frame = pd.read_csv(settings.USER_CSV_PATH, sep=settings.CSV_SETTING['SEPARATION_CHAR'])
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

            #NOTE(Tasuku): Both of creating the list bellow and saving the list on DB(bulk_create) will take a time to exec
            e_consumptions = [
                ElectricityConsumption(
                    datetime = pytz.utc.localize(
                        datetime.strptime(row['datetime'], settings.CSV_SETTING['COMSUMPTION']['DATETIME_FORMAT'])
                    ),
                    consumption = Decimal(row['consumption']), user_id = int(row['user_id'])
                )
                for row in data_frame.to_dict('records')
            ]
            ElectricityConsumption.objects.bulk_create(e_consumptions)

    def calc_consumptions(self):
        """Calc and put total and average electricity consumption into DB."""

        #
        # OPTIMIZE(Tasuku): Consider RAM when num of users are increased
        #
        # NOTE(Tasuku): a statement on SQLite
        # SELECT day, SUM(consumption), AVG(consumption) FROM(
        #    SELECT DATE(datetime) as day, consumption FROM consumption_electricityconsumption
        # ) GROUP BY day;
        day_consumption_aggregation = ElectricityConsumption.objects.annotate(day=TruncDay('datetime'))\
                .values('day').annotate(day_total=Sum('consumption')).annotate(day_average=Avg('consumption'))
        data_frame = pd.DataFrame.from_records(day_consumption_aggregation)
        ElectricityConsumptionDayAggregation.objects.bulk_create(
            [
                ElectricityConsumptionDayAggregation(day=row['day'], day_total=row['day_total'], day_average=row['day_average'])
                for row in data_frame.to_dict('records')
            ]
        )

