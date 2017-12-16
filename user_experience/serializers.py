
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer
from rest_framework import serializers
from .models import UserProfileExperience, UserProfileExperienceType
from institutions.serializers import InstitutionSerializer, InstitutionFullSerializer



class UserProfileExperienceSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = UserProfileExperience
        exclude = ('is_deleted', )

    institution = InstitutionSerializer(read_only=True)
    institution_id = serializers.UUIDField()
    type = serializers.CharField(read_only=True)
    type_id = serializers.UUIDField()

class UserProfileExperienceTypeSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = UserProfileExperienceType
        fields = '__all__'


class UserProfileExperienceFullSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = UserProfileExperience
        fields = '__all__'

    institution = InstitutionFullSerializer()
    type = UserProfileExperienceTypeSerializer()


class UserProfileExperienceTypeSelect2Serializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = UserProfileExperienceType
        fields = ('id', 'title', 'institution_search_type')


