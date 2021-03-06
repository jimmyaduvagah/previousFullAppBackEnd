# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-10 20:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='nationalities_nationality_created_by_related', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='nationalities_nationality_modified_by_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
