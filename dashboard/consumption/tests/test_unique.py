# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from consumption.tests.base import TestBase

class TestUnique(TestBase):
    def test_unique(self):
        print("Testing functions which make unique variables...")
        self.assertTrue(self.is_unique_variables(self.get_unique_ids(1000)) )
        self.assertTrue(self.is_unique_variables(self.get_random_unique_datetimes(1000)) )

        print("-" * 10)
