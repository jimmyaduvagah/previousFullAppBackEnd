import time
import os
import base64
from django.core.files import File
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied, NotAcceptable, MethodNotAllowed
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from cms_locations.models import Country, State
from courses.serializers_admin import CourseProgressAdminSerializer, CourseProgressFullAdminSerializer
from twz_server_django.utils import log_action
from twz_server_django.settings import MEDIA_ROOT
from twz_server_django.rest_extensions import LimitOffsetPagination, CreatedModifiedByModelViewSetMixin, \
    SmartTablesListMixIn, IsAllowedOrSuperuser
from .models import Course, CourseSection, CourseSectionType, Specialty, COURSE_STATE_CHOICES, CourseProgress
from .serializers_admin import CourseAdminSerializer, CourseSectionAdminSerializer, CourseSectionTypeAdminSerializer, SpecialtyAdminSerializer
import json
import mimetypes

class CourseAdminViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Course.objects.all()
    serializer_class = CourseAdminSerializer
    permission_classes = (IsAdminUser,)
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
        serializer = CourseSectionAdminSerializer(queryset, many=True, context={'request': request})

        return Response(serializer.data)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated,])
    def simplelist(self, request, *args, **kwargs):
        queryset = self.queryset.filter().order_by('order').values('id','title')


        return Response(list(queryset))


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        log_action(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @list_route(methods=['post'], permission_classes=[IsAuthenticated,])
    def reorder(self, request, *args, **kwargs):
        list = request.data
        for item in list:
            obj = Course.objects.get(id=item['id'])
            obj.order = item['order']
            obj.save()

        return Response('')


class CourseStatusAdminViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAdminUser,)


    def list(self, request):
        COURSE_STATE_CHOICES
        output = []
        for state in COURSE_STATE_CHOICES:
            output.append({
                "id": state[0],
                "title": state[1]
            })

        return Response(output)



class CourseSectionAdminViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = CourseSection.objects.all()
    serializer_class = CourseSectionAdminSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request):
        queryset = self.queryset.filter()

        log_action(request)

        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        log_action(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @list_route(methods=['post'], permission_classes=[IsAuthenticated,])
    def reorder(self, request, *args, **kwargs):
        list = request.data
        for item in list:
            obj = CourseSection.objects.get(id=item['id'])
            obj.order = item['order']
            obj.save()

        return Response('')



class CourseSectionTypeAdminViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = CourseSectionType.objects.all()
    serializer_class = CourseSectionTypeAdminSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request):
        queryset = self.queryset.filter()

        log_action(request)

        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        log_action(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class SpecialtyAdminViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtyAdminSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request):
        queryset = self.queryset.filter()

        log_action(request)

        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        log_action(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


from attachments.models import Attachment
from attachments.serializers import AttachmentSerializer

class CourseSectionFileUploadViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the user profiles in the system.
    """
    queryset = CourseSection.objects.all()
    serializer_class = CourseSectionAdminSerializer
    permission_classes = (IsAdminUser, IsAllowedOrSuperuser)
    parser_classes = (MultiPartParser,FormParser,FileUploadParser,)

    def list(self, request):
        raise MethodNotAllowed('GET')

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')

    def update(self, request, pk=None):
        file = request.FILES.get('file', None)
        obj = CourseSection.objects.get(pk=pk)
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

class CourseProgressAdminViewSet(CreatedModifiedByModelViewSetMixin, SmartTablesListMixIn):
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressAdminSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = LimitOffsetPagination

    def list(self, request, *args, **kwargs):
        log_action(request)

        response = super(CourseProgressAdminViewSet, self).list(request, *args, **kwargs)
        return response


    def retrieve(self, request, *args, **kwargs):
        log_action(request)

        if request.GET.get('full', None):
            self.serializer_class = CourseProgressFullAdminSerializer

        response = super(CourseProgressAdminViewSet, self).retrieve(request, *args, **kwargs)
        return response

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied()

        return Response('')

    def update(self, request, *args, **kwargs):
        log_action(request)
        response = super(CourseProgressAdminViewSet, self).update(request, *args, **kwargs)
        return response

    def create(self, request, *args, **kwargs):
        log_action(request)
        response = super(CourseProgressAdminViewSet, self).create(request, *args, **kwargs)
        return response

    @list_route(methods=['get'], permission_classes=[IsAuthenticated,])
    def projects(self, request, *args, **kwargs):
        log_action(request)

        if request.GET.get('full', None):
            self.serializer_class = CourseProgressFullAdminSerializer


        section_id = request.GET.get('section_id', None)

        sections = CourseSection.objects.filter(course_section_type__title='Project')
        search = None

        if section_id is not None:
            query = {
                'sections':{
                    str(section_id):{
                    }
                }
            }
            search = Q(object__contains=query)
        else:

            for section in sections:
                query = {
                    'sections':{
                        str(section.id):{
                            'project': {
                                'done': True
                            }
                        }
                    }
                }

                if search is None:
                    search = Q(object__contains=query)
                else:
                    search = search | Q(object__contains=query)




        self.queryset = self.queryset.filter(search)

        response = super(CourseProgressAdminViewSet, self).list(request, *args, **kwargs)
        return response
