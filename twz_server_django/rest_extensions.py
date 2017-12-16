import json

from django.contrib.auth.forms import PasswordResetForm
from django.db.utils import IntegrityError
from django.utils.text import slugify
from rest_auth.serializers import PasswordResetSerializer
from rest_framework import pagination
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, raise_errors_on_nested_writes, ReadOnlyField
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied, ValidationError
from rest_framework import viewsets, mixins

from rest_framework import permissions

from twz_server_django import settings


class BaseModelViewSet(viewsets.ModelViewSet):

    select2_serializer_class = None
    full_serializer_class = None


    def list(self, request, *args, **kwargs):
        pagination = request.GET.get('pagination', None)

        if pagination == 'false':
            self.pagination_class = None

        if request.GET.get('full', None):
            if self.full_serializer_class:
                self.serializer_class = self.full_serializer_class

        if request.GET.get('select2', None):
            if self.select2_serializer_class:
                self.serializer_class = self.select2_serializer_class


        return super(BaseModelViewSet, self).list(request, *args, **kwargs)

class ReadOnlyUserField(ReadOnlyField):
    def to_representation(self, obj):
        return obj.pk

    def to_internal_value(self, data):
        return False


class ReadOnlyChoiceDisplay(ReadOnlyField):
    choices = dict()
    def __init__(self, choices=tuple(), **kwargs):
        kwargs['read_only'] = True
        if len(choices) > 0:
            self.choices = dict(choices)

        super(ReadOnlyChoiceDisplay, self).__init__(**kwargs)

    def to_representation(self, obj):
        return self.choices.get(obj,obj)

    def to_internal_value(self, data):
        return False


class SmartTablesListMixIn(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        query = request.GET.get('query', None)
        sort = request.GET.get('sort', None)
        if query:
            query = json.loads(query)
            for field in query:
                if query[field] == 'true':
                    query[field] = True
                if query[field] == 'false':
                    query[field] = False

                if field == 'user':
                    query['user__username__icontains'] = query[field]
                    query.pop('user', None)

            self.queryset = self.queryset.filter(**query)

        if sort:
            self.queryset = self.queryset.order_by(sort)

        response = super(SmartTablesListMixIn, self).list(request, *args, **kwargs)
        return response


class CreatedModifiedByModelViewSetMixin(viewsets.ModelViewSet):
    """
    Create a model instance.
    """

    full_serializer_class = None

    def create(self, request, *args, **kwargs):
        self.check_for_full_serializer(request)
        request.data['created_by_id'] = str(request.user.id)
        request.data['modified_by_id'] = str(request.user.id)
        to_return = None
        try:
            to_return = super(CreatedModifiedByModelViewSetMixin, self).create(request, *args, **kwargs)
        except (IntegrityError, ValueError) as e:
            raise ValidationError({"detail": str(e)})

        return to_return

    def update(self, request, *args, **kwargs):
        self.check_for_full_serializer(request)
        request.data['modified_by_id'] = str(request.user.id)
        return super(CreatedModifiedByModelViewSetMixin, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.check_for_full_serializer(request)
        request.data['modified_by_id'] = str(request.user.id)
        return super(CreatedModifiedByModelViewSetMixin, self).partial_update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.check_for_full_serializer(request)
        return super(CreatedModifiedByModelViewSetMixin, self).retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.check_for_full_serializer(request)
        return super(CreatedModifiedByModelViewSetMixin, self).list(request, *args, **kwargs)

    def check_for_full_serializer(self, request):
        if request.GET.get('full', None):
            if self.full_serializer_class:
                self.serializer_class = self.full_serializer_class


class AdminViewSetMixin(CreatedModifiedByModelViewSetMixin):
    """
    Create a model instance.
    """

    def create(self, request, *args, **kwargs):
        self.is_staff(request)
        return super(AdminViewSetMixin, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.is_staff(request)
        return super(AdminViewSetMixin, self).update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.is_staff(request)
        return super(AdminViewSetMixin, self).retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.is_staff(request)
        return super(AdminViewSetMixin, self).list(request, *args, **kwargs)

    def is_staff(self, request):
        if request.user.is_staff is False:
            raise PermissionDenied()

        return True


class ReadOnlyModelViewSetMixin(viewsets.ModelViewSet):

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')


    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')


class CreateListRetrieveViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass


class SlugFilterListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A viewset that has the `retrieve`, `create`, and `list` actions.
    We also add the option to filter by a slug field, default to `slug` as the name.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.  Give a `.slug_field` attribute
    as well if you don't want to use `slug` as the field name.
    """
    slug_field = 'slug'

    def list(self, request, *args, **kwargs):
        filter_query = self.request.query_params.get(self.slug_field, None)

        if filter_query is not None:
            filter_kwargs = {'{0}__{1}'.format(self.slug_field, 'startswith'): slugify(filter_query)}
            self.queryset = self.queryset.filter(**filter_kwargs)

        return super(SlugFilterListViewSet, self).list(request, *args, **kwargs)


class CreatedModifiedByModelSerializer(ModelSerializer):

    modified_on = ReadOnlyField()
    created_on = ReadOnlyField()
    modified_by_id = serializers.UUIDField(allow_null=True)
    created_by_id = serializers.UUIDField(allow_null=True)

    def create(self, validated_data):
        return super(CreatedModifiedByModelSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(CreatedModifiedByModelSerializer, self).update(instance, validated_data)

class CreatedModifiedByModelSerializerV2(ModelSerializer):

    modified_on = ReadOnlyField()
    created_on = ReadOnlyField()
    modified_by_id = serializers.UUIDField(allow_null=True, required=False)
    created_by_id = serializers.UUIDField(allow_null=True, required=False)
    modified_by = serializers.CharField(read_only=True, required=False)
    created_by = serializers.CharField(read_only=True, required=False)

    def create(self, validated_data):
        return super(CreatedModifiedByModelSerializerV2, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(CreatedModifiedByModelSerializerV2, self).update(instance, validated_data)


class P33ModelSerializer(ModelSerializer):

    modified_on = ReadOnlyField()
    created_on = ReadOnlyField()
    modified_by = ReadOnlyUserField()
    created_by = ReadOnlyUserField()


class CreatedModifiedByHyperlinkedModelSerializer(CreatedModifiedByModelSerializer, HyperlinkedModelSerializer):
    pass



class LimitOffsetPagination(pagination.LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response({
            'state' : {
                'next_offset': self.get_next_offset(),
                'prev_offset': self.get_prev_offset(),
                'limit': self.limit,
                'total': self.count
            },
            'results': data,
        })

    def get_next_offset(self):
        return self.offset + self.limit

    def get_prev_offset(self):
        prev_offset = self.offset - self.limit
        if self.offset == 0:
            return None
        elif prev_offset < 0:
            return 0
        else:
            return prev_offset


from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class UserCreateForOwnUserPermission(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        if str(request.user.id) != request.data.get('user_id'):
            raise PermissionDenied('Tried to create an object for a user other then the currently logged in user.')

        return super(UserCreateForOwnUserPermission, self).create(request, *args, **kwargs)


class IsAllowedOrSuperuser(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):

        if request.user.is_superuser or request.user.is_staff:
            return True

        if obj.user_id == request.user.id:
            return True
        else:
            return False


class TWPasswordResetSerializer(serializers.Serializer):

    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()

    password_reset_form_class = PasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {
            'subject_template_name': 'emails/registration/password_reset_subject.txt',
            'email_template_name': 'emails/registration/password_reset_email.html',
            'html_email_template_name': 'emails/registration/password_reset_email_html.html',
        }

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)

