import re

import boto3
import requests
import binascii
import os
import re
from tempfile import NamedTemporaryFile
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from PIL import Image as PilImage
from django.core.files.uploadedfile import UploadedFile
from rest_framework import viewsets
from rest_framework.parsers import FileUploadParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from six import BytesIO
from django.http import HttpResponse
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import NotFound, MethodNotAllowed, NotAcceptable, PermissionDenied
from images.models import Image, Gallery, GalleryImage, average_image_color
from images.serializers import ImageSerializer, GallerySerializer, GalleryImageSerializer
from twz_server_django.rest_extensions import ReadOnlyModelViewSetMixin, CreatedModifiedByModelViewSetMixin
from pathlib import Path
from twz_server_django.settings import CACHE_ROOT
from twz_server_django.settings_private import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def rgb2hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

class ImageViewSet(ReadOnlyModelViewSetMixin):
    queryset = Image.objects.filter()
    serializer_class = ImageSerializer
    parser_classes = (JSONParser, FileUploadParser,)

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(ImageViewSet, self).list(request, *args, **kwargs)
        else:
            raise MethodNotAllowed('GET')

    @list_route(methods=['GET'])
    def make_colors(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            images = Image.objects.all()
            for image in images:
                r = requests.get(image.image.url, stream=True)
                data = r.content
                i = PilImage.open(BytesIO(data))
                average_color = average_image_color(i)
                if 'R' in average_color:
                    color = "rgb(%s,%s,%s)" % (average_color['R'], average_color['G'], average_color['B'])
                    image.color = color
                    image.save()

            return super(ImageViewSet, self).list(request, *args, **kwargs)
        else:
            raise MethodNotAllowed('GET')

    @list_route(methods=['POST',])
    def upload_base64(self, request, *args, **kwargs):
        if request.user.is_verified:
            data = request.data
            extension = 'jpg'
            if 'image' in data:
                if len(data['image']) > 0:
                    if re.compile('^data:image/jpeg;').match(data['image']) is not None:
                        image_type = 'image/jpeg'
                        extension = 'jpg'

                    if re.compile('^data:image/png;').match(data['image']) is not None:
                        image_type = 'image/png'
                        extension = 'png'

                    image_data = binascii.a2b_base64(
                        data['image'].replace('data:' + image_type + ';base64,', ''))
                    f = BytesIO(image_data)
                    pil_image = PilImage.open(f)
                    f.seek(0)

                    # TODO: make them all jpegs
                    average_color = average_image_color(pil_image)
                    color = "rgb(%s,%s,%s)" % (average_color['R'], average_color['G'], average_color['B'])
                    image = Image(width=pil_image.width, height=pil_image.height,
                                  created_by=request.user, modified_by=request.user, color=color)

                    image.image = UploadedFile(file=f,
                                               name='%s.%s' % (image.id, extension),
                                               content_type=image_type,
                                               size=len(image_data))
                    image.save()

                    f.close()

                return Response(ImageSerializer(image).data)

        raise NotFound()

    @list_route(methods=['POST',])
    def upload(self, request, *args, **kwargs):
        if request.user.is_verified and 'file' in request.data:
            data = request.data['file']
            extension = 'jpg'
            if len(data) > 0:

                pil_image = PilImage.open(data)
                # TODO: Convert image to JPEG so color averaging doesnt blow up.
                average_color = average_image_color(pil_image)
                color = "rgb(%s,%s,%s)" % (average_color['R'], average_color['G'], average_color['B'])
                image = Image(width=pil_image.width, height=pil_image.height,
                              created_by=request.user, modified_by=request.user, color=color)

                data.name = '%s.%s' % (image.id, extension)
                image.image = data
                image.save()

                return Response(ImageSerializer(image).data)

        raise PermissionDenied()

    @detail_route(methods=['GET',])
    def view(self, request, *args, **kwargs):
        resizer = request.GET.get('r', None)
        # quality_val = request.GET.get('q', '75')

        instance = self.get_object()
        cache_dir = Path(CACHE_ROOT)
        if not cache_dir.is_dir():
            cache_dir.mkdir()

        my_file = Path(os.path.join(CACHE_ROOT, str(instance.id)))

        if my_file.is_file():
            data = my_file.read_bytes()
            status_code = 200
            content_type = 'image/jpeg'
        else:
            r = requests.get(instance.image.url, stream=True)
            my_file.write_bytes(r.content)
            data = r.content
            content_type = r.headers['content-type']
            status_code = r.status_code

        if resizer:
            i = PilImage.open(BytesIO(data))
            i = i.convert('RGB')
            size = resizer.split('x')
            size[0] = int(size[0])
            size[1] = int(size[1])
            i.thumbnail(tuple(size), PilImage.ANTIALIAS)

            imgByteArr = BytesIO()
            i.save(imgByteArr, format='JPEG')
            imgByteArr = imgByteArr.getvalue()
        else:
            imgByteArr = data

        if status_code == 200:
            response = HttpResponse(content=imgByteArr, content_type=content_type)
        else:
            raise NotFound

        return response


    @list_route(methods=['GET',])
    def cache(self, request, *args, **kwargs):
        resizer = request.GET.get('r', None)
        url = request.GET.get('url', None)
        if url is None:
            raise NotFound()
        url_components = urlparse(url)
        path, file = os.path.split(url_components.path)
        cache_dir = Path(CACHE_ROOT)
        if not cache_dir.is_dir():
            cache_dir.mkdir()

        my_file = Path(os.path.join(CACHE_ROOT, str(file)))

        if my_file.is_file():
            data = my_file.read_bytes()
            status_code = 200
            content_type = 'image/jpeg'
            # r = requests.head(url, stream=True)
            # cache_last_modified = timezone.datetime.utcfromtimestamp(os.path.getmtime(os.path.join(CACHE_ROOT, str(file)))).replace(tzinfo=UTC)
            # last_modified = dateutil.parser.parse(r.headers['last-modified'])
            # if last_modified > cache_last_modified:
            #     r = requests.get(url, stream=True)
            #     my_file.write_bytes(r.content)
            #     data = r.content
            #     content_type = r.headers['content-type']
            #     status_code = r.status_code
            #
        else:
            r = requests.get(url, stream=True)
            my_file.write_bytes(r.content)
            data = r.content
            content_type = r.headers['content-type']
            status_code = r.status_code

        if resizer:
            i = PilImage.open(BytesIO(data))
            size = resizer.split('x')
            size[0] = int(size[0])
            size[1] = int(size[1])
            i.thumbnail(tuple(size))

            imgByteArr = BytesIO()
            i.save(imgByteArr, format='JPEG')
            imgByteArr = imgByteArr.getvalue()
        else:
            imgByteArr = data

        if status_code == 200:
            response = HttpResponse(content=imgByteArr, content_type=content_type)
        else:
            raise NotFound

        return response


class GalleryViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Gallery.objects.filter()
    serializer_class = GallerySerializer
    permission_classes = (IsAuthenticated,)
    # filter_backends = (SearchFilter, )
    # search_filter = ('title', 'text')

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(GalleryViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(GalleryViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(GalleryViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class GalleryImageViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = GalleryImage.objects.filter()
    serializer_class = GalleryImageSerializer
    permission_classes = (IsAuthenticated,)
    # filter_backends = (SearchFilter,)
    # search_filter = ('title', 'text')

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(GalleryImageViewSet, self).update(request, *args, **kwargs)

        raise MethodNotAllowed('PUT')

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(GalleryImageViewSet, self).create(request, *args, **kwargs)

        raise MethodNotAllowed('POST')

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super(GalleryImageViewSet, self).destroy(request, *args, **kwargs)

        raise MethodNotAllowed('DELETE')


class BeardViewSet(viewsets.GenericViewSet):
    serializer_class = ImageSerializer
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FileUploadParser,)

    @list_route(methods=['POST',])
    def upload_base64(self, request, *args, **kwargs):
        data = request.data
        extension = 'jpg'
        if 'image' in data:
            if len(data['image']) > 0:
                if re.compile('^data:image/jpeg;').match(data['image']) is not None:
                    image_type = 'image/jpeg'
                    extension = 'jpg'

                if re.compile('^data:image/png;').match(data['image']) is not None:
                    image_type = 'image/png'
                    extension = 'png'

                image_data = binascii.a2b_base64(
                    data['image'].replace('data:' + image_type + ';base64,', ''))
                f = BytesIO(image_data)

                client = boto3.client('rekognition', region_name='us-east-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                rekog_response = client.detect_faces(
                    Image={
                        'Bytes': f.read(),
                    },
                    Attributes=[
                        'ALL'
                    ]
                )
                response = {
                    'mustache': False,
                    'beard': False
                }
                if 'FaceDetails' in rekog_response:
                    face_data = rekog_response['FaceDetails']
                    for person in face_data:
                        if 'Mustache' in person:
                            if person['Mustache']['Value'] is True:
                                response['mustache'] = True
                        if 'Beard' in person:
                            if person['Beard']['Value'] is True:
                                response['beard'] = True

                return Response(response)
        raise NotFound()

    @list_route(methods=['POST',])
    def upload(self, request, *args, **kwargs):
        if 'file' in request.data:
            data = request.data['file']
            if len(data) > 0:

                # pil_image = PilImage.open(data)
                # color = "rgb(%s,%s,%s)" % (average_color['R'], average_color['G'], average_color['B'])
                # image = Image(width=pil_image.width, height=pil_image.height,
                #               created_by=request.user, modified_by=request.user, color=color)
                # uploaded_file = UploadedFile(file=f,
                #                              name='%s.jpg' % post.id,
                #                              content_type=type,
                #                              size=len(image_data))
                client = boto3.client('rekognition', region_name='us-east-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                rekog_response = client.detect_faces(
                    Image={
                        'Bytes': data.read(),
                    },
                    Attributes=[
                        'ALL'
                    ]
                )
                response = {
                    'mustache': False,
                    'beard': False
                }
                if 'FaceDetails' in rekog_response:
                    face_data = rekog_response['FaceDetails']
                    for person in face_data:
                        if 'Mustache' in person:
                            if person['Mustache']['Value'] is True:
                                response['mustache'] = True
                        if 'Beard' in person:
                            if person['Beard']['Value'] is True:
                                response['beard'] = True

                return Response(response)

        raise NotFound()


