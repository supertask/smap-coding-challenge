# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import random
import string
from enum import IntEnum
from enum import auto
from datetime import datetime, timedelta

from django.test import TestCase
from django.conf import settings

from consumption.models import User
from consumption.models import ElectricityConsumption
from consumption.models import EConsumptionDayAggregation
from consumption.models import UserEConsumptionDayAggregation


class VariableType(IntEnum):
    """A variable type of Django model"""
    BIG_INTEGER = 0
    STRING = auto()
    DATE = auto()
    DATETIME = auto()
    DECIMAL = auto()

class TestBase(TestCase):

    random_letters = string.ascii_letters + string.digits #NOTE: [a-z]+[A-Z]+[0-9]+
    minute_range = [0, 30] #NOTE: 0 mins or 30 mins
    big_integer_range = {'min': - (2 ** 63 - 1), 'max': 2 ** 63 - 1 }

    def setUp(self):
        pass

    def get_random_value(self, ignore_types = []):
        variable_types = list(VariableType)
        for ignore_type in ignore_types:
            variable_types.remove(ignore_type)
        v_type = random.choice(variable_types)
        #print(v_type)
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
        return round(random.uniform(-v, v), decimal_part_len)

    def get_random_big_integer(self):
        return random.randint(
            self.big_integer_range['min'],
            self.big_integer_range['max']
        )

    def get_invalid_random_big_integer(self):
        c = random.choice([0, 1])
        if c == 0:
            return random.randint(self.big_integer_range['max'] + 1, self.big_integer_range['max'] + 1000)
        elif c == 1:
            return random.randint(self.big_integer_range['min'] - 1000, self.big_integer_range['min'] - 1)
        raise NotImplementedError('Check out if you have enough "if" or "elif" statements.')

    def get_random_string(self, max_length=4):
        random_string = ""
        for i in range(max_length):
            random_string += random.choice(self.random_letters)
        return random_string
    
    def get_custom_random_datetime(self):
        dt = self.get_random_datetime()
        dt = dt.replace(minute = random.choice(self.minute_range), second = 0, microsecond = 0)
        return dt

    def get_random_date(self):
        dt = self.get_random_datetime()
        dt = dt.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        return dt

    def get_random_datetime(self, min_year=1900, max_year=datetime.now().year):
        start = datetime(min_year, 1, 1, 00, 00, 00)
        years = max_year - min_year + 1
        end = start + timedelta(days=365 * years)
        return start + (end - start) * random.random()