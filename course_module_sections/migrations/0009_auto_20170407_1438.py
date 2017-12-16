# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-07 14:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_module_sections', '0008_sectionquiz'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectiontext',
            name='html',
            field=models.TextField(blank=True, help_text='This is auto generated from Text.'),
        ),
        migrations.AlterField(
            model_name='sectiontext',
            name='text',
            field=models.TextField(blank=True, help_text='Markdown can be used here.'),
        ),
    ]
