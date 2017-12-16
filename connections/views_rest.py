from uuid import UUID

import django_filters
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q
from django.utils import timezone

from connections.models import Connection, ConnectionRequest
from connections.serializers import ConnectionSerializer, ConnectionRequestSerializer, ConnectionRequestToSerializer, \
    ConnectionRequestFromSerializer
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import NotAuthenticated, MethodNotAllowed, NotAcceptable, PermissionDenied, NotFound, \
    ParseError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_users.models import PushToken
from ionic_api.request import PushNotificationRequest
from notifications.models import Notification
from twz_server_django.notification_types import NOTIFICATION_TYPES
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin
from twz_server_django.settings_private import IONIC_PUSH_GROUP


class ConnectionViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Connection.objects.get_queryset()
    serializer_class = ConnectionSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter, )
    search_fields = ('to_user__first_name', 'to_user__last_name', 'to_user__town_of_residence__name')

    def list(self, request, *args, **kwargs):
        self.queryset = Connection.objects.get_active().filter(from_user=request.user)
        return super(ConnectionViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def for_user(self, request, *args, **kwargs):
        for_user = request.GET.get('user', None)
        if for_user is not None:
            self.queryset = Connection.objects.get_active().filter(from_user=for_user)
            return super(ConnectionViewSet, self).list(request, *args, **kwargs)
        else:
            raise NotFound()

    @detail_route(methods=['put'])
    def remove(self, request, *args, **kwargs):
        self.queryset = Connection.objects.get_active()

        instance = self.get_object()
        if instance.from_user.id == request.user.id:
            instance.state = 'I'
            instance.modified_by_id = request.user.id
            instance.save()

            other_instance = Connection.objects.get_active().filter(from_user=instance.to_user, to_user=instance.from_user)
            other_instance.state = 'I'
            other_instance.modified_by_id = request.user.id
            other_instance.save()

            return Response({"detail": ("You are no longer friends with %s" % instance.to_user)})
        else:
            raise PermissionDenied()

    @list_route(methods=['put'])
    def remove_with_userid(self, request, *args, **kwargs):
        try:
            to_user_id = UUID(request.data['to_user_id'])
        except ValueError:
            raise ParseError('to_user_id is a badly formed hexadecimal UUID string')
        from_user_id = request.user.id
        self.queryset = Connection.objects.get_active()

        try:
            instance = self.queryset.get(to_user_id=to_user_id, from_user_id=from_user_id)
        except ObjectDoesNotExist:
            raise NotFound('You are not connected to this user.')

        if instance.from_user.id == request.user.id:
            instance.state = 'I'
            instance.modified_by_id = request.user.id
            instance.save()

            other_instance = Connection.objects.get_active().get(from_user_id=to_user_id, to_user_id=from_user_id)
            other_instance.state = 'I'
            other_instance.modified_by_id = request.user.id
            other_instance.save()

            return Response({"detail": ("You are no longer friends with %s" % instance.to_user)})
        else:
            raise PermissionDenied()

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_superuser is not True:
            self.queryset = self.queryset.filter(from_user_id=request.user.id)
        return super(ConnectionViewSet, self).retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')


class ConnectionRequestViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = ConnectionRequest.objects.get_queryset()
    serializer_class = ConnectionRequestSerializer
    permission_classes = (IsAuthenticated,)
    # filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    # filter_class = CourseFilter

    @detail_route(methods=['put'])
    def accept(self, request, *args, **kwargs):
        self.queryset = ConnectionRequest.objects.get_visible()

        instance = self.get_object()
        if instance.state == 'P':
            if instance.to_user.id == request.user.id:
                instance.state = 'A'
                instance.modified_by_id = request.user.id
                instance.save()

                Connection.objects.create(
                    from_user=instance.from_user,
                    to_user=instance.to_user,
                    state='A',
                    created_by=instance.from_user,
                    modified_by=instance.from_user
                )
                my_connection = Connection.objects.create(
                    from_user=instance.to_user,
                    to_user=instance.from_user,
                    state='A',
                    created_by=instance.to_user,
                    modified_by=instance.from_user
                )

                tokens = PushToken.objects.filter(user=instance.from_user,
                                                  push_group=IONIC_PUSH_GROUP,
                                                  is_active=True).values_list('token')

                tokens_list = list()
                for token in tokens:
                    tokens_list.append(token[0])

                payload = {
                    "image": request.user.get_profile_image_cache_url(),
                    "connection_request_id": str(instance.id),
                    "created_by_id": str(request.user.id),
                    "type": NOTIFICATION_TYPES.CONNECTION_REQUEST_APPROVED
                }
                title = "You have a new friend!"
                message = "%s accepted your connection request" % str(request.user)
                notif = Notification(to_user=instance.from_user,
                                     from_user=request.user,
                                     created_on=my_connection.created_on,
                                     title=title,
                                     message=message,
                                     payload=payload)
                notif.save()

                if len(tokens_list) > 0:
                    r = PushNotificationRequest()
                    r.create({
                        "tokens": list(tokens_list),
                        "notification": {
                            "message": message,
                            "title": title,
                            "payload": payload,
                            "ios": {
                                "badge": "1",
                                "sound": "default",
                                "priority": 10
                            },
                            "android": {
                                "sound": "default",
                                "priority": "high"
                            }
                        },
                        "profile": IONIC_PUSH_GROUP
                    })

                return Response(ConnectionSerializer(my_connection).data)
            else:
                raise PermissionDenied()
        elif instance.state == 'A':
            return Response({"detail": "You are already friends."})
        else:
            raise NotFound()

    @detail_route(methods=['put'])
    def reject(self, request, *args, **kwargs):
        self.queryset = ConnectionRequest.objects.get_visible()

        instance = self.get_object()
        if instance.state == 'P':
            if instance.to_user.id == request.user.id:
                instance.state = 'R'
                instance.modified_by_id = request.user.id
                instance.save()

                return Response({"detail": "Connection request was rejected."})
            else:
                raise PermissionDenied()
        elif instance.state == 'A':
            return Response({"detail": "You are already friends."})
        else:
            raise NotFound()

    @detail_route(methods=['put'])
    def withdraw(self, request, *args, **kwargs):
        self.queryset = ConnectionRequest.objects.get_visible()

        instance = self.get_object()
        if instance.state == 'P':
            if instance.from_user.id == request.user.id:
                instance.state = 'W'
                instance.modified_by_id = request.user.id
                instance.save()

                return Response({"detail": "Connection request was withdrawn."})
            else:
                raise PermissionDenied()
        elif instance.state == 'A':
            return Response({"detail": "You are already friends."})
        else:
            raise NotFound()

    @list_route(methods=['get'])
    def my_sent_requests(self, request, *args, **kwargs):
        self.queryset = ConnectionRequest.objects.get_pending().filter(from_user_id=request.user.id)
        self.serializer_class = ConnectionRequestFromSerializer
        return super(ConnectionRequestViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def my_received_requests(self, request, *args, **kwargs):
        self.queryset = ConnectionRequest.objects.get_pending().filter(to_user_id=request.user.id)
        self.serializer_class = ConnectionRequestToSerializer
        return super(ConnectionRequestViewSet, self).list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        q = Q(
            Q(from_user_id=request.user.id) | Q(to_user_id=request.user.id)
        )
        self.queryset = ConnectionRequest.objects.get_pending().filter(q)
        return super(ConnectionRequestViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        q = Q(
            Q(to_user_id=request.user.id) | Q(from_user_id=request.user.id)
        )
        self.queryset = ConnectionRequest.objects.filter(q)
        if len(self.queryset) > 0:
            return super(ConnectionRequestViewSet, self).retrieve(request, *args, **kwargs)
        else:
            raise MethodNotAllowed('GET')

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')

    def create(self, request, *args, **kwargs):
        request.data['from_user_id'] = request.user.id
        to_user_id = request.data['to_user_id']

        check_for_pending_request = ConnectionRequest.objects.get_pending().filter(from_user_id=request.user.id, to_user_id=to_user_id)
        if len(check_for_pending_request) > 0:
            return Response({"detail": "A request is currently pending."}, status=409)

        check_for_connection = Connection.objects.get_active().filter(from_user_id=request.user.id, to_user_id=to_user_id)
        if len(check_for_connection) > 0:
            return Response({"detail": "You are already friends."}, status=409)

        self.serializer_class = ConnectionRequestToSerializer
        response = super(ConnectionRequestViewSet, self).create(request, *args, **kwargs)

        tokens = PushToken.objects.filter(user_id=to_user_id,
                                          push_group=IONIC_PUSH_GROUP,
                                          is_active=True).values_list('token')

        tokens_list = list()
        for token in tokens:
            tokens_list.append(token[0])

        payload = {
            "image": request.user.get_profile_image_cache_url(),
            "connection_request_id": str(response.data['id']),
            "created_by_id": str(request.data['from_user_id']),
            "type": NOTIFICATION_TYPES.CONNECTION_REQUEST
        }
        title = "%s wants to connect" % str(request.user)
        message = "View the request"
        print(response.data)
        notif = Notification(to_user_id=to_user_id,
                             from_user_id=request.data['from_user_id'],
                             created_on=timezone.datetime.now(),
                             title=title,
                             message=message,
                             payload=payload)
        notif.save()

        if len(tokens_list) > 0:
            r = PushNotificationRequest()
            r.create({
                "tokens": list(tokens_list),
                "notification": {
                    "message": message,
                    "title": title,
                    "payload": payload,
                    "ios": {
                        "badge": "1",
                        "sound": "default",
                        "priority": 10
                    },
                    "android": {
                        "sound": "default",
                        "priority": "high"
                    }
                },
                "profile": IONIC_PUSH_GROUP
            })

        return response
