# -*- coding: utf-8 -*-
# Generated by Django 1.9c2 on 2016-01-26 02:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_specialty_color'),
        ('assessments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='course',
            field=models.ForeignKey(default='00000000-0000-0000-0000-000000000000', on_delete=django.db.models.deletion.CASCADE, to='courses.Course'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='assessment',
            name='course_progress',
            field=models.ForeignKey(default='00000000-0000-0000-0000-000000000000', on_delete=django.db.models.deletion.CASCADE, to='courses.CourseProgress'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='assessment',
            name='course_section',
            field=models.ForeignKey(default='00000000-0000-0000-0000-000000000000', on_delete=django.db.models.deletion.CASCADE, to='courses.CourseSection'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='assessment',
            name='user_who_assessed',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_user_who_assessed', to=settings.AUTH_USER_MODEL),
        ),
    ]
