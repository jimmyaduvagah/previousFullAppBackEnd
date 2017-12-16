import json

from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from django.db.models.query_utils import Q
from ordered_model.models import OrderedModel

from twz_server_django.model_mixins import CreatedModifiedModel, CreatedModifiedModelManager


class ConnectionManager(CreatedModifiedModelManager):

    def get_queryset(self, *args, **kwargs):
        qs = super(ConnectionManager, self).get_queryset()
        return qs

    def get_active(self, *args, **kwargs):
        qs = super(ConnectionManager, self).get_queryset().filter(state='A')
        return qs


CONNECTION_STATE_CHOICES = (
    ("A", "Active"),
    ("I", "Inactive"),
)
CONNECTION_STATE_CHOICES_MAP = {
    "A": "Active",
    "I": "Inactive",
}


class Connection(CreatedModifiedModel):

    objects = ConnectionManager()

    from_user = models.ForeignKey('drf_users.User', blank=False, null=False, related_name='connection_from_user')
    to_user = models.ForeignKey('drf_users.User', blank=False, null=False, related_name='connection_to_user')
    state = models.CharField(choices=CONNECTION_STATE_CHOICES, default='A', max_length=1, null=False, blank=False)

    def __str__(self):
        return u"%s's Connection To %s" % (self.from_user, self.to_user)


class ConnectionRequestManager(CreatedModifiedModelManager):

    class Meta:
        ordering = ['-created_on',]

    def get_queryset(self, *args, **kwargs):
        qs = super(ConnectionRequestManager, self).get_queryset()
        return qs

    def get_pending(self, *args, **kwargs):
        qs = super(ConnectionRequestManager, self).get_queryset().filter(state='P')
        return qs

    def get_accepted(self, *args, **kwargs):
        qs = super(ConnectionRequestManager, self).get_queryset().filter(state='A')
        return qs

    def get_visible(self, *args, **kwargs):
        q = Q(
            Q(state='P') | Q(state='A')
        )
        qs = super(ConnectionRequestManager, self).get_queryset().filter(q)
        return qs


CONNECTION_REQUEST_STATE_CHOICES = (
    ("P", "Pending"),
    ("A", "Accepted"),
    ("R", "Rejected"),
    ("W", "Withdrawn"),
    ("B", "Blocked"),
)
CONNECTION_REQUEST_STATE_CHOICES_MAP = {
    "P": "Pending",
    "A": "Accepted",
    "R": "Rejected",
    "W": "Withdrawn",
    "B": "Blocked",
}


class ConnectionRequest(CreatedModifiedModel):

    class Meta:
        ordering = ['-created_on',]

    objects = ConnectionRequestManager()

    from_user = models.ForeignKey('drf_users.User', blank=False, null=False, related_name='connection_request_from_user')
    to_user = models.ForeignKey('drf_users.User', blank=False, null=False, related_name='connection_request_to_user')
    state = models.CharField(choices=CONNECTION_REQUEST_STATE_CHOICES, default='P', max_length=1, null=False, blank=False)

    def __str__(self):
        return u"%s's Connection Request To %s is %s" % (self.from_user, self.to_user, CONNECTION_REQUEST_STATE_CHOICES_MAP[self.state])
