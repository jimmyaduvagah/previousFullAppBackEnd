# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-16 01:08
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_courseprogress_last_opened'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseprogress',
            name='completed_on',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='courseprogress',
            name='ended_on',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='courseprogress',
            name='last_opened',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='courseprogress',
            name='total_time_viewing',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
