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

from consumption.models import User
from consumption.models import ElectricityConsumption
from consumption.models import EConsumptionDayAggregation
from consumption.models import UserEConsumptionDayAggregation
from consumption.tests.test_base import TestBase
from consumption.tests.test_base import VariableType

class UserColumn(IntEnum):
    USER_ID = 0
    AREA = auto()
    TARIFF = auto()

class TestUser(TestBase):
    def setUp(self):
        pass

    def test_expected_users(self):
        """Test users who is expected to have no errors.
        """
        print("Testing users whose parameters are safe...")
        for user_id in self.get_unique_user_ids(100):
            self.save_expected_user(user_id)
        
        User.objects.all().delete()
        print("Testing many users whose parameters are safe with bulk_create...")
        self.save_many_expected_users()


    def test_error_users(self):
        """Test users who have a wrong type parameter / an invalid parameter

        Purpose to make these users bellow is that saving data causes some errors
        when parameters of 'User' class are modified by someone.
        """

        print("Testing users who have a wrong type parameter...")
        for _ in range(100):
            self.make_wrong_type_user()

        print("Testing users who have an invalid parameter...")
        for _ in range(10000):
            self.make_invalid_user()


    def make_wrong_type_user(self):
        """Make a user which will cause ValueError.

        The random user is made by "baker.make" and has random parameters.
        A wrong parameter is also put into User class.
        """
        # NOTE(Tasuku): string(e.g. 'area' or 'tariff') doesn't make errors even the variable is wrong
        column = random.choice([UserColumn.USER_ID])
        caused_error = False
        if column == UserColumn.USER_ID:
            try:
                baker.make(User,
                    user_id = self.get_random_value(ignore_types = [VariableType.BIG_INTEGER, VariableType.DECIMAL])
                )
            except Exception:
                caused_error = True
            self.assertEqual(caused_error, True)
            return

        raise NotImplementedError('Check out if you have enough "if" or "elif" statements')


    def make_invalid_user(self):
        """Make a user which will cause invalid error.

        The random user is made by "baker.make" and has random parameters.
        An invalid parameter (e.g. too big integer) is also put into User class.
        """
        # NOTE(Tasuku): string(e.g. 'area' or 'tariff') doesn't make errors even the variable is invalid
        column = random.choice([UserColumn.USER_ID])
        caused_error = False
        if column == UserColumn.USER_ID:
            try:
                baker.make(User, user_id=self.get_invalid_random_big_integer())
            except transaction.TransactionManagementError as e:
                caused_error = True
            self.assertEqual(caused_error, True)


    def save_expected_user(self, user_id):
        area = self.get_random_string()
        tariff = self.get_random_string()
        try:
            caused_error = False
            user = User(user_id=user_id, area=area, tariff=tariff)
            user.save()
            user = list(User.objects.filter(user_id=user_id))[0]
        except Exception:
            caused_error = True
        self.assertEqual(caused_error, False)
        self.assertEqual(user.area, area)
        self.assertEqual(user.tariff, tariff)

    def save_many_expected_users(self):
        users = []
        users_dict = {} #For test
        for user_id in self.get_unique_user_ids(50000):
            users_dict[user_id] = { 'area': self.get_random_string(), 'tariff': self.get_random_string() }
            users.append( User(user_id=user_id, area=users_dict[user_id]['area'], tariff=users_dict[user_id]['tariff']))
        User.objects.bulk_create(users)

        for user in User.objects.all():
            self.assertEqual(user.area, users_dict[user.user_id]['area'])
            self.assertEqual(user.tariff, users_dict[user.user_id]['tariff'])

    
    def get_unique_user_ids(self, max_user_len):
        if max_user_len <= 0:
            sys.exit(settings.EXIT_FAILURE)
        return random.sample(
            range(
                0,
                self.big_integer_range['max'],
                int(self.big_integer_range['max'] / max_user_len / 10 )
            ),
            max_user_len
        )
