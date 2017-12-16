from django.utils import timezone
from django.core.urlresolvers import resolve
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser
from action_log.models import Action
import boto3
from twz_server_django.settings_private import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID
from random import randint


def generateVerificationCode():
    i = 0
    code = ''
    while i < 6:
        code = "%s%s" % (code, randint(0, 9))
        i += 1
    return code

def sendSMS(phone_number=None, message=None):
    if phone_number is None:
        raise Exception('phone_number can not be None')

    if message is None:
        raise Exception('message can not be None')

    client = boto3.client('sns', region_name='us-east-1', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    client.publish(
        PhoneNumber=phone_number,
        Message=message
    )

def pathToPk(url):
    pk = None
    resolved_path = None

    if type(url) == int:
        pk = url
    else:
        if 'http://' in url or 'https://' in url:
            url = url.replace('https://','')
            url = url.replace('http://','')

            path_array = url.split('/')
            i = 0
            path = ''
            for part in path_array:
                if i > 0:
                    path = path + "/" + part
                i = i + 1
            try:
                resolved_path = resolve(path)
            except:
                return ''
            if resolved_path != None:
                pk = resolved_path.kwargs['pk']
        else:
            pk = url


    return pk

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_request_headers(request):
    headers = {}
    for field in request.META:
        if field == 'HTTP_USER_AGENT' or field == 'HTTP_REFERER' or field == 'REQUEST_METHOD' or field == 'HTTP_AUTHORIZATION' or field == 'QUERY_STRING' or field == 'CONTENT_LENGTH' or field == 'CONTENT_TYPE' or field == 'REMOTE_ADDR' or field == 'HTTP_HOST' or field == 'HTTP_ACCEPT' or field == 'SERVER_NAME' or field == 'HTTP_ACCEPT_LANGUAGE' or field == 'HTTP_ORIGIN' or field == 'HTTP_ACCEPT_ENCODING':
            headers[field] = request.META[field]

    return headers

def log_action(request, obj=None):
    data = {
        'POST': request.POST,
        'GET': request.GET,
        'data': request.data
    }
    if type(request.user) == AnonymousUser:
        user = None
    else:
        user = request.user

    if obj == None:
        Action.objects.create(
            ip=get_client_ip(request),
            method=request.META.get('REQUEST_METHOD',''),
            endpoint=request.get_full_path(),
            user=user,
            headers=get_request_headers(request),
            data=data
        )
    else:
        Action.objects.create(
            ip=get_client_ip(request),
            method=request.META.get('REQUEST_METHOD',''),
            endpoint=request.get_full_path(),
            object_id=obj.pk,
            user=user,
            content_type=ContentType.objects.get_for_model(obj),
            headers=get_request_headers(request),
            data=data
        )

