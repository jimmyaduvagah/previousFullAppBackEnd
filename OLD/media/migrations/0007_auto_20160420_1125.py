# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 11:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0006_auto_20160413_2314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mediacategory',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='mediacategory',
            name='modified_by',
        ),
    ]
