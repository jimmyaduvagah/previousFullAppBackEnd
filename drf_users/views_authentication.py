import json
from uuid import UUID

import re
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework import parsers
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.views.generic import View
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from drf_users.models import User
from drf_users.serializers import UserSerializer
from twz_server_django import settings
from django.utils import timezone
import datetime


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ObtainAuthToken, self).dispatch(*args, **kwargs)

    def post(self, request):
        user_form_data = request.data
        if 'username' not in user_form_data:
            raise NotAcceptable('username is required')
        
        if 'password' not in user_form_data:
            raise NotAcceptable('password is required')

        if user_form_data['username'] is not None:
            EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
            if EMAIL_REGEX.match(user_form_data['username']):
                user_obj = User.objects.filter(email__iexact=user_form_data['username']).values('username', 'verified_email')
                if len(user_obj) > 0:
                    user_form_data['username'] = user_obj[0]['username']
            else:
                user_obj = User.objects.filter(username__iexact=user_form_data['username']).values('username', 'verified_email')
                if len(user_obj) > 0:
                    user_form_data['username'] = user_obj[0]['username']

        if len(user_obj) > 0:
            if user_obj[0]['verified_email'] is False:
                raise PermissionDenied({'detail': 'You need to verify your email before you can login.'})

        serializer = self.serializer_class(data=user_form_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.last_login = timezone.now()
        user.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


obtain_auth_token = ObtainAuthToken.as_view()


@csrf_exempt
def login_view(request):
    user = {}
    user['username'] = request.POST.get('username', None)
    user['password'] = request.POST.get('password', None)

    if user['username'] is not None:
        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if EMAIL_REGEX.match(user['username']):
            email = user['username']
            user_obj = User.objects.filter(email=email).values('username')
            if len(user_obj) > 0:
                user['username'] = user_obj[0]['username']

    serializer = AuthTokenSerializer(data=user)
    if serializer.is_valid(raise_exception=False):
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        if user.is_superuser:
            if settings.DEBUG:
                response = HttpResponseRedirect('%s%s:%s%s' % (settings.SERVER_PROTOCOL, settings.APP_SERVER_NAME, settings.APP_SERVER_PORT, settings.APP_ADMIN_LOGGED_IN_PATH))
            else:
                response = HttpResponseRedirect('%s%s%s' % (settings.SERVER_PROTOCOL, settings.APP_SERVER_NAME, settings.APP_ADMIN_LOGGED_IN_PATH))
        else:
            if settings.DEBUG:
                response = HttpResponseRedirect('%s%s:%s%s' % (settings.SERVER_PROTOCOL, settings.APP_SERVER_NAME, settings.APP_SERVER_PORT, settings.APP_USER_LOGGED_IN_PATH))
            else:
                response = HttpResponseRedirect('%s%s%s' % (settings.SERVER_PROTOCOL, settings.APP_SERVER_NAME, settings.APP_USER_LOGGED_IN_PATH))
        max_age = 7 * 24 * 60 * 60
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie('auth_token', token.key, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)
        user.last_login = timezone.now()
        user.save()
    else:
        if settings.DEBUG:
            response = HttpResponseRedirect('%s%s:%s%s' % (settings.SERVER_PROTOCOL, settings.APP_SERVER_NAME, settings.APP_SERVER_PORT, settings.APP_USER_LOG_IN_FAILED_PATH))
        else:
            response = HttpResponseRedirect('%s%s%s' % (settings.SERVER_PROTOCOL, settings.APP_SERVER_NAME, settings.APP_USER_LOG_IN_FAILED_PATH))

    return response


@csrf_exempt
def token_test(request):
    token = ''
    request_data = json.loads(request.body.decode('utf-8'))
    token = request_data.get('token', None)
    user_id = request_data.get('user_id', None)

    try:
        token_obj = Token.objects.get(key=token)
        user = token_obj.user
        if user.id == UUID(user_id):
            response = HttpResponse(json.dumps({
                "status": "good token",
                "user": UserSerializer(user).data
            }))
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        response = HttpResponse(json.dumps({
            "status": "bad token"
        }), status=401)

    return response

