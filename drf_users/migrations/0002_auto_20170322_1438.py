# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-22 14:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('towns', '0001_initial'),
        ('drf_users', '0001_initial'),
        ('nationalities', '0001_initial'),
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='place_of_birth',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_place_of_birth', to='towns.Town'),
        ),
        migrations.AddField(
            model_name='user',
            name='town_of_residence',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_town_of_residence', to='towns.Town'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AddField(
            model_name='user',
            name='nationality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nationalities.Nationality'),
        ),
    ]
