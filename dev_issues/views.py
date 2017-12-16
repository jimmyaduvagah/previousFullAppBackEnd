# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.serializers import json
from django.http import HttpResponse
# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import json
import gitlab
from django.conf import settings
from drf_users.permissions import IsAllowedOrSuperuser


class DevIssuesViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,IsAllowedOrSuperuser)

    def list(self, request, *args, **kwargs):
        gl = gitlab.Gitlab('https://gitlab.tunaweza.com/', settings.GITLAB_API_TOKEN)
        data = gl.getprojectissues(project_id=24, state='opened', per_page=100)
        return Response(data)

    @list_route()
    def closed(self, request, *args, **kwargs):
        gl = gitlab.Gitlab('https://gitlab.tunaweza.com/', settings.GITLAB_API_TOKEN)
        data = gl.getprojectissues(project_id=24, state='closed', per_page=100)
        return Response(data)

    @list_route()
    def all(self, request, *args, **kwargs):
        gl = gitlab.Gitlab('https://gitlab.tunaweza.com/', settings.GITLAB_API_TOKEN)
        data = gl.getprojectissues(project_id=24, per_page=100)
        return Response(data)

    def create(self, request, *args, **kwargs):
        gl = gitlab.Gitlab('https://gitlab.tunaweza.com/', settings.GITLAB_API_TOKEN)
        issue_data = json.loads(request.body.decode("utf-8"))
        f_issue = gl.createissue(project_id=24,title=issue_data['title'],description = issue_data['description'],labels = issue_data['category'])
        return Response(f_issue)