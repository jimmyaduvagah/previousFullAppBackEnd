from rest_framework import serializers
from drf_users.serializers import UserSerializer, UserFullSerializer
from twz_server_django.rest_extensions import P33ModelSerializer, CreatedModifiedByModelSerializer
from .models import Specialty, Course, CourseSectionType, CourseSection, CourseProgress
from attachments.serializers import AttachmentSerializer



#  View Serializers

class SpecialtySerializer(P33ModelSerializer):
    class Meta:
        model = Specialty

class SpecialtyFullSerializer(P33ModelSerializer):
    class Meta:
        model = Specialty

class CourseSerializer(P33ModelSerializer):
    class Meta:
        model = Course


class CourseSectionTypeSerializer(P33ModelSerializer):
    class Meta:
        model = CourseSectionType

class CourseSectionSerializer(P33ModelSerializer):
    class Meta:
        model = CourseSection

class CourseSectionFullSerializer(P33ModelSerializer):
    class Meta:
        model = CourseSection

    course = CourseSerializer(many=False, read_only=False)
    course_section_type = CourseSectionTypeSerializer(many=False, read_only=True)
    supporting_files = AttachmentSerializer(many=True, source="getSupportingFiles")

class CourseFullSerializer(P33ModelSerializer):
    class Meta:
        model = Course

    specialty = SpecialtySerializer(many=False, read_only=False)
    course_sections = CourseSectionSerializer(many=True, read_only=True)
    authors = UserSerializer(many=True, read_only=True)

class CourseProgressSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = CourseProgress

    course_id = serializers.UUIDField()
    course = serializers.CharField(read_only=True)
    course_section_id = serializers.UUIDField()
    course_section = serializers.CharField(read_only=True)
    user_id = serializers.UUIDField()
    user = serializers.CharField(read_only=True)


class CourseProgressFullSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = CourseProgress

    course_id = serializers.UUIDField()
    course = CourseSerializer(many=False, read_only=True)
    course_section_id = serializers.UUIDField()
    course_section = CourseSectionSerializer(many=False, read_only=True)
    user_id = serializers.UUIDField()
    user = serializers.CharField(read_only=True)


