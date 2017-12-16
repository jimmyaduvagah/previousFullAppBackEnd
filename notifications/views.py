import django_filters
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class IsMyNotification(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.to_user_id == request.user.id


class NotificationFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Notification
        fields = ['from_user', 'to_user', 'is_seen']


class NotificationViewset(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated, IsMyNotification)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = NotificationFilter

    def list(self, request, *args, **kwargs):
        response = super(NotificationViewset, self).list(request, *args, **kwargs)
        return response

    def get_queryset(self):
        qs = Notification.objects.filter(to_user=self.request.user)
        return qs

    def create(self, request, *args, **kwargs):
        response = super(NotificationViewset, self).create(request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        response = super(NotificationViewset, self).update(request, *args, **kwargs)
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super(NotificationViewset, self).retrieve(request, *args, **kwargs)
        return response

    def destroy(self, request, *args, **kwargs):
        response = super(NotificationViewset, self).destroy(request, *args, **kwargs)
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super(NotificationViewset, self).partial_update(request, *args, **kwargs)
        return response

