# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-24 23:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course_module_sections', '0012_sectionsurveygroup'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sectionsurveygroup',
            old_name='survey_group',
            new_name='survey_group_id',
        ),
    ]
