import time
import os
import base64
from django.core.files import File
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import  Group
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied, NotAcceptable
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import permissions
from rest_framework import status
from rest_framework import renderers
from rest_framework import viewsets

from drf_users.models import InvitationCode
from drf_users.serializers_admin import InvitationCodeAdminSerializer
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin
from twz_server_django.utils import get_client_ip, get_request_headers
from cms_locations.models import Country, State
from .models import User
from .permissions import IsAllowedOrSuperuser
from .serializers_admin import UserAdminSerializer
from .serializers import UserSerializer, GroupSerializer, UserProfileSerializer, UserProfileCreateSerializer
from twz_server_django.utils import log_action
from twz_server_django.settings import MEDIA_ROOT
from django.db.models import Q



class UserAdminViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = (IsAuthenticated,)


    def list(self, request):
        queryset = self.queryset.filter()

        log_action(request)

        exclude = request.GET.get('exclude', None)
        search_term = request.GET.get('search_term', None)
        ids = request.GET.get('ids', None)
        if search_term:
            queryset = queryset.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term)
            )

        if ids:
            queryset = queryset.filter(id__in=ids.split(','))

        if exclude:
            queryset = queryset.exclude(id__in=exclude.split(','))

        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)




class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint presents the groups in the system.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticated,)

class InvidationCodesViewSet(CreatedModifiedByModelViewSetMixin):
    """
    This endpoint presents the Invitation Codes in the system.
    """
    queryset = InvitationCode.objects.all()
    serializer_class = InvitationCodeAdminSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    pagination_class = None


class UserProfilesViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the user profiles in the system.
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,IsAllowedOrSuperuser)

    def list(self, request, *args, **kwargs):

        if request.user.is_staff or request.user.is_superuser:
            pass
        else:
            raise PermissionDenied('You do not have permission to access resource.')

        log_action(request)

        response = super(UserProfilesViewSet, self).list(self, request, *args, **kwargs)

        return response


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the user profiles in the system.
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,IsAllowedOrSuperuser)

    def list(self, request):
        queryset = self.queryset.filter()

        if request.user.pk != None:
            if request.user.userprofile != None:
                queryset = queryset.filter(pk=request.user.userprofile.pk)[0]
        else:
            raise NotAcceptable('No user profile for the current user exists.')

        log_action(request, queryset)

        serializer = self.serializer_class(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['post'], permission_classes=[IsAllowedOrSuperuser])
    def upload_user_image(self, request, pk=None):
        response = '{"details":"Accepted"}'

        image = request.FILES.get('user_image', None)

        if image != None:
            obj = User.objects.get(pk=pk)
            obj.user_image = image
            obj.save()

        log_action(request, obj)

        return Response(response)

    @detail_route(methods=['post'], permission_classes=[IsAllowedOrSuperuser])
    def upload_user_image_from_desktop(self, request, pk=None):
        response = '{"details":"Accepted"}'
        data = request.body

        if data != '':
            image_file_name = "%s/user_%s.jpg" % (MEDIA_ROOT, request.user.pk,)
            image = base64.b64decode(data);
            if os.path.isfile(image_file_name):
                image_file_name = "%s/user_%s_%s.jpg" % (MEDIA_ROOT, request.user.pk, int(time.time()),)
            f = open(image_file_name, "w")
            f.write(image)
            f.close()

            f = open(image_file_name, "r")
            obj = User.objects.get(pk=pk)
            obj.user_image = File(f)
            obj.save()
            f.close()
            os.remove(image_file_name)



        return Response(response)
