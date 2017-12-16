# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-21 17:35
from __future__ import unicode_literals

from django.db import migrations, models
import uuid

def fill_mymodel_uuid(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    notification_model = apps.get_model('notifications', 'Notification')
    for obj in notification_model.objects.using(db_alias).all():
        obj.uuid = uuid.uuid4()
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='uuid',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(fill_mymodel_uuid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='notification',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, unique=True),
        ),
        # this RemoveField operation is irreversible, because in order to
        # recreate it, the primary key constraint on the UUIDField would first
        # have to be dropped.
        migrations.RemoveField('Notification', 'id'),
        migrations.RenameField(
            model_name='notification',
            old_name='uuid',
            new_name='id'
        ),
        migrations.AlterField(
            model_name='notification',
            name='id',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False, unique=True),
        ),
    ]
