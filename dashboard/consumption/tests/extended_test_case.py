# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import random
import string
import pytz
import pandas as pd
from enum import IntEnum
from enum import auto
from decimal import Decimal
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils.timezone import timedelta

from django.test import TestCase
from django.conf import settings

from consumption.models import User
from consumption.models import ElectricityConsumption
from consumption.models import EConsumptionDayAggregation
from consumption.models import UserEConsumptionDayAggregation
from consumption.util import Util 

class ExtendedTestCase(TestCase):
    """ExtendedTestCase is a class which expanded from TestCase for the consumption app.

    Basically this class includes functions which make random values.
    The type of random values are only enums on VariableType at this time.
    """
    RANDOM_LETTERS = string.ascii_letters + string.digits #NOTE: [a-z]+[A-Z]+[0-9]+
    MINUTE_RANGE = [minute for minute in range(0, 60, settings.MINUTE_PER_ONE_CONSUMPTION_RECORD)] #NOTE: e.g. [0, 30]
    BIG_INTEGER_RANGE = {'min': - (2 ** 63 - 1), 'max': 2 ** 63 - 1 }

    def setUp(self):
        pass
    
    def is_unique_variables(self, variables):
        return (len(variables) == len(set(variables)) )

    def get_random_decimal(self, integer_part_len=4, decimal_part_len=1):
        v = 10 ** integer_part_len - 1
        return round(Decimal(random.randrange(-v, v)), decimal_part_len )

    def get_random_big_integer(self, additional_range={'min': 0, 'max': 0}):
        return random.randint(
            self.BIG_INTEGER_RANGE['min'],
            self.BIG_INTEGER_RANGE['max']
        )

    #
    # TODO(Tasuku): Test random functions bellow with Chi-squared test(e.g. scipy.stats.chisquare)
    #
    def get_random_string(self, max_length=4):
        random_string = ""
        for i in range(max_length):
            random_string += random.choice(self.RANDOM_LETTERS)
        return random_string
    
    def get_custom_random_datetime(self, min_year = 1900, max_year = 2100):
        dt = self.get_random_datetime(min_year, max_year)
        dt = dt.replace(minute = random.choice(self.MINUTE_RANGE), second = 0, microsecond = 0)
        return dt

    def get_random_date(self, min_year = 1900, max_year = 2100):
        dt = self.get_random_datetime(min_year, max_year)
        dt = dt.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        return dt

    def get_random_datetime(self, min_year = 1900, max_year = 2100, rand = random.random()):
        start = timezone.make_aware(datetime(min_year, 1, 1, 00, 00, 00), timezone=settings.TZ)
        years = max_year - min_year + 1
        end = start + timedelta(days=365 * years)
        return start + (end - start) * rand

    def get_consumption_datetimes(self, max_sample_len):
        start = self.get_custom_random_datetime()
        consumption_datetimes = []
        for i in range(max_sample_len):
            consumption_datetimes.append(
                start + timedelta(minutes = settings.MINUTE_PER_ONE_CONSUMPTION_RECORD * i)
            )
        return consumption_datetimes

    def get_unique_ids(self, max_sample_len):
        if max_sample_len <= 0:
            sys.exit(settings.EXIT_FAILURE)
        return random.sample(
            range(
                0,
                self.BIG_INTEGER_RANGE['max'],
                int(self.BIG_INTEGER_RANGE['max'] / max_sample_len / 10 )
            ),
            max_sample_len
        )

    def get_random_user_dataframe(self, num_of_rows):
        user_ids = self.get_unique_ids(num_of_rows)
        user_table = {
            'user_id': user_ids, 'area': [], 'tariff': []
        }
        for _ in range(len(user_ids)):
            user_table['area'].append(self.get_random_string())
            user_table['tariff'].append(self.get_random_string())
        return pd.DataFrame(user_table)

    def get_random_consumption_dataframe(self, num_of_rows, user_id):
        datetimes = self.get_consumption_datetimes(num_of_rows)
        consumption_table = {
            'datetime': datetimes, 'consumption': [], 'user_id': []
        }
        for _ in range(len(datetimes)):
            consumption_table['consumption'].append(self.get_random_decimal())
            consumption_table['user_id'].append(user_id)
        return pd.DataFrame(consumption_table)