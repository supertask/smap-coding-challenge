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

def generate_e_consumption_concurrently(divided_data_frame):
    return [
        ElectricityConsumption(
            datetime=datetime.strptime(row['datetime'], settings.CSV_DATETIME_FORMAT),
            consumption = Decimal(row['consumption']), user_id = int(row['user_id'])
        )
        for row in divided_data_frame.to_dict('records')
    ]

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
        # Imports user csv.
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

        #NOTE: Muti-processing wth pandas https://qiita.com/hoto17296/items/586dc01aee69cd4915cc


        self.import_electricity_consumption_old()
        ElectricityConsumption.objects.all().delete()

        start = time.time()
        # Combine entire csv files into data_frame
        with Pool(os.cpu_count()) as pool:
            data_frame = pd.concat(pool.map(read_csv_concurrently, User.objects.all()))
        print("done 1")

        """
        start = time.time()
        divided_data_frames = Util.split_list(data_frame, self.dataframe_segument_len)
        print("done 2. time: %s" % elapsed_time)
        with Pool(os.cpu_count()) as pool:
            divided_e_consumptions = pool.map(generate_e_consumption_concurrently, divided_data_frames)
            print(len(divided_e_consumptions))
            print(type(divided_e_consumptions))
        elapsed_time = time.time() - start
        print("done 3. time: %s" % elapsed_time)
        """

        consumptions = [
            ElectricityConsumption(
                datetime=datetime.strptime(row['datetime'], settings.CSV_DATETIME_FORMAT),
                consumption = Decimal(row['consumption']), user_id = int(row['user_id'])
            )
            for row in data_frame.to_dict('records')
        ]
        ElectricityConsumption.objects.bulk_create(consumptions)
        #for i in tqdm(range(0, len(data_frame), self.dataframe_segument_len)):
        elapsed_time = time.time() - start
        print("done 3. time: %s" % elapsed_time)

        #start = time.time()
        #elapsed_time = time.time() - start
        #print("done 4. time: %s" % elapsed_time)

        #print (data_frame)
        print ("data_frame: %s" % len(data_frame))
        #print ("consumptions: %s" % len(consumptions))

        #
        # Imports consumption csv.
        #
        print("Reading electricity consumption csv files...")

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


    """
    def generate_consumptions_old(self):
        # Use this for comparing between ex implementation and current implementation
        start = time.time()
        consumptions = [
            ElectricityConsumption(
                datetime=datetime.strptime(row['datetime'], settings.CSV_DATETIME_FORMAT),
                consumption = Decimal(row['consumption']), user_id = int(row['user_id'])
            )
            for row in data_frame.to_dict('records')
        ]
        elapsed_time = time.time() - start
        print("done 2. time: %s" % elapsed_time)
        return consumptions
    """

    def import_electricity_consumption_old(self):
        start = time.time()
        for user in User.objects.all():
            consumption_csv_path = os.path.join(settings.ELECTRICITY_CONSUMPTION_CSV_DIR, str(user.user_id) + '.csv')

            if not os.path.exists(consumption_csv_path):
                print('WARNING: the filename "%s" does not exist.' % consumption_csv_path)
                continue

            #logging
            #print(consumption_csv_path) 

            data_frame = pd.read_csv(consumption_csv_path, sep=settings.CSV_SEPARATION_CHAR)
            ElectricityConsumption.objects.bulk_create(
                [
                    ElectricityConsumption(
                        datetime=datetime.strptime(row['datetime'], settings.CSV_DATETIME_FORMAT),
                        consumption = Decimal(row['consumption']), user_id = user.user_id
                    ) for row in data_frame.to_dict('records')
                ]
            )
        elapsed_time = time.time() - start
        print("done 4. time: %s" % elapsed_time)