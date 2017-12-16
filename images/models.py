import uuid
from uuid import UUID

import boto3
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

# Create your models here.
from ordered_model.models import OrderedModel
from storages.backends.s3boto import S3BotoStorage

from twz_server_django.model_mixins import CreatedModifiedModel
from twz_server_django.settings import AWS_STORAGE_BUCKET_NAME, AWS_DEFAULT_ACL, SERVER_NAME, SERVER_PORT, \
    SERVER_PROTOCOL
from twz_server_django.settings_private import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def content_file_name(instance, filename):
    return 'images/%s-%s' % (instance.id, filename)


class Image(CreatedModifiedModel):
    class Meta:
        ordering = ["-created_on",]

    image = models.ImageField(null=True, blank=True, width_field='width', height_field='height',
                              upload_to=content_file_name,
                              storage=S3BotoStorage(bucket=AWS_STORAGE_BUCKET_NAME, acl=AWS_DEFAULT_ACL))
    width = models.PositiveIntegerField(default=0, null=False, blank=True)
    height = models.PositiveIntegerField(default=0, null=False, blank=True)
    color = models.CharField(default='rgb(255,255,255)', max_length=20, blank=False, null=False)
    display_position = models.CharField(default='center', max_length=10, blank=False, null=False)
    face_data = JSONField(default=None, null=True, blank=True)

    def get_api_url(self):
        return '%s%s:%s/api/v1/images/%s/view/' % (SERVER_PROTOCOL, SERVER_NAME, SERVER_PORT, self.id)

    def __str__(self):
        return '%s-%s' % (self.image, self.created_on)

    def get_face_data(self):
        client = boto3.client('rekognition', region_name='us-east-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        rekog_response = client.detect_faces(
            Image={
                'Bytes': self.image.read(),
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

            self.display_position = display_position
            self.face_data = face_data
            self.save()


class Gallery(CreatedModifiedModel):
    class Meta:
        verbose_name_plural = "Galleries"

    title = models.CharField(max_length=255, default="Gallery", null=False, blank=True)

    def __str__(self):
        if self.title == '':
            title = self.id.__str__()
        else:
            title = self.title
        return '%s' % title


class GalleryImage(CreatedModifiedModel, OrderedModel):
    class Meta:
        ordering = ["order"]

    order_with_respect_to = 'gallery'
    gallery = models.ForeignKey('images.Gallery', null=False, blank=False, related_name='images')
    image = models.ForeignKey('images.Image', null=False, blank=False)

    def get_api_url(self):
        return self.image.get_api_url()

    def __str__(self):
        return '%s-%s' % (self.gallery, self.image)


def average_image_color(imagedata):
    channel_histograms = {}
    color_averages = {}
    for mode in imagedata.mode:
        channel_histograms[mode] = channel_histogram(imagedata, mode)
        if channel_histograms[mode] is not False:
            color_averages[mode] = round(
                sum(i * w for i, w in enumerate(channel_histograms[mode])) / sum(channel_histograms[mode]))


    return color_averages


def channel_histogram(imagedata, mode):
    h = imagedata.histogram()
    color = False
    if mode == 'R':
        color = h[0:256]
    if mode == 'G':
        color = h[256:256 * 2]
    if mode == 'B':
        color = h[256 * 2: 256 * 3]

    return color
