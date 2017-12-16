import uuid

from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

# Create your models here.

class Notification(models.Model):

    class Meta:
        ordering = ['-created_on']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_user = models.ForeignKey('drf_users.User', null=False, blank=False, related_name='from_user')
    to_user = models.ForeignKey('drf_users.User', null=False, blank=False, related_name='to_user')
    created_on = models.DateTimeField(auto_created=True)
    modified_on = models.DateTimeField(auto_now=True, editable=True)
    is_seen = models.BooleanField(default=False)
    when_seen = models.DateTimeField(null=True, blank=True)
    payload = JSONField(null=False, blank=False, default={})
    title = models.CharField(null=False, blank=False, max_length=255)
    message = models.CharField(null=False, blank=False, max_length=255)

    def __str__(self):
        return u"%s - %s to %s" % (self.message, self.from_user, self.to_user)
