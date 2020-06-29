# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math

import pandas as pd
from django.db import models
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.conf import settings
from django.db.models.functions import TruncDay
from django.db.models import Avg
from django.db.models import Sum

#
# NOTE(Tasuku):
# Implementation of Django fields to understand "Django variable <-> Python variable"
# https://github.com/django/django/blob/master/django/forms/fields.py
#
# Outbounded decimal will cause a unintelligible error,
# https://code.djangoproject.com/ticket/26963
#

class User(models.Model):
    """This table is imported from data/user_data.csv, basically."""

    # NOTE: Database access optimization, https://docs.djangoproject.com/en/3.0/topics/db/optimization/
    user_id = models.BigIntegerField(primary_key=True, db_index=True)
    area = models.CharField(max_length=4) # NOTE(Tasuku): Under num of cities in the world
    tariff = models.CharField(max_length=4)

    def __str__(self):
        return "(user_id:{0}, area:{1}, tariff:{2})".format(self.user_id, self.area, self.tariff)


class ElectricityConsumption(models.Model):
    """This table is imported from data/consumption/<user_id>.csv, basically."""
    datetime = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    consumption = models.DecimalField(max_digits=5, decimal_places=1) # NOTE: e.g. 9999.9. Considering a max consumption for 'rich' family

    def __str__(self):
        return "(datetime:{0}, consumption:{1}, {2})".format(
            self.datetime, self.consumption, User.objects.get(user_id=self.user_id))


class UserEConsumptionDayAggregation(models.Model):
    """Total and average consumptions per day are aggregated into this table for each user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.DateField()
    day_total = models.DecimalField(
        max_digits= 5 + math.ceil(math.log10(settings.CONSUMPTION_RECORD_PER_DAY)),
        decimal_places = 1) # NOTE: e.g. 999999.9
    day_average = models.DecimalField(max_digits=14, decimal_places=10) # NOTE: e.g. 9999.9999999999

    @classmethod
    def calc_consumptions(self):
        """Calc and put total and average electricity consumption into DB."""

        #
        # OPTIMIZE(Tasuku): Consider RAM when num of users is increased. And test huge datasets over and over
        #
        # NOTE(Tasuku): a statement on SQLite
        # SELECT day, user_id, SUM(consumption) as day_total, AVG(consumption) as day_average FROM(
        #     SELECT DATE(datetime) as day, user_id, consumption FROM consumption_electricityconsumption
        # ) GROUP BY day, user_id;
        day_consumption_aggregation = ElectricityConsumption.objects.annotate(day=TruncDay('datetime'))\
                .values('day', 'user_id').annotate(day_total=Sum('consumption')).annotate(day_average=Avg('consumption'))
        data_frame = pd.DataFrame.from_records(day_consumption_aggregation)
        UserEConsumptionDayAggregation.objects.bulk_create(
            [
                UserEConsumptionDayAggregation(user_id = row['user_id'], day=row['day'], day_total=row['day_total'], day_average=row['day_average'])
                for row in data_frame.to_dict('records')
            ]
        )

    def __str__(self):
        return "(day:{0}, day_total:{1}, day_average:{2})".format(self.day, self.day_total_consumption, self.day_average_consumption)


class EConsumptionDayAggregation(models.Model):
    """Total and average consumptions per day are aggregated into this table for all users."""
    day = models.DateField()
    day_total = models.DecimalField(
        max_digits= 5 + math.ceil(math.log10(settings.ESTIMATED_NUM_OF_USERS * settings.CONSUMPTION_RECORD_PER_DAY)),
        decimal_places = 1) # NOTE: e.g. 9999999999999999.9
    day_average = models.DecimalField(max_digits=14, decimal_places=10) # NOTE: e.g. 9999.9999999999

    @classmethod
    def calc_consumptions(self):
        """Calc and put total and average electricity consumption into DB."""

        #
        # OPTIMIZE(Tasuku): Consider RAM when num of users is increased. And test huge datasets over and over
        #
        # NOTE(Tasuku): a statement on SQLite
        # SELECT day, SUM(consumption) as day_total, AVG(consumption) as day_average FROM(
        #    SELECT DATE(datetime) as day, consumption FROM consumption_electricityconsumption
        # ) GROUP BY day;
        day_consumption_aggregation = ElectricityConsumption.objects.annotate(day=TruncDay('datetime'))\
                .values('day').annotate(day_total=Sum('consumption')).annotate(day_average=Avg('consumption'))
        data_frame = pd.DataFrame.from_records(day_consumption_aggregation)
        EConsumptionDayAggregation.objects.bulk_create(
            [
                EConsumptionDayAggregation(day=row['day'], day_total=row['day_total'], day_average=row['day_average'])
                for row in data_frame.to_dict('records')
            ]
        )

    def __str__(self):
        return "(day:{0}, day_total:{1}, day_average:{2})".format(self.day, self.day_total, self.day_average)

