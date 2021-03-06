# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from django.conf import settings

from consumption.models import User
from consumption.tests.extended_test_case import ExtendedTestCase

class UserTester(ExtendedTestCase):
    def setUp(self):
        pass

    def test_expected_users(self):
        """Test users who is expected to have no errors.
        """
        print()
        print("Testing users whose parameters are safe...")
        for user_id in self.get_unique_ids(100):
            self.store_expected_user(user_id)
        
        User.objects.all().delete()
        print("Testing many users whose parameters are safe with bulk_create...")
        self.store_many_expected_users()

        print("-" * 10)

    def store_expected_user(self, user_id):
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

    def store_many_expected_users(self):
        users = []
        users_dict = {} #For test
        for user_id in self.get_unique_ids(50000):
            users_dict[user_id] = { 'area': self.get_random_string(), 'tariff': self.get_random_string() }
            users.append( User(user_id=user_id, area=users_dict[user_id]['area'], tariff=users_dict[user_id]['tariff']))
        User.objects.bulk_create(users)

        for user in User.objects.all():
            self.assertEqual(user.area, users_dict[user.user_id]['area'])
            self.assertEqual(user.tariff, users_dict[user.user_id]['tariff'])