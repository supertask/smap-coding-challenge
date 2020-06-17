# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import random
from enum import IntEnum
from enum import auto

from django.test import TestCase
from django.core import exceptions
from django.conf import settings
from django.db import transaction

from consumption.models import ElectricityConsumption
from consumption.tests.test_base import TestBase
from consumption.tests.test_base import VariableType

class EConsumptionColumn(IntEnum):
    DATETIME = 0
    CONSUMPTION = auto()
    USER_ID = auto()

class TestElectricityConsumption(TestBase):
    def setUp(self):
        pass

    def test_expected_consumptions(self):
        """Test consumptions which are expected to have no errors.
        """
        print("Testing consumptions whose parameters are safe...")
        for unique_datetime in self.get_random_unique_datetimes(1000):
            self.save_expected_consumption(unique_datetime)
        
        ElectricityConsumption.objects.all().delete()
        print("Testing many consumptions whose parameters are safe with bulk_create...")
        self.save_many_expected_consumptions()

        print("-" * 10)


    def test_error_consumptions(self):
        """Test consumptions which have a wrong type parameter / an invalid parameter

        Purpose to make these consumptions bellow is that saving data causes some errors
        when parameters of 'ElectricityConsumption' class are modified by someone.
        """

        print("Testing consumptions who have a wrong type parameter...")
        for _ in range(1000):
            self.make_wrong_type_consumption()

        print("Testing consumptions who have an invalid parameter...")
        for _ in range(10000):
            self.make_invalid_consumption()

        print("-" * 10)


    def make_wrong_type_consumption(self):
        """Make a consumption which will cause ValueError.

        The random consumption is made by functions on BaseTest class and has random parameters.
        One of the random parameters is wrong type parameter. This test detects it.
        """
        # NOTE(Tasuku): string(e.g. 'area' or 'tariff') doesn't make errors even the variable is wrong
        column = random.choice(list(EConsumptionColumn))
        caused_error = False
        if column == EConsumptionColumn.DATETIME:
            try:
                e_consumption = ElectricityConsumption(
                    datetime = self.get_random_value(ignore_types = [VariableType.DATETIME, VariableType.DATE]),
                    consumption = self.get_random_decimal(), user_id = self.get_random_big_integer()
                )
                e_consumption.save()
            except Exception:
                caused_error = True
            self.assertTrue(caused_error)
            return
        elif column == EConsumptionColumn.CONSUMPTION:
            try:
                e_consumption = ElectricityConsumption(
                    datetime = self.get_custom_random_datetime(),
                    consumption = self.get_random_value(ignore_types = [VariableType.BIG_INTEGER, VariableType.DECIMAL]),
                    user_id = self.get_random_big_integer()
                )
                e_consumption.save()
            except Exception:
                caused_error = True
            self.assertTrue(caused_error)
            return
        elif column == EConsumptionColumn.USER_ID:
            try:
                e_consumption = ElectricityConsumption(
                    datetime = self.get_custom_random_datetime(), consumption = self.get_random_decimal(),
                    user_id = self.get_random_value(ignore_types = [VariableType.BIG_INTEGER, VariableType.DECIMAL])
                )
                e_consumption.save()
            except Exception:
                caused_error = True
            self.assertTrue(caused_error)
            return

        raise NotImplementedError('Check out if you have enough "if" or "elif" statements')


    def make_invalid_consumption(self):
        """Make a consumption which will cause invalid error.

        The random consumption is made by functions on BaseTest class and has random parameters.
        One of the random parameters is invalid parameter. This test detects it. 
        """
        # NOTE(Tasuku): string(e.g. 'area' or 'tariff') doesn't make errors even the variable is invalid
        column = random.choice([EConsumptionColumn.CONSUMPTION, EConsumptionColumn.USER_ID])
        caused_error = False
        if column == EConsumptionColumn.CONSUMPTION:
            try:
                e_consumption = ElectricityConsumption(
                    datetime = self.get_custom_random_datetime(),
                    consumption = self.get_random_decimal(),
                    user_id = self.get_random_big_integer()
                )
                e_consumption.save()
            except transaction.TransactionManagementError as e:
                caused_error = True
            self.assertTrue(caused_error)
            return

        elif column == EConsumptionColumn.USER_ID:
            try:
                e_consumption = ElectricityConsumption(
                    datetime = self.get_custom_random_datetime(), consumption = self.get_random_decimal(),
                    user_id = self.get_invalid_random_big_integer()
                )
                e_consumption.save()
            except transaction.TransactionManagementError as e:
                caused_error = True
            self.assertTrue(caused_error)
            return

        raise NotImplementedError('Check out if you have enough "if" or "elif" statements')


    def save_expected_consumption(self, unique_datetime):
        consumption = self.get_random_decimal()
        user_id = self.get_random_big_integer()
        try:
            caused_error = False
            e_consumption = ElectricityConsumption(datetime=unique_datetime, consumption=consumption, user_id=user_id)
            e_consumption.save()
            e_consumption = list(ElectricityConsumption.objects.filter(datetime=unique_datetime))[0]
        except Exception:
            caused_error = True
        self.assertFalse(caused_error)
        self.assertEqual(e_consumption.datetime, unique_datetime)
        self.assertEqual(e_consumption.consumption, consumption)
        self.assertEqual(e_consumption.user_id, user_id)

    def save_many_expected_consumptions(self):
        e_consumptions = []
        e_consumptions_dict = {}
        for unique_datetime in self.get_random_unique_datetimes(50000):
            e_consumptions_dict[unique_datetime] = {
                'consumption': self.get_random_decimal(),
                'user_id': self.get_random_big_integer()
            }
            e_consumptions.append(
                ElectricityConsumption(
                    datetime = unique_datetime,
                    consumption = e_consumptions_dict[unique_datetime]['consumption'],
                    user_id = e_consumptions_dict[unique_datetime]['user_id'],
                )
            )
        ElectricityConsumption.objects.bulk_create(e_consumptions)

        for e_consumption in ElectricityConsumption.objects.all():
            self.assertEqual(e_consumption.consumption, e_consumptions_dict[e_consumption.datetime]['consumption'])
            self.assertEqual(e_consumption.user_id, e_consumptions_dict[e_consumption.datetime]['user_id'])
