from rest_framework import serializers

from courses.models import CourseProgress
from drf_users.serializers import UserSerializer
from twz_server_django.rest_extensions import P33ModelSerializer, CreatedModifiedByModelSerializer
from .models import Specialty, Course, CourseSectionType, CourseSection
from attachments.serializers import AttachmentSerializer



# Admin View Serializers

class SpecialtyAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Specialty

class CourseAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Course


class CourseSectionTypeAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = CourseSectionType

class CourseSectionAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = CourseSection

    supporting_files = AttachmentSerializer(many=True, read_only=True, source="getSupportingFiles")


class CourseSectionFullAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = CourseSection

    course = CourseAdminSerializer(many=False, read_only=False)
    section_type = CourseSectionTypeAdminSerializer(many=True, read_only=False)

class CourseFullAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Course

    specialty = SpecialtyAdminSerializer(many=False, read_only=False)
    course_sections = CourseSectionAdminSerializer(many=True, read_only=True, source='get_serializer_fields()')

class CourseProgressAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = CourseProgress

    user_id = serializers.UUIDField(read_only=True)
    user = serializers.CharField(read_only=True)
    course_id = serializers.UUIDField()
    course = serializers.CharField(read_only=True)
    course_section_id = serializers.UUIDField()
    course_section = serializers.UUIDField(read_only=True)

class CourseProgressFullAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = CourseProgress

    user_id = serializers.UUIDField(read_only=True)
    user = UserSerializer(many=False, read_only=True)
    course_id = serializers.UUIDField()
    course = CourseAdminSerializer(many=False, read_only=True)
    course_section_id = serializers.UUIDField()
    course_section = CourseSectionAdminSerializer(read_only=True)
