from rest_framework import serializers
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializerV2
from module_progress.models import ModuleProgress


class ModuleProgressSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = ModuleProgress
        fields = (
            'id',
            'modified_on',
            'created_on',
            'modified_by_id',
            'created_by_id',
            'modified_by',
            'created_by',
            'object',
            'completed',
            'percent_completed',
            'has_assessment',
            'assessment_submitted',
            'assessment_submitted_on',
            'assessment_response_completed',
            'module_id',
            'current_media_id',
            'user_id'
        )

    current_media_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    module_id = serializers.UUIDField()

