# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-17 14:48
from __future__ import unicode_literals

from django.db import migrations, models
import drf_users.models
import storages.backends.s3boto


class Migration(migrations.Migration):

    dependencies = [
        ('drf_users', '0003_user_verification_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, storage=storages.backends.s3boto.S3BotoStorage(acl='public-read', bucket='twz-dev-public'), upload_to=drf_users.models.profile_file_name),
        ),
    ]
