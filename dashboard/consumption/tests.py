# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from consumption.models import User, ElectricityConsumption

# Create your tests here.

    def tmp():
        User.objects.all().delete()
        ElectricityConsumption.objects.all().delete()

        user = User()
        user.user_id = 2
        user.area = "a1"
        user.tariff = "t2"
        user.save()
        e_consumption = ElectricityConsumption()
        e_consumption.datetime = datetime.strptime('2016-07-15 02:00:00', settings.CSV_DATETIME_FORMAT)
        e_consumption.consumption = 28.2
        e_consumption.user_id = user.user_id
        e_consumption.save()

        e_consumption = ElectricityConsumption()
        e_consumption.datetime = datetime.strptime('2016-07-20 14:00:00', settings.CSV_DATETIME_FORMAT)
        e_consumption.consumption = 14.7
        e_consumption.user_id = user.user_id
        e_consumption.save()
        #print(user)
        #print(e_consumption)

        records = ElectricityConsumption.objects.select_related('user').filter(consumption__gt=15)
        for r in records:
            print(r)