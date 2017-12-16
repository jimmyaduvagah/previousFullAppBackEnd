from rest_framework import serializers

from assessments.models import Assessment
from courses.serializers import CourseSerializer, CourseSectionSerializer, CourseProgressSerializer
from drf_users.serializers import UserSerializer
from twz_server_django.rest_extensions import P33ModelSerializer, CreatedModifiedByModelSerializer


class AssessmentSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Assessment

    user_assessed_id = serializers.UUIDField()
    user_assessed = serializers.CharField(read_only=True)
    user_who_assessed_id = serializers.UUIDField()
    user_who_assessed = serializers.CharField(read_only=True)
    rating = serializers.IntegerField(min_value=0, max_value=5)
    course_id = serializers.UUIDField()
    course = serializers.CharField(read_only=True)
    course_section_id = serializers.UUIDField()
    course_section = serializers.CharField(read_only=True)
    course_progress_id = serializers.UUIDField()
    course_progress = serializers.CharField(read_only=True)

class AssessmentFullSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Assessment

    user_assessed_id = serializers.UUIDField()
    user_assessed = UserSerializer(many=False, read_only=True)
    user_who_assessed_id = serializers.UUIDField()
    user_who_assessed = UserSerializer(many=False, read_only=True)
    rating = serializers.IntegerField()
    course_id = serializers.UUIDField()
    course = CourseSerializer(many=False, read_only=True)
    course_section_id = serializers.UUIDField()
    course_section = CourseSectionSerializer(many=False, read_only=True)
    course_progress_id = serializers.UUIDField()
    course_progress = CourseProgressSerializer(many=False, read_only=True)


