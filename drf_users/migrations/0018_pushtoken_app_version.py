# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-24 15:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drf_users', '0017_auto_20170622_0027'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushtoken',
            name='app_version',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
