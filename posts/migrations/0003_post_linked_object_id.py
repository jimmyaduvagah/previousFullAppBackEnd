# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-20 17:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_remove_post_linked_object_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='linked_object_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
