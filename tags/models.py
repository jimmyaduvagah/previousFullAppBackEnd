from django.db import models
from twz_server_django.model_mixins import CreatedModifiedModel


class Tag (CreatedModifiedModel):
    title = models.CharField(max_length=255, null=False, blank=False, unique=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title = self.title.lower()
        super(Tag, self).save(*args, **kwargs)
