import hashlib
import json
import time
import os
import random
from simplejson.decoder import JSONDecodeError
from uuid import UUID

import binascii

import boto3
import markdown
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import UploadedFile
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import Group
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework.mixins import ListModelMixin, CreateModelMixin

from drf_users.models import PhoneVerificationCode, PushToken
from drf_users.permissions import IsUserOrSuperuser
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied, NotAcceptable, MethodNotAllowed, NotFound, ParseError
from rest_framework.filters import SearchFilter
from tempfile import NamedTemporaryFile
from rest_framework.decorators import detail_route, list_route, api_view
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework import status
from rest_framework import viewsets

from drf_users.serializers import UserUpdateSerializer, UserMinimalWithFriendshipSerializer, PushTokenSerializer, \
    UserNotMeSerializer
from ionic_api.request import PushTokenRequest, PushTokenRequestOptions, PushMessageRequest, PushNotificationRequest, \
    PushNotificationRequestOptions
from ionic_api.response import OKResponse, ErrorResponse
from nationalities.models import Nationality
from towns.models import Town
from twz_server_django.notification_types import NOTIFICATION_TYPES
from twz_server_django.settings_private import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, IONIC_PUSH_GROUP
from twz_server_django.utils import sendSMS, generateVerificationCode
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin
from cms_locations.models import Country, State
from .models import User, InvitationCode
from .permissions import IsAllowedOrSuperuser
from .serializers import UserSerializer, GroupSerializer, UserProfileSerializer, UserProfileCreateSerializer, UserRegisterSerializer, UserFullSerializer
from twz_server_django.utils import log_action
from twz_server_django.settings import APP_USER_VERIFIED_PATH, APP_USER_VERIFICATION_FAILED


