# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from decimal import Decimal

from django.shortcuts import render
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

from consumption.models import User
from consumption.models import EConsumptionDayAggregation
from consumption.models import UserEConsumptionDayAggregation

def summary(request):
    return render(request, 'consumption/summary.html', {
        'total_consumptions': json.dumps(
            list(EConsumptionDayAggregation.objects.values('day', 'day_total')),
            cls=DjangoJSONEncoder
        ),
        'average_consumptions': json.dumps(
            list(EConsumptionDayAggregation.objects.values('day', 'day_average')),
            cls=DjangoJSONEncoder
        ),
        'header': ['Index', 'Area', 'Tariff', 'Action'],
        'users': list(User.objects.values('area', 'tariff', 'user_id'))
    })


def detail(request, user_id):
    return render(request, 'consumption/detail.html', {
        'user_total_consumptions': json.dumps(
            list(UserEConsumptionDayAggregation.objects.filter(user_id=user_id).values('day', 'day_total')),
            cls=DjangoJSONEncoder
        ),
        'user_average_consumptions': json.dumps(
            list(UserEConsumptionDayAggregation.objects.filter(user_id=user_id).values('day', 'day_average')),
            cls=DjangoJSONEncoder
        ),
        'user': list(User.objects.filter(user_id=user_id).values('area', 'tariff', 'user_id'))[0]
    })
