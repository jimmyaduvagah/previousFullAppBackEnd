# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-25 12:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_experience', '0002_userprofileexperience_job_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='degree',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='degree',
            name='degree_type',
        ),
        migrations.RemoveField(
            model_name='degree',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='degreetype',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='degreetype',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='userprofileexperience',
            name='degree',
        ),
        migrations.DeleteModel(
            name='Degree',
        ),
        migrations.DeleteModel(
            name='DegreeType',
        ),
    ]
