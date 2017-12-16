from django.db import models

# Create your models here.
from ordered_model.models import OrderedModel

from twz_server_django.model_mixins import CreatedModifiedModel

from django.db import models


class MediaManager(models.Manager):
    pass


class Media(CreatedModifiedModel, OrderedModel):

    objects = MediaManager()
    order_with_respect_to = 'module'

    class Meta(OrderedModel.Meta):
        ordering = ['module', 'order']
        verbose_name_plural = "Media"

    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    image = models.FileField(null=True, blank=True, upload_to='media_images/')
    icon = models.FileField(null=True, blank=True, upload_to='media_images/')
    is_active = models.BooleanField(default=True)
    color = models.CharField(null=True, blank=True, max_length=50)
    video = models.CharField(max_length=255, null=False, blank=True)
    module = models.ForeignKey('module.Module', null=True)
    has_quiz = models.BooleanField(default=True)
    quiz = models.ForeignKey('quiz.Quiz', null=True, blank=True, related_name='media_quiz')

    def __str__(self):
        return u"%s | %s" % (self.title, self.module.title)


