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

    def test_aggregations(self):
        print("Making random users...")
        user_ids = self.make_user_datasets(5)

        print("Making random consumptions...")
        for user_id in user_ids:
            data_frame = self.get_random_consumption_dataframe(10000, user_id)

            ElectricityConsumption.objects.bulk_create(
                [ ElectricityConsumption(**row) for row in data_frame.to_dict('records') ]
            )
        EConsumptionDayAggregation.calc_consumptions()
        UserEConsumptionDayAggregation.calc_consumptions()

        self.compare_all_aggregation()
        self.compare_user_aggregation()
        print("-" * 10)


    def compare_all_aggregation(self):
        """Compare a result of SQLite with a result of EConsumptionDayAggregation.calc_consumptions()
        """
        cursor = connection.cursor()
        cursor.execute("""
            SELECT day, SUM(consumption) as day_total, AVG(consumption) as day_average FROM(
                SELECT DATE(datetime) as day, consumption FROM consumption_electricityconsumption
            ) GROUP BY day ORDER BY day;
        """) #TODO(Tasuku): Call a DB name from a model
        rows = cursor.fetchall()
        testing_rows = EConsumptionDayAggregation.objects.order_by('day').all().values()
        
        for row, testing_row in zip(rows, list(testing_rows)):
            self.assertEqual(row[0], testing_row['day'].strftime('%Y-%m-%d'))

            # WARNING(Tasuku): I guess the way of rounding between Django's decimal & Sql decimal is different. So I used isclose
            # This might be a hint, https://github.com/django/django/blob/master/django/forms/fields.py
            self.assertTrue(math.isclose(Decimal(row[1]), testing_row['day_total'], rel_tol=1e-9) )
            self.assertTrue(math.isclose(Decimal(row[2]), testing_row['day_average'], rel_tol=1e-9) )

    def compare_user_aggregation(self):
        """Compare a result of SQLite with a result of UserEConsumptionDayAggregation.calc_consumptions()
        """
        cursor = connection.cursor()
        cursor.execute("""
            SELECT user_id, day, SUM(consumption) as day_total, AVG(consumption) as day_average FROM(
                SELECT DATE(datetime) as day, user_id, consumption FROM consumption_electricityconsumption
            ) GROUP BY day, user_id  ORDER BY user_id ASC, day ASC;
        """) #TODO(Tasuku): Call a DB name from a model
        rows = cursor.fetchall()
        testing_rows = UserEConsumptionDayAggregation.objects.order_by('user_id', 'day').all().values()

        for row, testing_row in zip(rows, list(testing_rows)):
            self.assertEqual(row[0], testing_row['user_id'])
            self.assertEqual(row[1], testing_row['day'].strftime('%Y-%m-%d'))

            # WARNING(Tasuku): I guess the way of rounding between Django's decimal & Sql decimal is different. So I used isclose
            self.assertTrue(math.isclose(Decimal(row[2]), testing_row['day_total'], rel_tol=1e-9) )
            self.assertTrue(math.isclose(Decimal(row[3]), testing_row['day_average'], rel_tol=1e-9) )

    def make_user_datasets(self, num_of_users):
        data_frame = self.get_random_user_dataframe(num_of_users)
        User.objects.bulk_create(
            [ User(**row) for row in data_frame.to_dict('records') ]
        )
        return list(data_frame['user_id'])