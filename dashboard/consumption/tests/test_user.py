# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from model_bakery import baker

from consumption.models import User
from consumption.models import ElectricityConsumption
from consumption.models import EConsumptionDayAggregation
from consumption.models import UserEConsumptionDayAggregation
from consumption.tests.test_base import TestBase

class TestUser(TestBase):
    def setUp(self):
        pass

    def test_user(self):
        user = baker.make('consumption.User', user_id=1)
        print(user.user_id)

    #def test_bad_maths(self):
    #    self.assertEqual(1+1, 3)