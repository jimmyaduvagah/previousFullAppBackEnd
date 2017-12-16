import time
import os
import base64
from django.core.files import File
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.views.generic import TemplateView
from rest_framework.exceptions import PermissionDenied, NotAcceptable
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from cms_locations.models import Country, State
from twz_server_django.utils import log_action
from twz_server_django.settings import MEDIA_ROOT
from twz_server_django.rest_extensions import LimitOffsetPagination
import vimeo
from twz_server_django.settings_private import VIMEO_ACCESS_TOKEN, VIMEO_CLIENT_KEY, VIMEO_CLIENT_SECRET
import requests
import json

class VimeoViewSet(viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):
        endpoint = kwargs.get('endpoint', None)
        if endpoint == '' or endpoint == None:
            return Response(False)

        v = vimeo.VimeoClient(
            token=VIMEO_ACCESS_TOKEN,
            key=VIMEO_CLIENT_KEY,
            secret=VIMEO_CLIENT_SECRET)

        response = v.get("/%s" % (endpoint,), params=dict(request.GET))
        data = response.json()

        return Response(data, status=response.status_code)


class VimeoVideoView(TemplateView):
    url = ''
    template_name = 'vimeo-video.html'
    current_domain = 'www.localhost.com'

    def make_url(self, video_id=None):
        if not video_id:
            raise Exception('no video id was provided')

        url = "https://player.vimeo.com/video/%s?title=0&byline=0&portrait=0" % (video_id,)

        return url

    def dispatch(self, request, *args, **kwargs):
        host = request.META.get('HTTP_HOST', None)
        if host:
            host = host\
                .replace('https://','')\
                .replace('http://','')\
                .replace(':8000','')
            self.current_domain = host

        video_id = kwargs.get('vimeo_id', None)
        self.url = self.make_url(video_id)
        return super(VimeoVideoView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(VimeoVideoView, self).get_context_data(**kwargs)
        request_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/6.2.8 Safari/537.85.17'
        }
        source_page = requests.get(self.url, headers=request_headers)
        context['source'] = source_page.content.decode()
        context['source'].replace('src="/', 'src="https://player.vimeo.com/')
        context['source'].replace('"cookie_domain": ".vimeo.com"', '"cookie_domain": "%s"' % self.current_domain)

        return context

    def get(self, request, *args, **kwargs):
        response = super(VimeoVideoView, self).get(request, *args, **kwargs)
        response['X-Frame-Options'] = 'ALLOWALL'

        return response
