# -*- coding: utf-8 -*-
# Generated by Django 1.9c2 on 2016-01-26 02:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0002_auto_20160126_0215'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assessmentcomment',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='assessmentcomment',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='assessmentcomment',
            name='user',
        ),
        migrations.AddField(
            model_name='assessment',
            name='comment',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='AssessmentComment',
        ),
    ]
