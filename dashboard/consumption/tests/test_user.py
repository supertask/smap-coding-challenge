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
        for user_id in self.get_unique_ids(100):
            self.save_expected_user(user_id)
        
        User.objects.all().delete()
        print("Testing many users whose parameters are safe with bulk_create...")
        self.save_many_expected_users()

        print("-" * 10)


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
        print("-" * 10)


    def make_wrong_type_user(self):
        """Make a user which will cause ValueError.

        The random user is made by functions on BaseTest class and has random parameters.
        One of the random parameters is wrong type parameter. This test detects it.
        """
        # NOTE(Tasuku): string(e.g. 'area' or 'tariff') doesn't make errors even the variable is wrong
        column = random.choice([UserColumn.USER_ID])
        caused_error = False
        if column == UserColumn.USER_ID:
            try:
                user = User(
                    user_id = self.get_random_value(ignore_types = [VariableType.BIG_INTEGER, VariableType.DECIMAL]),
                    area = self.get_random_string(), tariff = self.get_random_string()
                )
                user.save()
            except Exception:
                caused_error = True
            self.assertTrue(caused_error)
            return

        raise NotImplementedError('Check out if you have enough "if" or "elif" statements')


    def make_invalid_user(self):
        """Make a user which will cause invalid error.

        The random user is made by functions on BaseTest class and has random parameters.
        One of the random parameters is invalid type parameter. This test detects it.
        """
        # NOTE(Tasuku): string(e.g. 'area' or 'tariff') doesn't make errors even the variable is invalid
        column = random.choice([UserColumn.USER_ID])
        caused_error = False
        if column == UserColumn.USER_ID:
            try:
                user = User(
                    user_id=self.get_invalid_random_big_integer(),
                    area = self.get_random_string(), tariff = self.get_random_string()
                )
                user.save()
            except transaction.TransactionManagementError as e:
                caused_error = True
            self.assertTrue(caused_error)


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
        self.assertFalse(caused_error)
        self.assertEqual(user.area, area)
        self.assertEqual(user.tariff, tariff)

    def save_many_expected_users(self):
        users = []
        users_dict = {} #For test
        for user_id in self.get_unique_ids(50000):
            users_dict[user_id] = { 'area': self.get_random_string(), 'tariff': self.get_random_string() }
            users.append( User(user_id=user_id, area=users_dict[user_id]['area'], tariff=users_dict[user_id]['tariff']))
        User.objects.bulk_create(users)

        for user in User.objects.all():
            self.assertEqual(user.area, users_dict[user.user_id]['area'])
            self.assertEqual(user.tariff, users_dict[user.user_id]['tariff'])

    