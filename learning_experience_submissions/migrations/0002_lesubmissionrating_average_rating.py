# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-11 19:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_experience_submissions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesubmissionrating',
            name='average_rating',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
