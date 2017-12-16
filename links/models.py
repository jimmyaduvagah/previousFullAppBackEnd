from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

# Create your models here.
from twz_server_django.model_mixins import CreatedModifiedModel


class Link(CreatedModifiedModel):

    data = JSONField(default={"url": ''})

    def __str__(self):
        return '%s' % (self.data['url'], )

