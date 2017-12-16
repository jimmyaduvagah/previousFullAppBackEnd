from django.db import models

# Create your models here.
from ordered_model.models import OrderedModel

from twz_server_django.model_mixins import CreatedModifiedModel


class Module(CreatedModifiedModel, OrderedModel):

    order_with_respect_to = 'category'

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Modules"


    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    image = models.FileField(null=True, blank=True, upload_to='module_images/')
    icon = models.FileField(null=True, blank=True, upload_to='module_images/')
    is_active = models.BooleanField(default=True)
    color = models.CharField(null=True, blank=True, max_length=50)
    has_user_assessment = models.BooleanField(default=False)
    user_assessment = models.ForeignKey('module.UserAssessment', null=True, blank=True)
    main_media = models.ForeignKey('media.Media', null=True, blank=True, related_name="module_main_media_related")
    category = models.ForeignKey('module.ModuleCategory', null=True)
    locked = models.BooleanField(default=False)

    def __str__(self):
        return u"%s | Module" % self.title


class ModuleCategory(CreatedModifiedModel, OrderedModel):

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Module Categories"

    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    image = models.FileField(null=True, blank=True, upload_to='module_category_images/')
    icon = models.FileField(null=True, blank=True, upload_to='module_category_images/')
    is_active = models.BooleanField(default=True)
    color = models.CharField(null=True, blank=False, default='#014386', max_length=50)

    def __str__(self):
        return u"%s" % self.title


class UserAssessment(CreatedModifiedModel):

    class Meta:
        ordering = ["-created_on"]

    title = models.CharField(max_length=255, null=False, blank=False)
    instructions = models.TextField(null=False, blank=False)
    group_assessment = models.BooleanField(default=False)

    def __str__(self):
        return u"%s" % self.title

