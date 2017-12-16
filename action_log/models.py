import datetime
import collections
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.postgres.fields import JSONField

class Action(models.Model):
    user = models.ForeignKey('drf_users.User', null=True, blank=True)

    name = models.CharField(max_length=100, default='Action', null=False, blank=False, db_index=True)
    method = models.CharField(max_length=10, default="", null=False, blank=True, db_index=True)
    ip = models.CharField(max_length=100, null=False, blank=False, db_index=True)
    endpoint = models.CharField(max_length=255, null=False, blank=False, db_index=True)
    date = models.DateTimeField(auto_now=True, null=False, blank=False)
    object_id = models.UUIDField(default=None, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, default=None, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    headers = JSONField(null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.user, self.name, self.endpoint,)

# objects = Action.objects.all()
# for obj in objects:
#     print 'fixing id: %s' % (obj.pk,)
#     if obj.headers != None:
#         obj.method = obj.headers['REQUEST_METHOD']
#         obj.save()
