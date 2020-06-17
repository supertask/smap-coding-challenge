# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import random
import math 
from enum import IntEnum
from enum import auto
import decimal
from decimal import Decimal

from tqdm import tqdm
from django.test import TestCase
from django.db import connection

from consumption.models import User
from consumption.models import ElectricityConsumption
from consumption.models import EConsumptionDayAggregation
from consumption.models import UserEConsumptionDayAggregation
from consumption.tests.base import TestBase

class TestAggregations(TestBase):
    def setUp(self):
        User.objects.all().delete()
        ElectricityConsumption.objects.all().delete()

        #print(User.objects.all())

    def test_aggregations(self):
        print("Making random users...")
        user_ids = self.make_user_datasets(3)

        print("Making random consumptions...")
        for user_id in user_ids:
            data_frame = self.get_random_consumption_dataframe(100000, user_id)

            ElectricityConsumption.objects.bulk_create(
                [ ElectricityConsumption(**row) for row in data_frame.to_dict('records') ]
            )
        EConsumptionDayAggregation.calc_consumptions()
        UserEConsumptionDayAggregation.calc_consumptions()

        cursor = connection.cursor()
        cursor.execute("""
            SELECT day, SUM(consumption) as day_total, AVG(consumption) as day_average FROM(
                SELECT DATE(datetime) as day, consumption FROM consumption_electricityconsumption
            ) GROUP BY day ORDER BY day;
        """) #TODO(Tasuku): Call a db name from a model
        rows = cursor.fetchall()
        testing_rows = EConsumptionDayAggregation.objects.order_by('day').all().values()
        for row, testing_row in zip(rows, list(testing_rows)):
            self.assertEqual(row[0], testing_row['day'].strftime('%Y-%m-%d'))

            # WARNING(Tasuku): I guess the way of rounding between Django's decimal & Sql decimal is different. So I used isclose
            # This might be a hint, https://github.com/django/django/blob/master/django/forms/fields.py
            self.assertTrue(math.isclose(Decimal(row[1]), testing_row['day_total'], rel_tol=1e-10) )
            self.assertTrue(math.isclose(Decimal(row[2]), testing_row['day_average'], rel_tol=1e-10) )


        #TODO(Tasuku): Do it from here

        cursor = connection.cursor()
        cursor.execute("""
            SELECT day, user_id, SUM(consumption) as day_total, AVG(consumption) as day_average FROM(
                SELECT DATE(datetime) as day, user_id, consumption FROM consumption_electricityconsumption
            ) GROUP BY day, user_id;
        """) #TODO(Tasuku): Call a db name from a model
        rows = cursor.fetchall()
        testing_rows = UserEConsumptionDayAggregation.objects.order_by('day').all().values()

        for row, testing_row in zip(rows, list(testing_rows)):
            print(row, testing_row)
            break
            self.assertEqual(row[0], testing_row['day'].strftime('%Y-%m-%d'))

            # WARNING(Tasuku): I guess rounding between Django's decimal & Sql decimal is different. So I used isclose
            #self.assertTrue(math.isclose(Decimal(row[1]), testing_row['day_total'], rel_tol=1e-10) )
            #self.assertTrue(math.isclose(Decimal(row[2]), testing_row['day_average'], rel_tol=1e-10) )

        print("-" * 10)


    def make_user_datasets(self, num_of_users):
        data_frame = self.get_random_user_dataframe(num_of_users)
        User.objects.bulk_create(
            [ User(**row) for row in data_frame.to_dict('records') ]
        )
        return list(data_frame['user_id'])