class IsMeOrAdmin(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.id == obj.id:
            return True

        return False


# from .models import Snippet
def codegenerator():
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pw_length = 8
    mypw = ""

    for i in range(pw_length):
        next_index = random.randrange(len(alphabet))
        mypw = mypw + alphabet[next_index]
    return mypw


class UserLogoutViewSet(viewsets.GenericViewSet, CreateModelMixin):
    queryset = PushToken.objects.all()

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed('get')

    def create(self, request, *args, **kwargs):
        body = request.body.decode('utf-8')
        if len(body) > 0:
            try:
                data = json.loads(body)
            except JSONDecodeError:
                raise ParseError()

        tokens = []
        if 'device_id' in data:
            tokens = PushToken.objects.filter(user=request.user, device_id=data['device_id'], is_active=True)
        else:
            # tokens = PushToken.objects.filter(user=request.user, is_active=True)
            pass

        if len(tokens) > 0:
            for token in tokens:
                token.invalidate()

        return Response({
            "detail": "You are now logged out"
        })

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('put')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('patch')

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('get')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('delete')

class UserViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the users in the system.

    ###create_user: __/create_user/__ ###

    Allows an is_staff user to push new users into the system.

    The system attempts to match the string entry of address_country and address_state against the full name and abbreviations and replaces it with the corresponding foreign key.


    """
    queryset = User.objects.all()
    serializer_class = UserNotMeSerializer
    # permission_classes = (IsAuthenticated,)
    #TODO: add method permissions
    permission_classes = (IsAuthenticated, IsMeOrAdmin)
    filter_backends = (SearchFilter,)
    search_fields = ('first_name', 'last_name', 'town_of_residence__name',)

    @list_route(methods=['get', 'put'])
    def current_user(self, request, *args, **kwargs):
        self.serializer_class = UserSerializer
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=request.user.pk)

        log_action(request, user)

        if request.method == 'PUT':
            data = request.data
            data['id'] = user.id
            serializer = UserUpdateSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                user = serializer.update(user, serializer.validated_data)

        if request.GET.get('full', None):
            serializer = UserFullSerializer(user, context={'request': request})
        else:
            serializer = UserSerializer(user, context={'request': request})

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        # user who is uploading is user they are editing.
        if request.user.id == UUID(kwargs.get('pk')) or request.user.is_superuser or request.user.is_staff:
            self.serializer_class = UserSerializer

            instance = self.get_object()

            if 'nationality' in request.data:
                try:
                    nationality = Nationality.objects.get(name=request.data['nationality'])
                    instance.nationality_id = nationality.id
                except ObjectDoesNotExist:
                    nationality = Nationality.objects.create(name=request.data['nationality'],
                                                             created_by=request.user,
                                                             modified_by=request.user)
                    instance.nationality_id = nationality.id

            if 'place_of_birth' in request.data:
                try:
                    place_of_birth = Town.objects.get(name=request.data['place_of_birth'])
                    instance.place_of_birth_id = place_of_birth.id
                except ObjectDoesNotExist:
                    place_of_birth = Town.objects.create(name=request.data['place_of_birth'],
                                                         created_by=request.user,
                                                         modified_by=request.user)
                    instance.place_of_birth_id = place_of_birth.id

            if 'town_of_residence' in request.data:
                try:
                    town_of_residence = Town.objects.get(name=request.data['town_of_residence'])
                    instance.town_of_residence_id = town_of_residence.id
                except ObjectDoesNotExist:
                    town_of_residence = Town.objects.create(name=request.data['town_of_residence'],
                                                            created_by=request.user,
                                                            modified_by=request.user)
                    instance.town_of_residence_id = town_of_residence.id

            if 'profile_image_base64' in request.data:

                if len(request.data['profile_image_base64']) > 0:
                    profile_image_data = binascii.a2b_base64(request.data['profile_image_base64'].replace('data:image/jpeg;base64,', ''))
                    temp_file = NamedTemporaryFile(delete=False)
                    temp_file.close()
                    f = open(temp_file.name, mode='wb')
                    f.write(profile_image_data)
                    f.close()
                    f = open(temp_file.name, mode='rb')

                    instance.profile_image = UploadedFile(file=f,
                                                         name='%s.jpg' % request.data['id'],
                                                         content_type='image/jpeg',
                                                         size=len(profile_image_data))

            if 'bio' in request.data:
                instance.bio_html = markdown.markdown(request.data['bio'])

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if 'profile_image_base64' in request.data:
                if len(request.data['profile_image_base64']) > 0:
                    f.close()
                    temp_file.close()
                    os.remove(temp_file.name)

            return Response(serializer.data)

        raise PermissionDenied()

    # @detail_route(methods=['get'])
    # def reset_password(self, request, *args, **kwargs):
    #
    #     queryset = User.objects.all()
    #     user = get_object_or_404(queryset, pk=request.user.pk)
    #     log_action(request, user)
    #     if request.GET.get('full', None):
    #         serializer = UserFullSerializer(user, context={'request': request})
    #     else:
    #         serializer = UserSerializer(user, context={'request': request})
    #
    #     return Response(serializer.data)
    # @list_route(methods=['post', 'put'])
    # def sign_nda(self, request, *args, **kwargs):
    #     signed_nda_ip = request.META.get('REMOTE_ADDR', None)
    #     signed_nda_user_agent = request.META.get('HTTP_USER_AGENT', None)
    #     signed_nda = request.data.get('signed_nda', None)
    #     signed_nda_text = request.data.get('signed_nda_text', '')
    # 
    #     print(request.data)
    # 
    # 
    # 
    #     response = {
    #         "detail": "There was a problem signing the nda."
    #     }
    # 
    #     if request.user and signed_nda:
    #         request.user.signed_nda = signed_nda
    #         request.user.signed_nda_ip = signed_nda_ip
    #         request.user.signed_nda_datetime = timezone.now()
    #         request.user.signed_nda_user_agent = signed_nda_user_agent
    #         request.user.signed_nda_text = signed_nda_text
    #         request.user.save()
    #         response['detail'] = "Thanks for signing our NDA. Enjoy the Future Leaders Programme!"
    # 
    #     else:
    #         response['detail'] = 'You are not currently logged in.'
    #         raise PermissionDenied(response['detail'])
    # 
    #     return Response(response)

    # @list_route(methods=['post', 'put'])
    # def flp_apply(self, request, *args, **kwargs):
    #     first_name = request.data.get('first_name')
    #     last_name = request.data.get('last_name')
    #     email = request.data.get('email')
    #     phone_number = request.data.get('phone_number')
    #     enroll_message = request.data.get('enroll_message')
    # 
    #     # print(request.data)
    # 
    #     response = {
    #         "detail": "There was a problem applying.",
    #     }
    # 
    #     if request.user:
    #         request.user.first_name = first_name
    #         request.user.last_name = last_name
    #         request.user.email = email
    #         request.user.phone_number = phone_number
    #         request.user.enroll_message = enroll_message
    #         request.user.flp_applied = True
    #         request.user.save()
    #         response['detail'] = "Thanks for applying to be a Future Leader. Spots are limited.  Someone will get back to you shortly."
    # 
    #     else:
    #         response['detail'] = 'You are not currently logged in.'
    #         raise PermissionDenied(response['detail'])
    # 
    #     return Response(response)

    def update(self, request, *args, **kwargs):
        if request.user.id == UUID(kwargs.get('pk')) or request.user.is_superuser or request.user.is_staff:
            self.serializer_class = UserSerializer
            return super(UserViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            self.serializer_class = UserSerializer
            return super(UserViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            self.serializer_class = UserSerializer
            return super(UserViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')

    @detail_route(methods=['put'])
    def initial_setup(self, request, *args, **kwargs):
        self.serializer_class = UserSerializer
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        is_initial_setup = request.GET.get('is_initial_setup', False)

        data = request.data
        try:
            nationality = Nationality.objects.get(name=data['nationality'])
        except ObjectDoesNotExist:
            nationality = Nationality.objects.create(name=data['nationality'],
                                                     created_by=request.user,
                                                     modified_by=request.user)

        try:
            place_of_birth = Town.objects.get(name=data['place_of_birth'])
        except ObjectDoesNotExist:
            place_of_birth = Town.objects.create(name=data['place_of_birth'],
                                                 created_by=request.user,
                                                 modified_by=request.user)

        try:
            town_of_residence = Town.objects.get(name=data['town_of_residence'])
        except ObjectDoesNotExist:
            town_of_residence = Town.objects.create(name=data['town_of_residence'],
                                                    created_by=request.user,
                                                    modified_by=request.user)

        data['place_of_birth_id'] = place_of_birth.id
        data['nationality_id'] = nationality.id
        data['town_of_residence_id'] = town_of_residence.id
        data['completed_initial_setup'] = True

        if 'profile_image_base64' in data:
            if len(data['profile_image_base64']) > 0:
                print(data['profile_image_base64'][:100])
                profile_image_data = binascii.a2b_base64(data['profile_image_base64'].replace('data:image/jpeg;base64,', ''))
                temp_file = NamedTemporaryFile(delete=False)
                temp_file.close()
                f = open(temp_file.name, mode='wb')
                f.write(profile_image_data)
                f.close()
                f = open(temp_file.name, mode='rb')

                instance.profile_image = UploadedFile(file=f,
                                                     name='%s.jpg' % data['id'],
                                                     content_type='image/jpeg',
                                                     size=len(profile_image_data))

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if 'profile_image_base64' in data:
            if len(data['profile_image_base64']) > 0:
                f.close()
                temp_file.close()
                os.remove(temp_file.name)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @list_route(methods=['post', 'put'])
    def change_password(self, request, *args, **kwargs):
        self.serializer_class = UserSerializer
        current_password = request.data.get('current_password', None)
        new_password = request.data.get('new_password', None)

        response = {
            "detail": "There was a problem changing your password."
        }

        if current_password is None:
            response['detail'] = 'Current password was not supplied.'
            raise PermissionDenied(response['detail'])

        if new_password is None:
            response['detail'] = 'A new password was not supplied.'
            raise PermissionDenied(response['detail'])

        if request.user.username:
            instance = authenticate(username=request.user.username, password=current_password)

            if instance:
                instance.set_password(new_password)
                instance.save()
                response['detail'] = 'Your password was changed.'
            else:
                response['detail'] = 'The current password you provided is incorrect.'
                raise PermissionDenied(response['detail'])
        else:
            response['detail'] = 'You are not currently logged in.'
            raise PermissionDenied(response['detail'])

        return Response(response)


    @detail_route(methods=['get'])
    def profile(self, request, *args, **kwargs):
        lookup = {}
        try:
            UUID(kwargs['pk'], version=4)
            lookup['pk'] = kwargs['pk']
        except ValueError:
            if kwargs['pk'] == 'me':
                lookup['pk'] = request.user.pk
            else:
                lookup['username'] = kwargs['pk']

        user = User.objects.get(**lookup)

        log_action(request, user)
        if request.GET.get('full', None):
            self.serializer = UserFullSerializer(user, context={'request': request})
        else:
            self.serializer = UserSerializer(user, context={'request': request})


        return Response(self.serializer.data)

    @list_route(methods=['post'])
    def create_user(self, request, *args, **kwargs):
        self.serializer_class = UserSerializer

        if request.user.is_staff:
            request.data['user']['groups'] = dict()
            address_country = request.data['userprofile']['address_country']
            if address_country == '':
                address_country = 'US'

            if address_country != '':
                if address_country == 'USA':
                    address_country = 'US'

                if address_country == 'UK':
                    address_country = 'GB'

                address_country = Country.objects.filter(
                    Q(abbreviation__iexact=address_country)
                    | Q(name__iexact=address_country)
                ).distinct()

                if len(address_country) > 0:
                    address_country = address_country[0].pk

                request.data['userprofile']['address_country'] = address_country

            address_state = request.data['userprofile']['address_state']
            if address_state != '':
                address_state = State.objects.filter(
                    Q(abbreviation__iexact=address_state)
                    | Q(name__iexact=address_state)
                ).distinct()

                if len(address_state) > 0:
                    address_state = address_state[0].pk

                request.data['userprofile']['address_state'] = address_state

            # request.data['userprofile']['is_approver'] = False

            user_serializer = UserSerializer(data=request.data['user'])
            user_serializer.is_valid(raise_exception=True)

            user_obj = user_serializer.save()

            user_obj.set_password(codegenerator())
            user_obj.save()

            if user_obj:
                request.data['userprofile']['user'] = user_obj
                request.data['userprofile']['user_id'] = user_obj.pk
                user_profile_serializer = UserProfileCreateSerializer(data=request.data['userprofile'])
                user_profile_serializer.is_valid(raise_exception=True)

                if user_profile_serializer.save():
                    log_action(request, user_obj)
                    return Response({"details":"created","object_id":user_obj.pk}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"details":"not created"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({"details":"not created"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        else:
            raise PermissionDenied('You do not have permission to perform this action.')

    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = (IsAuthenticated,)
        if request.user.id == UUID(kwargs.get('pk')) or request.user.is_superuser or request.user.is_staff:
            self.serializer_class = UserSerializer

        self.queryset = self.queryset.extra(
            select={
                'connected': "SELECT COUNT(id) FROM connections_connection WHERE connections_connection.state = 'A' AND connections_connection.to_user_id = drf_users_user.id AND connections_connection.from_user_id = '" + str(request.user.id) + "'",
                'pending_request':
                    "select id from connections_connectionrequest " +
                    "WHERE "+
                    "(" +
                        "(" +
                            "connections_connectionrequest.to_user_id = drf_users_user.id " +
                            "AND " +
                            "connections_connectionrequest.from_user_id = '" + str(request.user.id) + "'" +
                        ")" +
                        " OR " +
                        "(" +
                            "connections_connectionrequest.to_user_id = '" + str(request.user.id) + "'" +
                            " AND " +
                            "connections_connectionrequest.from_user_id = drf_users_user.id" +
                        ")" +
                    ")" +
                    " AND connections_connectionrequest.state = 'P'" +
                    " ORDER BY created_on DESC LIMIT 1"
            }
        )
        return super(UserViewSet, self).retrieve(request, *args, **kwargs)

    @list_route(methods=['POST'])
    def verifyphone(self, request, *args, **kwargs):
        user = request.user
        if user.phone_country_dial_code and user.phone_number:
            phone_number = "%s%s" % (user.phone_country_dial_code, user.phone_number)
            code = generateVerificationCode()
            old_codes = PhoneVerificationCode.objects.filter(user=request.user, is_active=True)
            for old_code in old_codes:
                old_code.is_active = False
                old_code.save()

            verification_code = PhoneVerificationCode(code=code,
                                                      created_by=user,
                                                      modified_by=user,
                                                      user=user,
                                                      is_used=False,
                                                      is_active=True)
            verification_code.save()
            message = "Here is your verification code from Tunaweza: %s." % code
            sendSMS(phone_number=phone_number, message=message)
            response = Response({'detail': 'Message sent'})
        else:
            response = Response({'detail': 'No phone number is on the account.'}, status=422)
        return response

    @list_route(methods=['POST'])
    def verifyphonecode(self, request, *args, **kwargs):
        user = request.user
        if 'code' in request.data:
            code = request.data['code']
            try:
                verification_code = PhoneVerificationCode.objects.get(user=user, code=code, is_active=True, is_used=False)
                verification_code.is_active = False
                verification_code.is_used = True
                request.user.verified_phone = True
                request.user.save()
                verification_code.save()
                response = Response({'detail': 'Phone number now verified.'})

                # send push notif to mark that numbers were verified
                try:
                    tokens = PushToken.objects.filter(user=User.objects.get(email='mhatchell@mac.com'), push_group=IONIC_PUSH_GROUP, is_active=True)\
                        .values_list('token')
                    tokens_list = list()
                    for token in tokens:
                        tokens_list.append(token[0])

                    payload = {
                        "image": verification_code.user.get_profile_image_cache_url(),
                        "created_by_id": str(verification_code.user.id),
                        "type": NOTIFICATION_TYPES.PHONE_VERIFIED
                    }
                    title = "%s verified" % verification_code.user
                    message = "%s verified their phone number" % verification_code.user

                    if len(tokens_list) > 0:
                        r = PushNotificationRequest()
                        r.create({
                            "tokens": tokens_list,
                            "notification": {
                                "message": message,
                                "title": title,
                                "payload": payload,
                                "ios": {
                                    "badge": "1",
                                    "sound": "",
                                    "priority": 10
                                },
                                "android": {
                                    "sound": "",
                                    "priority": "high"
                                }
                            },
                            "profile": IONIC_PUSH_GROUP
                        })
                except ObjectDoesNotExist:
                    pass

            except ObjectDoesNotExist:
                response = Response({'detail': 'Could not verify your phone number, please try again.'}, status=404)
        else:
            raise ParseError({'detail': 'A code was not supplied.'})
        return response


class UserRegisterViewSet(viewsets.GenericViewSet):
    """
    This endpoint allows users to register.

    __list() doesnt do anything unless a ?vc param is supplied, then it will try to activate the user account associated with it.__


    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny, )
    authentication_classes = (TokenAuthentication,)

    def list(self, request, *args, **kwargs):
        verification_code = request.GET.get('vc', None)
        redirect_after_verification = (request.GET.get('r', False) == 'True')
        resend_verification = (request.GET.get('resend', False) == 'True')
        user_email = request.GET.get('email', None)


        if verification_code is not None:
            try:
                user = User.objects.get(verification_code=verification_code)
                user.verify_user()
                if redirect_after_verification:
                    return HttpResponseRedirect(APP_USER_VERIFIED_PATH)
                else:
                    response = {"detail": "User account verified."}
                    return Response(response)
            except (ObjectDoesNotExist):
                if redirect_after_verification:
                    return HttpResponseRedirect(APP_USER_VERIFICATION_FAILED)
                else:
                    raise NotFound('Verification code not valid.')

        if user_email is not None:
            if resend_verification:
                try:
                    user = User.objects.get(email=user_email)
                    user.send_verification_email()
                    print('sent email for %s' % user)
                except (ObjectDoesNotExist):
                    response = {"detail": "If an account that matches the email provided exists you will receive and email with a verification link."}
                    return Response(response)

        raise MethodNotAllowed('GET')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        to_return = ''
        will_account_be_activated = False

        if not serializer.is_valid():
            return Response(serializer.errors, status=406)

        else:
            if User.objects.filter(username=serializer.data.get('email')):
                return Response({"username": "Username already exists."}, status=406)

            if User.objects.filter(email=serializer.data.get('email')):
                return Response({"email": "Email already used to create an account."}, status=406)

            invitation_code = serializer.data.get('invitation_code', None)

            invitation_code_object = InvitationCode.objects.checkCode(invitation_code)
            if invitation_code_object:
                invitation_code_object.incrementUsed()
                will_account_be_activated = True
            else:
                will_account_be_activated = False

            will_account_be_activated = True

            if 'profile_image_base64' in request.data:
                if len(request.data['profile_image_base64']) > 0:
                    profile_image_data = request.data['profile_image_base64']
                    missing_padding = len(profile_image_data) % 4
                    if missing_padding != 0:
                        ii = 0
                        while ii < 4 - missing_padding:
                            ii += 1
                            profile_image_data += '='

                        profile_image_data =  binascii.a2b_base64(profile_image_data)

                    temp_file = NamedTemporaryFile(delete=False)
                    temp_file.close()
                    f = open(temp_file.name, mode='wb')
                    f.write(profile_image_data)
                    f.close()
                    f = open(temp_file.name, mode='rb')

                    profile_image = UploadedFile(file=f,
                                                 name='%s.jpg' % request.data['id'],
                                                 content_type='image/jpeg',
                                                 size=len(profile_image_data))

                    f.close()
                    temp_file.close()
                    os.remove(temp_file.name)


            new_user = User.objects.create(
                username=serializer.data.get('email'),
                password=make_password(serializer.data.get('password')),
                first_name=serializer.data.get('first_name'),
                last_name=serializer.data.get('last_name'),
                email=serializer.data.get('email'),
                is_active=will_account_be_activated,
                verification_code=User.make_verification_code(
                    serializer.data.get('email'),
                    serializer.data.get('email')
                )
            )
            new_user.set_password(serializer.data.get('password'))
            new_user.save()
            # new_user_profile = User.objects.create(created_by=new_user,
            #                                               modified_by=new_user,
            #                                               user=new_user
            #                                               )

            if new_user:
                group = Group.objects.get(name='Users')
                new_user.groups.add(group)
                new_user.send_verification_email()

            return Response({"will_account_be_activated": will_account_be_activated}, status=201)


class UsernameTestViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):

        queryset = User.objects.all()
        log_action(request)
        username = request.GET.get('username', None)
        email = request.GET.get('email', None)

        if username:
            queryset = queryset.filter(username=username)
            if len(queryset) > 0:
                return Response(True)
            else:
                return Response(False)
        if email:
            queryset = queryset.filter(email=email)
            if len(queryset) > 0:
                return Response(True)
            else:
                return Response(False)


        return Response(True)

    def retrieve(self, request, *args, **kwargs):
        return Response({})


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint presents the groups in the system.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticated,)

class UserProfilesViewSet(CreatedModifiedByModelViewSetMixin):
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


class UserProfileViewSet(CreatedModifiedByModelViewSetMixin):
    """
    This endpoint presents the user profiles in the system.
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,IsAllowedOrSuperuser)

    def list(self, request):
        queryset = self.queryset.filter()

        if request.user.pk != None:
            try:
                request.user.userprofile
                queryset = queryset.filter(pk=request.user.userprofile.pk)[0]
            except User.DoesNotExist:
                raise NotAcceptable('No user profile for the current user exists.')
        else:
            raise NotAcceptable('No user profile for the current user exists.')

        log_action(request, queryset)

        serializer = self.serializer_class(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['post'], permission_classes=[IsAllowedOrSuperuser])
    def upload_user_image(self, request, pk=None):
        self.parser_classes = (FileUploadParser,)
        response = '{"details":"Accepted"}'

        image = request.FILES.get('user_image', None)

        if image != None:
            obj = User.objects.get(pk=pk)
            obj.profile_image = image
            obj.save()

        log_action(request, obj)

        return Response(response)

    def create(self, request, *args, **kwargs):
        self.serializer_class = UserProfileCreateSerializer

        request.data['user_id'] = request.user.id
        return super(UserProfileViewSet, self).create(request, *args, **kwargs)

class UserProfileImageViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the user profiles in the system.
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,IsAllowedOrSuperuser)
    parser_classes = (FileUploadParser,)

    def list(self, request):
        raise NotAcceptable('No user profile for the current user exists.')
        return Response('')

    def retrieve(self, request, *args, **kwargs):
        raise NotAcceptable('No user profile for the current user exists.')
        return Response('')


    @detail_route(methods=['post'], permission_classes=[IsAllowedOrSuperuser])
    def upload_user_image(self, request, pk=None):
        image = request.FILES.get('file', None)
        if image != None:
            obj = User.objects.get(pk=pk)
            filename, file_extension = os.path.splitext(image.name)
            image.name = "%s-%s%s" % (obj.id, str(time.time()).replace('.', '-'), file_extension)
            obj.profile_image = image
            obj.save()

            # temp_thumbnail_file = NamedTemporaryFile()
            # size = 128, 128
            # try:
            #     im = Image.open(image)
            #     im.thumbnail(size)
            #     im.save(temp_thumbnail_file, "JPEG")
            # except IOError:
            #     print "cannot create thumbnail for"

            log_action(request, obj)
            response = '{"detail":"Accepted"}'
            return Response(response, status=201)

        else:
            response = '{"detail":"No Image"}'
            log_action(request)
            return Response(response, status=406)


class PeopleViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserMinimalWithFriendshipSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (SearchFilter,)
    search_fields = ('first_name', 'last_name', 'town_of_residence__name',)

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('post')

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('put')

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('get')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('delete')

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.extra(
            select={
                'connected': "SELECT COUNT(id) FROM connections_connection WHERE connections_connection.state = 'A' AND connections_connection.to_user_id = drf_users_user.id AND connections_connection.from_user_id = '" + str(request.user.id) + "'",
                'pending_request': "SELECT id FROM connections_connectionrequest " +
                                   "WHERE "+
                                   "(" +
                                       "(" +
                                           "connections_connectionrequest.to_user_id = drf_users_user.id " +
                                           "AND " +
                                           "connections_connectionrequest.from_user_id = '" + str(request.user.id) + "'" +
                                       ")" +
                                       " OR " +
                                       "(" +
                                           "connections_connectionrequest.to_user_id = '" + str(request.user.id) + "'" +
                                           " AND " +
                                           "connections_connectionrequest.from_user_id = drf_users_user.id" +
                                       ")" +
                                   ")" +
                                   " AND connections_connectionrequest.state = 'P'" +
                                   " ORDER BY created_on DESC LIMIT 1"
            }
        ).exclude(id=request.user.id)
        search = request.GET.get('search', None)
        if search is None or len(search) < 0:
            raise NotAcceptable('you must search for something')
        else:
            return super(PeopleViewSet, self).list(request, *args, **kwargs)


class PushTokenViewSet(viewsets.ModelViewSet):

    queryset = PushToken.objects.all()
    serializer_class = PushTokenSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            device_id = ''
            if 'device_id' in serializer.data:
                device_id = serializer.data['device_id']

            device_manufacturer = ''
            if 'device_manufacturer' in serializer.data:
                device_manufacturer = serializer.data['device_manufacturer']

            device_model = ''
            if 'device_model' in serializer.data:
                device_model = serializer.data['device_model']

            device_version = ''
            if 'device_version' in serializer.data:
                device_version = serializer.data['device_version']

            push_group = ''
            if 'push_group' in serializer.data:
                push_group = serializer.data['push_group']

            device_platform = ''
            if 'device_platform' in serializer.data:
                device_platform = serializer.data['device_platform']

            app_version = ''
            if 'app_version' in serializer.data:
                app_version = serializer.data['app_version']
            try:
                token = PushToken.objects.get(token=serializer.data['token'], user=request.user)
                if token.is_active is False:
                    token.make_valid()

                token.device_id = device_id
                token.device_manufacturer = device_manufacturer
                token.device_model = device_model
                token.device_version = device_version
                token.is_active = True
                token.push_group = push_group
                token.device_platform = device_platform
                token.app_version = app_version
            except ObjectDoesNotExist:
                token = PushToken(
                    token=serializer.data['token'],
                    created_on=timezone.datetime.now(),
                    user=request.user,
                    is_active=True,
                    device_id=device_id,
                    device_manufacturer=device_manufacturer,
                    device_model=device_model,
                    push_group=push_group,
                    device_version=device_version,
                    app_version=app_version,
                    device_platform=device_platform
                )
            token.modified_on = timezone.datetime.now()
            token.save()
            return Response({'detail': 'Registered a new push token.'})
        else:
            raise MethodNotAllowed('post')

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('put')

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('get')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('delete')

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed('get')
