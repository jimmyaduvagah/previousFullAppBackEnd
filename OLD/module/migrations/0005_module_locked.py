# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-26 14:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0004_auto_20160514_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='locked',
            field=models.BooleanField(default=False),
        ),
    ]
