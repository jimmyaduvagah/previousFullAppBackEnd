from .models import Country, State
from rest_framework import serializers
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer


class CountrySerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Country

        fields = (
            'id',
            'name',
        )

class StateSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = State

        fields = (
            'id',
            'name',
        )
