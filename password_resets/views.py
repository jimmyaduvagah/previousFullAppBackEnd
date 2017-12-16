import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from rest_framework.exceptions import MethodNotAllowed, NotAcceptable, NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_users.models import User
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin, CsrfExemptSessionAuthentication
from twz_server_django.settings import SERVER_PROTOCOL, APP_SERVER_NAME, APP_SERVER_PORT, APP_RESET_PASSWORD_URL
from password_resets.models import PasswordResetToken
from password_resets.serializers import PasswordResetTokenSerializer


class PasswordResetTokenViewSet(CreatedModifiedByModelViewSetMixin):
    """
    This endpoint presents the user profiles in the system.
    """
    queryset = PasswordResetToken.objects.all()
    serializer_class = PasswordResetTokenSerializer
    permission_classes = (AllowAny,)
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def create(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        found = False
        if email:
            try:
                user = User.objects.get(email=email)
                if user:
                    found = True
            except ObjectDoesNotExist as e:
                found = False

            if found:
                token = create_password_reset_token_for_user(user)
                send_email_with_password_reset_link_to(token=token, user=user)
                return Response({"detail":"Password reset email has been sent."})
            else:
                raise NotFound("No matching account was found.")

        else:
            raise NotFound("No email was provided.")

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')

    def update(self, request, *args, **kwargs):
        token_id = kwargs['pk']
        password = request.data.get('password', None)
        token = None
        found = False
        try:
            token = PasswordResetToken.objects.get(pk=token_id)
            if token.is_valid():
                found = True
        except (ObjectDoesNotExist, ValueError) as e:
            found = False


        if found and token:
            if password:
                token.user.set_password(password)
                token.user.save()
                token.valid = False
                token.used = True
                token.used_on = timezone.now()
                token.save()

            else:
                return Response({"detail": "No password was supplied"})

            return Response({"detail": "Your password was reset."})
        else:
            raise NotFound('No valid matching token was found.')



def create_password_reset_token_for_user(user):
    PasswordResetToken.objects.invalidate_tokens_for_user(user)
    token_obj = PasswordResetToken.objects.create(user=user, requested_on=timezone.now(), used=False)
    return token_obj

def send_email_with_password_reset_link_to(user, token):
    url = make_reset_password_link(token)
    html_message = """
<p>Hello %s,</p>

<p>As a reminder, your username is: %s</p>

<p>Please follow the link below to reset your password.</p>

<p><a href="%s">%s</a></p>

<p>This link will expire in 2 hours.</p>
    """ % (user.get_full_name(), user.username, url, url)

    message = """
Hello %s,

As a reminder, your username is: %s

Please follow the link below to reset your password.

%s

This link will expire in 2 hours.
    """ % (user.get_full_name(), user.username, url)

    user.email_user("Password reset request for Future Leaders Training", message, html_message=html_message)
    return True

def make_reset_password_link(token):
    if APP_SERVER_PORT != '80':
        port = ':%s' % APP_SERVER_PORT
    else:
        port = ''

    url = '%s%s%s%s/%s' % (SERVER_PROTOCOL, APP_SERVER_NAME, port, APP_RESET_PASSWORD_URL, token.id)
    return url

