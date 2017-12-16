from rest_framework import serializers

from course_module_sections.serializers import CourseModuleSectionSerializer
from courses.models import Course, Category, CourseModule, CourseProgress
from images.serializers import ImageSerializer
from twz_server_django.rest_extensions import P33ModelSerializer, CreatedModifiedByModelSerializerV2


class CourseSerializer(P33ModelSerializer):
    class Meta:
        model = Course
        exclude = ('authors', 'tags')

    image = ImageSerializer(read_only=True)
    image_id = serializers.UUIDField(read_only=False)
    category = serializers.CharField(read_only=True)
    category_id = serializers.UUIDField(read_only=False)
    is_started = serializers.BooleanField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    vimeo = serializers.DictField(source='get_video', read_only=True)

class CourseSerializerForPost(P33ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'image_id', 'category_id', 'authors', 'tags', 'title', 'description', 'state', 'deleted', 'color', 'image',
                  'category', 'authors_json', 'vimeo_id')

    image = ImageSerializer(read_only=True)
    image_id = serializers.UUIDField(read_only=False)
    category = serializers.CharField(read_only=True)
    category_id = serializers.UUIDField(read_only=False)

class CourseCategorySerializer(P33ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CourseModuleSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = CourseModule
        fields = '__all__'

    image = ImageSerializer(read_only=True)
    image_id = serializers.UUIDField(read_only=False)


class CourseProgressSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = CourseProgress
        fields = '__all__'

