# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# NOTE: https://qiita.com/okoppe8/items/a1149b2be54441951de1
# NOTE: https://qiita.com/pirorirori_n712/items/b47ade3fdaf8b4a109ba
# NOTE: Database access optimization, https://docs.djangoproject.com/en/3.0/topics/db/optimization/
# NOTE: Filter, https://medium.com/@hakibenita/9-django-tips-for-working-with-databases-beba787ed7d3

class User(models.Model):
    """This table is imported from data/user_data.csv, basically."""

    user_id = models.BigIntegerField(primary_key=True, db_index=True,
      validators=[MinValueValidator(0), MaxValueValidator(10 ** 10)]) # NOTE(Tasuku): Considering around 9 billion people use in 2050
    area = models.CharField(max_length=2)
    tariff = models.CharField(max_length=2)

    def __str__(self):
        return "User(user_id:{0}, area:{1}, tariff:{2})".format(self.user_id, self.area, self.tariff)


class ElectricityConsumption(models.Model):
    """This table is imported from data/consumption/<user_id>.csv, basically."""

    datetime = models.DateField(unique=True)
    consumption = models.DecimalField(max_digits=10, decimal_places=1) # TODO(Tasuku): Consider a max consumption for 'rich' family
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_sum(self): pass
    def get_average(self): pass

    def __str__(self):
        a_user = User.objects.get(user_id=self.user_id)
        return "ElectricityConsumption(datetime:{0}, consumption:{1}, {2})".format(self.datetime, self.consumption, a_user)


class ElectricityConsumptionAggregation(models.Model):
    pass
