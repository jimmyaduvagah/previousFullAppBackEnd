# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-13 15:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0003_auto_20160413_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='video',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
