from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

# Create your models here.
from twz_server_django.model_mixins import CreatedModifiedModel


class Quiz(CreatedModifiedModel):

    object = JSONField(null=False, blank=True, default=dict)
    title = models.CharField(max_length=255, blank=False, null=False)
    instructions = models.TextField(blank=True, null=False, default='')

    def __str__(self):
        return "%s" % self.title