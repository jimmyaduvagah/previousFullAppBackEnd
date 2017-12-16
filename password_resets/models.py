import datetime

from django.utils import timezone
from django.db import models

# Create your models here.

from twz_server_django.model_mixins import CreatedModifiedModel

class PasswordResetTokenManager(models.Manager):

    def invalidate_tokens_for_user(self, user):
        tokens = self.filter(user=user)
        for token in tokens:
            token.valid = False
            token.save()

class PasswordResetToken(CreatedModifiedModel):

    objects = PasswordResetTokenManager()

    user = models.ForeignKey('drf_users.User')
    valid = models.BooleanField(default=True)
    used = models.BooleanField(default=False)
    used_on = models.DateTimeField(null=True, blank=True)
    requested_on = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return u"%s" % self.id

    def is_valid(self):
        if self.valid:
            if self.requested_on > timezone.now()-datetime.timedelta(hours=2):
                return True
            else:
                self.valid = False
                self.save()
                return False
        else:
            return False
