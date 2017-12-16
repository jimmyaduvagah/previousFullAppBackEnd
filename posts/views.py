try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import binascii

import os
from uuid import UUID

import boto3
import django_filters
import requests
from PIL import Image
from django.core.files.uploadedfile import UploadedFile
from django.db.models.query_utils import Q
from django.shortcuts import render
from django.utils import timezone
from django.utils.six import BytesIO
from tempfile import NamedTemporaryFile

from rest_framework.exceptions import NotFound, MethodNotAllowed
from rest_framework.filters import SearchFilter

from attachments.permissions import IsAllowedOrSuperuser
from drf_users.models import PushToken
from images.models import Image as ImageObject, average_image_color
from ionic_api.request import PushNotificationRequest
from links.models import Link
from requests.exceptions import ConnectionError
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import Notification
from posts.models import PostReport
from posts.serializers import PostReportSerializer
from twz_server_django.notification_types import NOTIFICATION_TYPES
from twz_server_django.settings_private import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, IONIC_PUSH_GROUP
from .models import Post, PostLike
from .serializers import PostSerializer, PostLikeSerializer
import re
from django.contrib.contenttypes.models import ContentType
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin


class PostFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Post
        fields = ['parent_post_id', 'created_by_id']


class PostViewset(CreatedModifiedByModelViewSetMixin):
    # queryset = Post.objects.filter(parent_post_id=None)
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = PostFilter
    associated_object_id = None
    # TODO: add new request parser for file upload.

    def list(self, request, *args, **kwargs):
        associated_object_id = request.GET.get('associated_object_id', None)

        if associated_object_id:
            try:
                uuid = UUID(associated_object_id)
            except (ValueError, TypeError) as e:
                return Response({})

            self.associated_object_id = uuid

        response = super(PostViewset, self).list(request, *args, **kwargs)
        return response

    def get_queryset(self):
        qs = Post.objects_with_my_like.get_queryset(user_id=self.request.user.id).filter(parent_post_id=None, reported__lt=2)
        if self.associated_object_id:
            qs = qs.filter(associated_object_id=self.associated_object_id, reported__lt=2).order_by('-likes_count')
        else:
            qs = qs.filter(associated_object_id=None, reported__lt=2)
        return qs

    # TODO: duplicate method and use new method for binary image post uploads.
    def create(self, request, *args, **kwargs):
        linked_content_object = None
        if 'linked_content_object' in request.data:
            linked_content_object = request.data['linked_content_object']
            del request.data['linked_content_object']

        response = super(PostViewset, self).create(request, *args, **kwargs)
        post = Post.objects.get(pk=response.data['id'])

        if post.post_type == 2 or post.post_type == 3:
            link = Link.objects.create(data=linked_content_object, created_by=post.created_by, modified_by=post.modified_by)
            post.linked_content_type = ContentType.objects.get(app_label="links", model="link")
            post.linked_object_id = link.pk
            post.save()

        if post.post_type == 4:
            if 'image' in linked_content_object:
                if len(linked_content_object['image']) > 0:
                    if re.compile('^data:image/jpeg;').match(linked_content_object['image']) is not None:
                        type = 'image/jpeg'

                    if re.compile('^data:image/png;').match(linked_content_object['image']) is not None:
                        type = 'image/png'

                    # TODO: retrieve image if exists as binary data
                    image_data = binascii.a2b_base64(linked_content_object['image'].replace('data:' + type + ';base64,', ''))
                    temp_file = NamedTemporaryFile(delete=False)
                    temp_file.close()
                    f = open(temp_file.name, mode='wb')
                    f.write(image_data)
                    f.close()
                    f = open(temp_file.name, mode='rb')

                    pil_image = Image.open(f)
                    uploaded_file = UploadedFile(file=f,
                                                 name='%s.jpg' % post.id,
                                                 content_type=type,
                                                 size=len(image_data))
                    client = boto3.client('rekognition', region_name='us-east-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                    rekog_response = client.detect_faces(
                        Image={
                            'Bytes': image_data,
                        },
                        Attributes=[
                            'ALL'
                        ]
                    )
                    display_position = 'center'
                    face_data = None
                    if 'FaceDetails' in rekog_response:
                        if len(rekog_response['FaceDetails']) > 0:
                            if rekog_response['FaceDetails'][0]['BoundingBox']['Top'] < .33:
                                display_position = 'top'
                            elif rekog_response['FaceDetails'][0]['BoundingBox']['Top'] > .6:
                                display_position = 'bottom'

                        face_data = rekog_response['FaceDetails']

                    average_color = average_image_color(pil_image)
                    color = "rgb(%s,%s,%s)" % (average_color['R'], average_color['G'], average_color['B'])
                    image = ImageObject.objects.create(
                        image=uploaded_file,
                        width=pil_image.width,
                        height=pil_image.height,
                        created_by=post.created_by,
                        modified_by=post.modified_by,
                        display_position=display_position,
                        face_data=face_data,
                        color=color)

                    post.linked_content_type = ContentType.objects.get(app_label="images", model="image")
                    post.linked_object_id = image.pk
                    post.save()

                    f.close()
                    temp_file.close()
                    os.remove(temp_file.name)

        if post.parent_post is None:
            payload = {
                "post_id": str(post.id),
                "created_by_id": str(post.created_by_id),
                "image": post.created_by.get_profile_image_cache_url(),
                "type": NOTIFICATION_TYPES.NEW_POST
            }
            r = PushNotificationRequest()
            r.create({
                "send_to_all": True,
                # "tokens": ['fgKJr4Br_9Y:APA91bHjLX10CFRcaVQ-ehRPHJxocSRJ7UvRlN62A_GrjzaHass6dEgG1CdllXDFxq4N1xahWSPD6lMubd14bh3cVuRNt-oonwLLAW5-1HHDish-BcRGd_dcpB1eGzIcPt7uLaxCPXc8'],
                "notification": {
                    "message": "%s" % str(post.text_content),
                    "title": "%s made a post" % post.created_by,
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

        if post.parent_post:
            tokens_for_parent_post_creator_qs = PushToken.objects.filter(user=post.parent_post.created_by,
                                                                         push_group=IONIC_PUSH_GROUP,
                                                                         is_active=True).values_list('token').exclude(user=post.created_by_id)
            tokens_for_parent_post_creator = list()
            for token in tokens_for_parent_post_creator_qs:
                tokens_for_parent_post_creator.append(token[0])

            payload = {
                "comment_id": str(post.id),
                "image": post.created_by.get_profile_image_cache_url(),
                "post_id": str(post.parent_post_id),
                "created_by_id": str(post.created_by_id),
                "type": NOTIFICATION_TYPES.NEW_COMMENT
            }
            title = "%s commented on your post." % str(post.created_by)
            message = "%s" % post.text_content
            if post.parent_post.created_by_id != request.user.id:
                notif = Notification(to_user=post.parent_post.created_by,
                                     from_user=post.created_by,
                                     created_on=timezone.datetime.now(),
                                     title=title,
                                     message=message,
                                     payload=payload)
                notif.save()

            if len(tokens_for_parent_post_creator) > 0:
                r = PushNotificationRequest()
                r.create({
                    "tokens": list(tokens_for_parent_post_creator),
                    "notification": {
                        "message": message,
                        "title": title,
                        "payload": payload,
                        "ios": {
                            "badge": "1",
                            "sound": "default",
                            "priority": 10
                        },
                        "android": {
                            "sound": "default",
                            "priority": "high"
                        }
                    },
                    "profile": IONIC_PUSH_GROUP
                })

        return Response(PostSerializer(post).data)

    def retrieve(self, request, *args, **kwargs):
        response = super(PostViewset, self).retrieve(request, *args, **kwargs)
        unseen_notifications = Notification.objects.filter(to_user=request.user,
                                                           is_seen=False,
                                                           payload__contains={'post_id': response.data['id']})
        print(unseen_notifications.query)
        return response

class PostCreationViewset(viewsets.GenericViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAllowedOrSuperuser]

    def list(self, request, *args, **kwargs):
        return Response()

    def create(self, request, *args, **kwargs):
        if 'content' in request.data:
            urls = re.findall(re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', flags=re.IGNORECASE | re.MULTILINE), request.data['content'])
            content = []

            for url in urls:
                og = OpenGraph(url=url)

                if og.is_valid():
                    content.append(json.loads(og.to_json()))

            print(content)

        return Response(content)


class PostLikeViewset(CreatedModifiedByModelViewSetMixin):
    queryset = PostLike.objects.filter()
    serializer_class = PostLikeSerializer
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)


class CommentViewset(CreatedModifiedByModelViewSetMixin):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)

    def get_queryset(self):
        """
        This view should return a list of all the comments for a post
        as determined by the parent_id portion of the URL.
        """
        parent_id = self.kwargs['posts_pk']
        return Post.objects_with_my_like.get_queryset(user_id=self.request.user.id).filter(parent_post_id=parent_id)


# encoding: utf-8
import re
from bs4 import BeautifulSoup
import json

class OpenGraph(dict):
    """
    """
    valid = True

    required_attrs = ['title', 'type', 'image', 'url']

    def __init__(self, url=None, html=None, **kwargs):
        self._url = url

        for k in kwargs.keys():
            self[k] = kwargs[k]

        dict.__init__(self)

        if url is not None:
            self.fetch(url)

        if html is not None:
            self.parser(html)

    def __setattr__(self, name, val):
        self[name] = val

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            return None

    def fetch(self, url):
        """
        """
        headers = requests.utils.default_headers()
        headers.update({
            'User-Agent': 'OpenGraph Parser',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': ', '.join(('gzip', 'deflate')),
            'Accept': '*/*',
            'Connection': 'keep-alive',
        })
        try:
            if re.compile('\.mp4$').search(urlparse(url).path):
                response = requests.head(url, headers=headers)
            else:
                response = requests.get(url, headers=headers)
        except ConnectionError:
            self.valid = False
            return None

        parsed_url = urlparse(response.url)
        self['domain'] = parsed_url.netloc

        if re.compile(r'^image').search(response.headers['content-type']):
            return self.parse_image(response, parsed_url)
        elif re.compile(r'^video').search(response.headers['content-type']):
            return self.parse_video(response, parsed_url)
        else:
            html = response.content
            return self.parser(response, parsed_url)

    def parser(self, response, parsed_url):
        """
        """
        doc = BeautifulSoup(response.content, "html.parser")
        ogs = doc.html.head.findAll(property=re.compile(r'^og'))
        for og in ogs:
            self[og[u'property'][3:]]=og[u'content']

        if 'title' not in self:
            self['title'] = doc.html.head.title.text.replace("\n", "").replace("\r", "")

        if 'description' not in self:
            desc_search = doc.find(attrs={"name": "description"})
            if desc_search:
                if 'content' in desc_search.attrs:
                    if len(desc_search.attrs['content']) > 0:
                        self['description'] = desc_search.attrs['content']

        if 'description' not in self:
            desc_search = doc.find(name='p')
            print(desc_search)
            if desc_search:
                if desc_search:
                    self['description'] = desc_search.text

        if 'image' not in self:
            img_search = doc.html.body.findAll("img")
            if img_search:
                images = []
                possible_logo = ''
                redundent_image_check = {}

                for img in img_search:
                    if 'src' in img.attrs:
                        img_src = img.attrs['src']
                        if img_src not in redundent_image_check:
                            redundent_image_check[img_src] = img_src
                            if re.compile('^//').search(img_src):
                                img_src = "%s:%s" % (parsed_url.scheme, img_src)

                            if re.compile('^/').search(img_src):
                                img_src = "%s://%s%s" % (parsed_url.scheme, parsed_url.netloc, img_src)

                            if not re.compile('^http').search(img_src):
                                img_src = "%s://%s/%s" % (parsed_url.scheme, parsed_url.netloc, img_src)

                            if re.compile('/.*?logo[a-zA-Z0-9_\-]+?\.(png|jpg|gif)$|\?').search(img_src) and possible_logo == '':
                                possible_logo = img_src
                            else:
                                images.append(img_src)

                if possible_logo != '':
                    images.insert(0, possible_logo)

                self['images'] = images

        if 'type' not in self:
            self['type'] = 'website'

        if 'content_type' not in self:
            self['content_type'] = response.headers['content-type']

        if 'url' not in self:
            self['url'] = response.url

        self['display'] = 'horizontal'
        if 'image:height' in self and 'image:width' in self:
            if int(self['image:height']) >= 300 and int(self['image:width']) >= 300:
                self['display'] = 'vertical'


    def parse_image(self, response, parsed_url):
        if 'type' not in self:
            self['type'] = 'image'

        if 'content_type' not in self:
            self['content_type'] = response.headers['content-type']

        im = Image.open(BytesIO(response.content))

        if 'image:width' not in self:
            self['image:width'] = im.width

        if 'image:height' not in self:
            self['image:height'] = im.height

        if 'url' not in self:
            self['url'] = response.url

        if 'image' not in self:
            self['image'] = response.url

        im.close()

    def parse_video(self, response, parsed_url):
        if 'type' not in self:
            self['type'] = 'video'

        if 'content_type' not in self:
            self['content_type'] = response.headers['content-type']

        if 'url' not in self:
            self['url'] = response.url

        if 'video' not in self:
            self['video'] = response.url

    def is_valid(self):
        # return all([hasattr(self, attr) for attr in self.required_attrs])
        return self.valid

    def to_html(self):
        if not self.is_valid():
            return u"<meta property=\"og:error\" content=\"og metadata is not valid\" />"

        meta = u""
        for key,value in self.iteritems():
            meta += u"\n<meta property=\"og:%s\" content=\"%s\" />" %(key, value)
        meta += u"\n"

        return meta

    def to_json(self):
        if not self.is_valid():
            return json.dumps({'error':'og metadata is not valid'})

        return json.dumps(self)

    def to_xml(self):
        pass


class PostReportFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = PostReport
        fields = ['post_id', 'created_by_id']


class PostReportViewset(CreatedModifiedByModelViewSetMixin):
    queryset = PostReport.objects.filter()
    serializer_class = PostReportSerializer
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = PostReportFilter

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('delete')