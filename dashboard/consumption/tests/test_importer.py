# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import os

from django.db import connection
from django.conf import settings

from consumption.models import User
from consumption.models import ElectricityConsumption
from consumption.models import EConsumptionDayAggregation
from consumption.models import UserEConsumptionDayAggregation
from consumption.tests.base import TestBase

class TestImporter(TestBase):

    NUM_OF_USERS = 5
    NUM_OF_CONSUMPTIONS = 100000
    USER_CSV_PATH = os.path.join(settings.BASE_DIR, './consumption/tests/data/user_data.csv')
    ELECTRICITY_CONSUMPTION_CSV_DIR = os.path.join(settings.BASE_DIR, './consumption/tests/data/consumption/')

    def setUp(self):
        User.objects.all().delete()
        ElectricityConsumption.objects.all().delete()

        print("Making test csv files")
        if not os.path.exists(os.path.dirname(self.USER_CSV_PATH)):
            os.makedirs(os.path.dirname(self.USER_CSV_PATH))
        data_frame = self.get_random_user_dataframe(self.NUM_OF_USERS)
        user_ids = list(data_frame['user_id'])
        data_frame = data_frame.rename(columns = {'user_id': 'id'})
        data_frame.to_csv(self.USER_CSV_PATH, index=False)

        if not os.path.exists(self.ELECTRICITY_CONSUMPTION_CSV_DIR):
            os.makedirs(self.ELECTRICITY_CONSUMPTION_CSV_DIR)
        for user_id in user_ids:
            print(user_id)
            data_frame = self.get_random_consumption_dataframe(self.NUM_OF_CONSUMPTIONS, user_id)
            data_frame.to_csv(
                os.path.join(self.ELECTRICITY_CONSUMPTION_CSV_DIR, str(user_id) + '.csv'),
                index=False
            )


    def test_importer(self):
        pass