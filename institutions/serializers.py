
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer
from rest_framework import serializers
from .models import Institution, InstitutionType

class InstitutionTypeSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = InstitutionType
        fields = '__all__'

class InstitutionSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'

    type = serializers.CharField(read_only=True)
    type_id = serializers.UUIDField()


class InstitutionFullSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'

    type = serializers.CharField(read_only=True)

class InstitutionSelect2Serializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Institution

        fields = ('id', 'type', 'title')

