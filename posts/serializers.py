from images.models import Image
from images.serializers import ImageSerializer
from links.models import Link
from links.serializers import LinkSerializer
from rest_framework.fields import ReadOnlyField

from posts.models import PostReport
from .models import Post, PostLike
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer, CreatedModifiedByModelSerializerV2
from rest_framework import serializers


class PostLinkedObjectRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, Link):
            return LinkSerializer(value).data
        if isinstance(value, Image):
            return ImageSerializer(value).data
        raise Exception('Unexpected type of tagged object')


class PostSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = Post
        fields = ('__all__')

    # TODO: Maybe make just post_type this field and have post_type_id like Mark did in created/modified_by?
    post_type_display = serializers.SerializerMethodField()
    # created_by_profile_image = serializers.CharField(read_only=True, source='getPublicProfileImageUrl')
    # profile_image = serializers.ImageField(read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True, required=False, source="get_profile_image")
    # created_by_profile_image
    my_like = serializers.CharField(read_only=True, required=False)

    linked_content_object = PostLinkedObjectRelatedField(read_only=True)

    def get_post_type_display(self, obj):
        return obj.get_post_type_display()

    def get_profile_image(self, obj):
        return obj.created_by.get_profile_image_cache_url()


class PostLikeSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = PostLike
        fields = ('__all__')


class PostReportSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = PostReport
        fields = ('__all__')



