# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-14 19:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_postreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='reported',
            field=models.IntegerField(default=0),
        ),
    ]
