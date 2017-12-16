from rest_framework import serializers

from images.models import Image, GalleryImage, Gallery
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer, P33ModelSerializer


class ImageSerializer(P33ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


    src = serializers.URLField(source='get_api_url')


class GalleryImageSerializer(P33ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = '__all__'

    order = serializers.IntegerField()
    gallery_id = serializers.UUIDField()
    image = ImageSerializer(read_only=True)
    image_id = serializers.UUIDField()


class GallerySerializer(P33ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'

    title = serializers.CharField()
    images = GalleryImageSerializer(many=True, source='images.all', read_only=True)
