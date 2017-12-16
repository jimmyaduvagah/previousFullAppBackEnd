from django.db import models
from django.utils.text import slugify

from twz_server_django.model_mixins import CreatedModifiedModel


class Nationality(CreatedModifiedModel):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    slug = models.SlugField(blank=True, null=False, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        super(Nationality, self).save(*args, **kwargs)
