# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
import math

class User(models.Model):
    """This table is imported from data/user_data.csv, basically."""

    #NOTE: Database access optimization, https://docs.djangoproject.com/en/3.0/topics/db/optimization/
    user_id = models.BigIntegerField(primary_key=True, db_index=True,
        validators=[MinValueValidator(0), MaxValueValidator(settings.ESTIMATED_NUM_OF_USERS)]) 
    area = models.CharField(max_length=4) #NOTE(Tasuku): Under num of cities in the world
    tariff = models.CharField(max_length=4)

    def __str__(self):
        return "(user_id:{0}, area:{1}, tariff:{2})".format(self.user_id, self.area, self.tariff)


class ElectricityConsumption(models.Model):
    """This table is imported from data/consumption/<user_id>.csv, basically."""

    datetime = models.DateTimeField()

    #NOTE(Tasuku): Considering a max consumption for 'rich' family
    consumption = models.DecimalField(max_digits=5, decimal_places=1) #NOTE: e.g. 9999.9
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "(datetime:{0}, consumption:{1}, {2})".format(
            self.datetime, self.consumption, User.objects.get(user_id=self.user_id))


class ElectricityConsumptionDayAggregation(models.Model):
    """This table has total and average consumptions which will be calc"""
    day = models.DateField()
    day_total = models.DecimalField(
        max_digits= 5 + math.ceil(math.log10(settings.ESTIMATED_NUM_OF_USERS * settings.COMSUMPTION_RECORD_PER_DAY)),
        decimal_places = 1) #NOTE: e.g. 9999999999999999.9
    day_average = models.DecimalField(max_digits=14, decimal_places=10) #NOTE: e.g. 9999.9999999999

    def __str__(self):
        return "(day:{0}, day_total:{1}, day_average:{2})".format(self.day, self.day_total, day_average)

