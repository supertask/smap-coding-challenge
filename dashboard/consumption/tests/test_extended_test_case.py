# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from scipy import stats

from consumption.tests.extended_test_case import ExtendedTestCase

class ExtendedTestCaseTester(ExtendedTestCase):

    STATS_SIGNIFICANCE_LEVEL = 0.05
    NUM_OF_DIVISION = 1 / STATS_SIGNIFICANCE_LEVEL # 1/0.05 = 20

    def test_unique(self):
        """Test for get_unique_ids() & get_consumption_datetimes() of ExtendedTestCase"""

        print("Testing functions which make unique variables...")
        self.assertTrue(self.is_unique_variables(self.get_unique_ids(1000)) )
        self.assertTrue(self.is_unique_variables(self.get_consumption_datetimes(1000)) )
        print("-" * 10)

    def test_random_decimal(self):
        integer_part_len = 4
        num_of_test = 50000
        max_decimal = 10 ** integer_part_len
        min_decimal = -max_decimal
        pattern_per_division = (2 * max_decimal) / self.NUM_OF_DIVISION

        observed_frequencies_dict = {}
        for _ in range(num_of_test):
            value = self.get_random_decimal(integer_part_len) #-9999.9 ~ 9999.9
            self.count_observed_frequencies(
                value, min_decimal, max_decimal,
                pattern_per_division, observed_frequencies_dict
            )
        self.assertLess(self.STATS_SIGNIFICANCE_LEVEL, self.get_p_value(observed_frequencies_dict, num_of_test))

    def count_observed_frequencies(self, value, min_value, max_value, pattern_per_division, observed_frequencies_dict):
        for d in range(min_value, max_value, int(pattern_per_division)): #range(-10000, 10000, 1000)
            if d < value < d + pattern_per_division:
                if d in observed_frequencies_dict:
                    observed_frequencies_dict[d] += 1
                else:
                    observed_frequencies_dict[d] = 1
                break

    def get_p_value(self, observed_frequencies_dict, num_of_test):
        observed_frequencies = list(observed_frequencies_dict.values())
        expected_frequencies = [ int(num_of_test / self.NUM_OF_DIVISION) for _ in range(len(observed_frequencies))]
        print(observed_frequencies, expected_frequencies)
        _, p_value = stats.chisquare(f_obs=observed_frequencies, f_exp=expected_frequencies)
        print(p_value)

        return p_value