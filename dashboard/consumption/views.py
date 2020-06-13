# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import render
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

from consumption.models import User, ElectricityConsumptionDayAggregation

def summary(request):
    from django.conf import settings

    #NOTE: https://qiita.com/kytiken/items/6f22b538ef67b9ea6f1e
    consumptions = {
        'day_totals': list(ElectricityConsumptionDayAggregation.objects.values('day', 'day_total')),
        'day_averages': list(ElectricityConsumptionDayAggregation.objects.values('day', 'day_average'))
    }

    return render(request, 'consumption/summary.html', {
        'consumptions': json.dumps(consumptions, cls=DjangoJSONEncoder)
    })


def detail(request):
    context = {
    }
    return render(request, 'consumption/detail.html', context)
