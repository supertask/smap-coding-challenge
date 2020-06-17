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
from consumption.tests.base import TestBase

class TestConsumption(TestBase):
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
