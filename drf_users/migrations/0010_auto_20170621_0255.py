# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-21 02:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drf_users', '0009_pushtoken_modified_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushtoken',
            name='device_manufacturer',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pushtoken',
            name='device_model',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pushtoken',
            name='device_platform',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pushtoken',
            name='device_serial',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pushtoken',
            name='device_version',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
