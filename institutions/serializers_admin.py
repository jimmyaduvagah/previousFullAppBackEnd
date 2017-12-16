
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer
from rest_framework import serializers
from .models import Institution, InstitutionType

class InstitutionTypeAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = InstitutionType

class InstitutionAdminSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Institution
