from django.db import models

from twz_server_django.model_mixins import CreatedModifiedModel



class InstitutionType(CreatedModifiedModel):
    title = models.CharField(max_length=255, blank=False, null=False)
    is_active = models.BooleanField(default=True, null=False)

    def __str__(self):
        return "%s" % self.title

class Institution(CreatedModifiedModel):
    title = models.CharField(max_length=255, blank=False, null=False)
    type = models.ForeignKey(InstitutionType)
    is_active = models.BooleanField(default=True, null=False)

    def __str__(self):
        return "%s - %s" % (self.title, self.type,)
