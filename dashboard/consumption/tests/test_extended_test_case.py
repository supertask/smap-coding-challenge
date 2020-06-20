# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from scipy import stats
from django.utils import timezone
from django.utils.timezone import datetime
from django.conf import settings

from consumption.tests.extended_test_case import ExtendedTestCase

class ExtendedTestCaseTester(ExtendedTestCase):

    SIGNIFICANCE_LEVEL = 0.01
    NUM_OF_DIVISION = 10

    def test_unique(self):
        """Test for get_unique_ids() & get_consumption_datetimes() of ExtendedTestCase"""

        print()
        print("Testing functions which make unique variables...")
        self.assertTrue(self.is_unique_variables(self.get_unique_ids(1000)) )
        self.assertTrue(self.is_unique_variables(self.get_consumption_datetimes(1000)) )
        print("-" * 10)

    def test_random_decimal(self):
        print()
        print("Testing random decimal...")

        integer_part_len = 4
        num_of_test = 10000
        max_decimal = 10 ** integer_part_len
        min_decimal = -max_decimal

        observed_frequencies_dict = {}
        for _ in range(num_of_test):
            value = self.get_random_decimal(integer_part_len) #-9999.9 ~ 9999.9
            self.assertTrue(isinstance(value, Decimal))
            self.assertTrue(Decimal(min_decimal) <= value < Decimal(max_decimal))

            observed_frequencies_dict = self.count_observed_frequencies(
                value, min_decimal, max_decimal,
                observed_frequencies_dict
            )
        self.assertLess(self.SIGNIFICANCE_LEVEL, self.get_p_value(observed_frequencies_dict, num_of_test))

    def test_random_big_integer(self):
        print()
        print("Testing random decimal...")

        num_of_test = 10000
        min_integer = self.BIG_INTEGER_RANGE['min']
        max_integer = self.BIG_INTEGER_RANGE['max']

        observed_frequencies_dict = {}
        for _ in range(num_of_test):
            value = self.get_random_big_integer()
            self.assertTrue(isinstance(value, int))
            self.assertTrue(min_integer <= value < max_integer)

            observed_frequencies_dict = self.count_observed_frequencies(
                value, min_integer, max_integer,
                observed_frequencies_dict
            )
        self.assertLess(self.SIGNIFICANCE_LEVEL, self.get_p_value(observed_frequencies_dict, num_of_test))

    def test_random_datetime(self):
        print()
        print("Testing random datetime...")

        num_of_test = 10000
        min_year = 1900
        max_year = 2100
        start_t = int(timezone.make_aware(datetime(min_year, 1, 1, 00, 00, 00), timezone=settings.TZ).timestamp())
        end_t = int(timezone.make_aware(datetime(max_year, 1, 1, 00, 00, 00), timezone=settings.TZ).timestamp())

        observed_frequencies_dict = {}
        for _ in range(num_of_test):
            rand_datetime = self.get_random_datetime(min_year, max_year)
            self.assertTrue(isinstance(rand_datetime, datetime))
            self.assertTrue(min_year <= rand_datetime.year <= max_year)

            observed_frequencies_dict = self.count_observed_frequencies(
                rand_datetime.timestamp(), start_t, end_t,
                observed_frequencies_dict
            )
        self.assertLess(self.SIGNIFICANCE_LEVEL, self.get_p_value(observed_frequencies_dict, num_of_test))

    def test_custom_random_datetime(self):
        print()
        print("Testing custom random datetime...")

        num_of_test = 10000
        min_year = 1900
        max_year = 2100
        start_t = int(timezone.make_aware(datetime(min_year, 1, 1, 00, 00, 00), timezone=settings.TZ).timestamp())
        end_t = int(timezone.make_aware(datetime(max_year, 1, 1, 00, 00, 00), timezone=settings.TZ).timestamp())

        observed_frequencies_dict = {}
        for _ in range(num_of_test):
            rand_datetime = self.get_custom_random_datetime(min_year, max_year)
            self.assertTrue(isinstance(rand_datetime, datetime))
            self.assertTrue(min_year <= rand_datetime.year <= max_year)
            self.assertTrue(rand_datetime.minute in self.MINUTE_RANGE)
            self.assertEqual(rand_datetime.second, 0)
            self.assertEqual(rand_datetime.microsecond, 0)

            observed_frequencies_dict = self.count_observed_frequencies(
                rand_datetime.timestamp(), start_t, end_t,
                observed_frequencies_dict
            )
        self.assertLess(self.SIGNIFICANCE_LEVEL, self.get_p_value(observed_frequencies_dict, num_of_test))


    def count_observed_frequencies(self, value, min_value, max_value, observed_frequencies_dict):
        pattern_per_division = int(float(max_value - min_value) / self.NUM_OF_DIVISION)
        for d in range(min_value, max_value, pattern_per_division): #range(-10000, 10000, 1000)
            if d < value <= d + pattern_per_division:
                if d in observed_frequencies_dict:
                    observed_frequencies_dict[d] += 1
                else:
                    observed_frequencies_dict[d] = 1
                break
        return observed_frequencies_dict

    def get_p_value(self, observed_frequencies_dict, num_of_test):
        observed_frequencies = list(observed_frequencies_dict.values())
        expected_frequencies = [ int(num_of_test / self.NUM_OF_DIVISION) for _ in range(len(observed_frequencies))]
        _, p_value = stats.chisquare(f_obs=observed_frequencies, f_exp=expected_frequencies)
        print("Observed frequencies: %s" % observed_frequencies)
        print("Expected frequencies: %s" % expected_frequencies)
        print("P-value: %s" % p_value)
        return p_value

    def is_unique_variables(self, variables):
        return (len(variables) == len(set(variables)) )