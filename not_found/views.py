import time
import os
import base64
from django.core.files import File
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied, NotAcceptable, NotFound
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework import status
from rest_framework import renderers
from rest_framework import viewsets
from twz_server_django.utils import get_client_ip, get_request_headers
from cms_locations.models import Country, State
from twz_server_django.utils import log_action
from twz_server_django.settings import MEDIA_ROOT
import random


class NotFoundViewSet(viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):
        raise NotFound()