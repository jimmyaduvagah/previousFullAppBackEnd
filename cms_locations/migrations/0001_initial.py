# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-22 14:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('abbreviation', models.CharField(db_index=True, max_length=3)),
            ],
            options={
                'verbose_name_plural': 'Countries',
                'verbose_name': 'Country',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('abbreviation', models.CharField(db_index=True, max_length=3)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms_locations.Country')),
            ],
            options={
                'verbose_name_plural': 'States',
                'verbose_name': 'State',
            },
        ),
    ]
