# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-28 14:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0012_media_quiz'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='media',
            options={'ordering': ['module', 'order'], 'verbose_name_plural': 'Media'},
        ),
    ]
