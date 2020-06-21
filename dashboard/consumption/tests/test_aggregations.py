# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import math 
import decimal
from decimal import Decimal

from tqdm import tqdm
from django.db import connection

from consumption.models import User
from consumption.models import ElectricityConsumption
from consumption.models import EConsumptionDayAggregation
from consumption.models import UserEConsumptionDayAggregation
from consumption.tests.extended_test_case import ExtendedTestCase

class TestAggregations(ExtendedTestCase):
    NUM_OF_USERS = 10
    NUM_OF_CONSUMPTIONS = 10000

    # NOTE: If NUM_OF_CONSUMPTIONS or NUM_OF_USERS are increased, decrease this rate
    # Why this rate is needed is that SQLite's Real has no Decimal while Django has Decimal.
    # SQLite's Real is like 8 bite double variable. Therefore, when "num of calculation is increased",
    # a calculation error will increase
    RELATIVE_TOLERANCE = 1e-8

    def setUp(self):
        User.objects.all().delete()
        ElectricityConsumption.objects.all().delete()

    def test_datasets(self):
        print()
        print("Making random users...")
        user_ids = self.make_user_datasets(self.NUM_OF_USERS)

        print("Making random consumptions...")
        for user_id in user_ids:
            data_frame = self.get_random_consumption_dataframe(self.NUM_OF_CONSUMPTIONS, user_id)

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

            if not math.isclose(Decimal(row[2]), testing_row['day_average'], rel_tol=self.RELATIVE_TOLERANCE):
                print(Decimal(row[2]), testing_row['day_average'])
                print(row[2], testing_row['day_average'])

            # WARNING(Tasuku): If you encountered an error here due to 
            # too much increased NUM_OF_CONSUMPTIONS or NUM_OF_USERS, then decrease RELATIVE_TOLERANCE
            self.assertTrue(math.isclose(Decimal(row[1]), testing_row['day_total'], rel_tol=self.RELATIVE_TOLERANCE) )
            self.assertTrue(math.isclose(Decimal(row[2]), testing_row['day_average'], rel_tol=self.RELATIVE_TOLERANCE) )

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

            if not math.isclose(Decimal(row[3]), testing_row['day_average'], rel_tol=self.RELATIVE_TOLERANCE):
                print(Decimal(row[3]), testing_row['day_average'])
                print(row[3], testing_row['day_average'])

            # WARNING(Tasuku): If you encountered an error here due to 
            # too much increased NUM_OF_CONSUMPTIONS or NUM_OF_USERS, then decrease RELATIVE_TOLERANCE
            self.assertTrue(math.isclose(Decimal(row[2]), testing_row['day_total'], rel_tol=self.RELATIVE_TOLERANCE) )
            self.assertTrue(math.isclose(Decimal(row[3]), testing_row['day_average'], rel_tol=self.RELATIVE_TOLERANCE) )

    def make_user_datasets(self, num_of_users):
        data_frame = self.get_random_user_dataframe(num_of_users)
        User.objects.bulk_create(
            [ User(**row) for row in data_frame.to_dict('records') ]
        )
        return list(data_frame['user_id'])