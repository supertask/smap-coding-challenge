# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from django.conf import settings

from consumption.models import ElectricityConsumption
from consumption.tests.extended_test_case import ExtendedTestCase

class ConsumptionTester(ExtendedTestCase):
    def setUp(self):
        pass

    def test_expected_consumptions(self):
        """Test consumptions which are expected to have no errors.
        """
        print()
        print("Testing consumptions whose parameters are safe...")
        for current_datetime in self.get_consumption_datetimes(1000):
            self.store_expected_consumption(current_datetime)
        
        ElectricityConsumption.objects.all().delete()
        print("Testing many consumptions whose parameters are safe with bulk_create...")
        self.store_many_expected_consumptions()

        print("-" * 10)


    def store_expected_consumption(self, current_datetime):
        consumption = self.get_random_decimal()
        user_id = self.get_random_big_integer()
        try:
            caused_error = False
            e_consumption = ElectricityConsumption(datetime=current_datetime, consumption=consumption, user_id=user_id)
            e_consumption.save()
            e_consumption = list(ElectricityConsumption.objects.filter(datetime=current_datetime))[0]
        except Exception:
            caused_error = True
        self.assertFalse(caused_error)
        self.assertEqual(e_consumption.datetime, current_datetime)
        self.assertEqual(e_consumption.consumption, consumption)
        self.assertEqual(e_consumption.user_id, user_id)

    def store_many_expected_consumptions(self):
        e_consumptions = []
        e_consumptions_dict = {}
        for current_datetime in self.get_consumption_datetimes(50000):
            e_consumptions_dict[current_datetime] = {
                'consumption': self.get_random_decimal(),
                'user_id': self.get_random_big_integer()
            }
            e_consumptions.append(
                ElectricityConsumption(
                    datetime = current_datetime,
                    consumption = e_consumptions_dict[current_datetime]['consumption'],
                    user_id = e_consumptions_dict[current_datetime]['user_id'],
                )
            )
        ElectricityConsumption.objects.bulk_create(e_consumptions)

        for e_consumption in ElectricityConsumption.objects.all():
            self.assertEqual(e_consumption.consumption, e_consumptions_dict[e_consumption.datetime]['consumption'])
            self.assertEqual(e_consumption.user_id, e_consumptions_dict[e_consumption.datetime]['user_id'])
