# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import os
import shutil

from django.conf import settings

from consumption.models import User
from consumption.models import ElectricityConsumption
from consumption.tests.test_aggregations import TestAggregations
from consumption.management.commands.importer import Command

class TestImporter(TestAggregations):

    TEST_USER_CSV_PATH = os.path.join(settings.BASE_DIR, './consumption/tests/data/user_data.csv')
    TEST_ELECTRICITY_CONSUMPTION_CSV_DIR = os.path.join(settings.BASE_DIR, './consumption/tests/data/consumption/')

    def setUp(self):
        User.objects.all().delete()
        ElectricityConsumption.objects.all().delete()

        user_csv_dir = os.path.dirname(self.TEST_USER_CSV_PATH)
        shutil.rmtree(user_csv_dir)
        os.makedirs(user_csv_dir)

        #
        # Make csv files
        #
        print()
        print("Making test csv files...")
        data_frame = self.get_random_user_dataframe(self.NUM_OF_USERS)
        user_ids = list(data_frame['user_id'])
        data_frame = data_frame.rename(columns = {'user_id': 'id'})
        data_frame.to_csv(self.TEST_USER_CSV_PATH, index=False)

        if not os.path.exists(self.TEST_ELECTRICITY_CONSUMPTION_CSV_DIR):
            os.makedirs(self.TEST_ELECTRICITY_CONSUMPTION_CSV_DIR)
        for user_id in user_ids:
            data_frame = self.get_random_consumption_dataframe(self.NUM_OF_CONSUMPTIONS, user_id)
            data_frame['datetime'] = data_frame['datetime'].astype(str).str[:-6] #Removes timezone
            del data_frame['user_id'] # Removes the column, user_id
            data_frame.to_csv(
                os.path.join(self.TEST_ELECTRICITY_CONSUMPTION_CSV_DIR, str(user_id) + '.csv'),
                index=False
            )

    def test_datasets(self):
        Command.user_csv_path = self.TEST_USER_CSV_PATH
        Command.electricity_consumption_csv_dir = self.TEST_ELECTRICITY_CONSUMPTION_CSV_DIR
        Command().handle() # Importer's command
        self.compare_all_aggregation()
        self.compare_user_aggregation()