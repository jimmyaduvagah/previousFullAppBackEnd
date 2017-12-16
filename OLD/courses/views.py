import time
import os
import base64
from django.core.files import File
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied, NotAcceptable, NotFound, MethodNotAllowed
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions, viewsets, status
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser

from attachments.models import Attachment
from attachments.serializers import AttachmentSerializer
from cms_locations.models import Country, State
from courses.serializers import CourseProgressFullSerializer
from twz_server_django.utils import log_action
from twz_server_django.settings import MEDIA_ROOT
from twz_server_django.rest_extensions import LimitOffsetPagination, CreatedModifiedByModelViewSetMixin, \
    UserCreateForOwnUserPermission, IsAllowedOrSuperuser
from .models import Course, CourseSection, CourseSectionType, Specialty, COURSE_STATE_CHOICES, CourseProgress
from .serializers import CourseSerializer, CourseFullSerializer, CourseSectionFullSerializer, SpecialtySerializer, SpecialtyFullSerializer, CourseProgressSerializer
import json


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.filter(state='PUB')
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter().order_by('order')

        log_action(request)
        filter = {}
        filter['specialty'] = request.GET.get('filter_specialty', None)

        if filter['specialty']:
            queryset = queryset.filter(specialty=filter['specialty'])

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'], permission_classes=[IsAuthenticated,])
    def sections(self, request, *args, **kwargs):
        queryset = CourseSection.objects.all().order_by('order')
        queryset = queryset.filter(course_id=kwargs['pk'])
        serializer = CourseSectionFullSerializer(queryset, many=True, context={'request': request})

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        log_action(request, instance)

        serializer = self.get_serializer(instance, context={'request': request})

        if request.GET.get('full', None):
            serializer = CourseFullSerializer(instance, context={'request': request})

        return Response(serializer.data)

class SpecialtyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def list(self, request):
        queryset = self.queryset.filter()

        log_action(request)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        log_action(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CourseProgressViewSet(CreatedModifiedByModelViewSetMixin, UserCreateForOwnUserPermission):
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    full_serializer_class  = CourseProgressFullSerializer
    permission_classes = (IsAuthenticated,IsAllowedOrSuperuser)
    pagination_class = None

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user, course__state='PUB')
        if (request.GET.get('full', None)):
            self.serializer_class = self.full_serializer_class

        log_action(request)
        response = super(CourseProgressViewSet, self).list(request, *args, **kwargs)
        return response


    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)
        response = super(CourseProgressViewSet, self).retrieve(request, *args, **kwargs)
        return response

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied()

        return Response('')

    def update(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)

        if kwargs.get('upload', None):
            response = self.upload_file(request, *args, **kwargs)
        else:
            response = super(CourseProgressViewSet, self).update(request, *args, **kwargs)

        return response

    def create(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)

        response = super(CourseProgressViewSet, self).create(request, *args, **kwargs)
        return response


class CourseProgressFileUploadViewSet(CreatedModifiedByModelViewSetMixin, UserCreateForOwnUserPermission):
    """
    This endpoint presents the user profiles in the system.
    """
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)
    parser_classes = (MultiPartParser,FormParser,FileUploadParser,)

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.GET.get('delete_attachment'):
            attachment_id = request.GET.get('attachment_id', None)
            if attachment_id:
                attachment = Attachment.objects.filter(id=attachment_id)
                if len(attachment) > 0:
                    print("deleting-%s" % (attachment[0].id,))
                    attachment[0].delete()

            else:
                raise NotAcceptable('No id was supplied.')

            response = '{"detail":"deleted"}'
            return Response(response, status=200)
        else:
            raise MethodNotAllowed('DELETE')


    def update(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)

        file = request.FILES.get('file', None)
        obj = self.get_object()
        mime_type = ''
        #raw data upload
        if file != None:
            mime_type= request.META.get('CONTENT_TYPE','')

        #multipart form upload
        elif request.data.get('file[file]', None):
            file = request.data.get('file[file]', None)
            mime_type = file.content_type

        if file != None:
            attachment = Attachment.objects.save_attachment_for_object(
                obj=obj,
                file=file,
                mime_type=mime_type,
                request=request
            )

            # log_action(request, attachment)
            response = AttachmentSerializer(attachment)
            return Response(response.data, status=201)
        else:
            response = '{"detail":"No File"}'
            # log_action(request)
            return Response(response, status=406)

class CourseProgressObjectViewSet(viewsets.GenericViewSet):
    model = CourseProgress
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)
    pagination_class = None

    def list(self, request, *args, **kwargs):
        course_id = request.GET.get('course_id', None)
        if course_id:
            object = self.model.objects.get_for_user_and_course(user_id=request.user.id, course_id=course_id )
            serializer = self.serializer_class(object, many=False, context={'request': request})
            return Response(serializer.data)
        else:
            raise PermissionDenied()



    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)
        return Response('')

