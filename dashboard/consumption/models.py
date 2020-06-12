# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

class User(models.Model):
    """This table is imported from data/user_data.csv, basically."""

    #NOTE: Database access optimization, https://docs.djangoproject.com/en/3.0/topics/db/optimization/
    user_id = models.BigIntegerField(primary_key=True, db_index=True,
        validators=[MinValueValidator(0), MaxValueValidator(settings.ESTIMATED_NUM_OF_USERS)]) 
    area = models.CharField(max_length=4) #NOTE(Tasuku): Under num of cities in the world
    tariff = models.CharField(max_length=4)

    def __str__(self):
        return "User(user_id:{0}, area:{1}, tariff:{2})".format(self.user_id, self.area, self.tariff)


class ElectricityConsumption(models.Model):
    """This table is imported from data/consumption/<user_id>.csv, basically."""

    datetime = models.DateField()
    consumption = models.DecimalField(max_digits=8, decimal_places=1) #TODO(Tasuku): Consider a max consumption for 'rich' family
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "ElectricityConsumption(datetime:{0}, consumption:{1}, {2})".format(
            self.datetime, self.consumption, User.objects.get(user_id=self.user_id))


class ElectricityConsumptionAggregation(models.Model):
    """This table has total and average consumptions which will be calc"""
    date = models.DateField()
    date_total = models.DecimalField(max_digits=8 * settings.ESTIMATED_NUM_OF_USERS, decimal_places=1)
    date_average = models.DecimalField(max_digits=8, decimal_places=1)

    def __str__(self):
        pass #TODO
