# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2020-06-12 15:23
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ElectricityConsumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateField()),
                ('consumption', models.DecimalField(decimal_places=1, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='ElectricityConsumptionAggregation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('date_total', models.DecimalField(decimal_places=1, max_digits=80000000000)),
                ('date_average', models.DecimalField(decimal_places=1, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.BigIntegerField(db_index=True, primary_key=True, serialize=False, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10000000000)])),
                ('area', models.CharField(max_length=4)),
                ('tariff', models.CharField(max_length=4)),
            ],
        ),
        migrations.AddField(
            model_name='electricityconsumption',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consumption.User'),
        ),
    ]
