# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-13 15:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
