from rest_framework import serializers

from twz_server_django.rest_extensions import CreatedModifiedByModelSerializerV2
from media.serializers import MediaSerializer
from module.models import UserAssessment
from .models import Module, ModuleCategory

class UserAssessmentSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = UserAssessment



class ModuleCategorySerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = ModuleCategory


class ModuleSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = Module


    category = ModuleCategorySerializer(read_only=True)
    category_id = serializers.UUIDField()

    main_media = MediaSerializer(read_only=True)
    main_media_id = serializers.UUIDField()

    user_assessment = UserAssessmentSerializer(read_only=True)
    user_assessment_id = serializers.UUIDField()


