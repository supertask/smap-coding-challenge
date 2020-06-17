# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import random
import string
import pytz
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


class VariableType(IntEnum):
    """A variable type of Django model"""
    BIG_INTEGER = 0
    STRING = auto()
    DATE = auto()
    DATETIME = auto()
    DECIMAL = auto()

class TestBase(TestCase):
    """Base class for test.

    Basically this class includes functions which make random values.
    The type of random values are only enums on VariableType at this time.
    """
    random_letters = string.ascii_letters + string.digits #NOTE: [a-z]+[A-Z]+[0-9]+
    minute_range = [0, 30] #NOTE: 0 mins or 30 mins
    big_integer_range = {'min': - (2 ** 63 - 1), 'max': 2 ** 63 - 1 }

    def setUp(self):
        pass
    
    def test_unique(self):
        print("Testing functions which make unique variables...")
        self.assertTrue(self.is_unique_variables(self.get_unique_ids(1000)) )
        self.assertTrue(self.is_unique_variables(self.get_random_unique_datetimes(1000)) )

        print("-" * 10)


    def is_unique_variables(self, variables):
        return (len(variables) == len(set(variables)) )

    def get_random_value(self, ignore_types = []):
        variable_types = list(VariableType)
        for ignore_type in ignore_types:
            variable_types.remove(ignore_type)
        v_type = random.choice(variable_types)
        if v_type == VariableType.BIG_INTEGER: 
            return self.get_random_big_integer()
        elif v_type == VariableType.STRING: 
            return self.get_random_string()
        elif v_type == VariableType.DATE: 
            return self.get_random_date()
        elif v_type == VariableType.DATETIME: 
            return self.get_custom_random_datetime()
        elif v_type == VariableType.DECIMAL: 
            return self.get_random_decimal()

        raise NotImplementedError('Check out if you have enough "if" or "elif" statements.')

    def get_random_decimal(self, integer_part_len=4, decimal_part_len=1):
        v = 10 ** integer_part_len - 1
        return round(Decimal(random.randrange(-v, v)), 1 )

    def get_random_big_integer(self, additional_range={'min': 0, 'max': 0}):
        return random.randint(
            self.big_integer_range['min'],
            self.big_integer_range['max']
        )

    def get_invalid_random_big_integer(self):
        rand = random.choice([0, 1])
        if rand == 0:
            return random.randint(self.big_integer_range['max'] + 1, self.big_integer_range['max'] + 1000)
        elif rand == 1:
            return random.randint(self.big_integer_range['min'] - 1000, self.big_integer_range['min'] - 1)
        raise NotImplementedError('Check out if you have enough "if" or "elif" statements.')

    def get_random_string(self, max_length=4):
        random_string = ""
        for i in range(max_length):
            random_string += random.choice(self.random_letters)
        return random_string
    
    def get_custom_random_datetime(self, min_year = 1900, max_year = 2100):
        dt = self.get_random_datetime(min_year, max_year)
        dt = dt.replace(minute = random.choice(self.minute_range), second = 0, microsecond = 0)
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

    def get_random_unique_datetimes(self, max_sample_len):
        if max_sample_len <= 0:
            sys.exit(settings.EXIT_FAILURE)
        start_t = int(datetime.timestamp(
            timezone.make_aware(datetime(1900, 1, 1, 00, 00, 00), timezone=settings.TZ)
        ))
        end_t = int(datetime.timestamp(datetime.now()) )
        rand_timestamps = random.sample(
            range(start_t, end_t, int((end_t - start_t) / max_sample_len / 10)),
            max_sample_len
        )
        rand_datetimes = [datetime.fromtimestamp(t, tz=pytz.timezone(settings.TIME_ZONE)) for t in rand_timestamps]
        return rand_datetimes

    def get_unique_ids(self, max_sample_len):
        if max_sample_len <= 0:
            sys.exit(settings.EXIT_FAILURE)
        return random.sample(
            range(
                0,
                self.big_integer_range['max'],
                int(self.big_integer_range['max'] / max_sample_len / 10 )
            ),
            max_sample_len
        )