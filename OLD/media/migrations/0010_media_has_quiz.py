# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0009_remove_media_parent_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='has_quiz',
            field=models.BooleanField(default=True),
        ),
    ]
