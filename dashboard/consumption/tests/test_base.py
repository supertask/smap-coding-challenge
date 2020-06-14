# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.conf import settings
from model_bakery import baker

from consumption.models import User
from consumption.models import ElectricityConsumption
from consumption.models import EConsumptionDayAggregation
from consumption.models import UserEConsumptionDayAggregation

class TestBase(TestCase):
    def generate_random_user(self):
        return baker.make('consumption.User', user_id=1)
