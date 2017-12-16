from drf_users.serializers import UserMinimalSerializer
from rest_framework import serializers

from connections.models import Connection, ConnectionRequest
from twz_server_django.rest_extensions import P33ModelSerializer, CreatedModifiedByModelSerializerV2


class ConnectionSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = Connection
        fields = '__all__'

    from_user_obj = serializers.CharField(read_only=True, source='from_user')
    from_user_id = serializers.UUIDField()

    to_user_obj = UserMinimalSerializer(read_only=True, source='to_user')
    to_user_id = serializers.UUIDField()

    state = serializers.SerializerMethodField(read_only=True)
    state_id = serializers.CharField(source='state')

    def get_state(self, obj):
        return obj.get_state_display()


class ConnectionRequestSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = ConnectionRequest
        fields = ('id', 'from_user_obj', 'from_user_id', 'to_user_obj', 'to_user_id', 'state', 'state_id')

    from_user_obj = UserMinimalSerializer(read_only=True, source='from_user')
    from_user_id = serializers.UUIDField()

    to_user_obj = UserMinimalSerializer(read_only=True, source='to_user')
    to_user_id = serializers.UUIDField()

    state = serializers.SerializerMethodField(read_only=True)
    state_id = serializers.CharField(source='state', required=False)

    def get_state(self, obj):
        return obj.get_state_display()


class ConnectionRequestFromSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = ConnectionRequest
        fields = ('id', 'from_user', 'from_user_id', 'to_user_obj', 'to_user_id', 'state', 'state_id')

    from_user_obj = serializers.CharField(read_only=True, source='from_user')
    from_user_id = serializers.UUIDField()

    to_user_obj = UserMinimalSerializer(read_only=True, source='to_user')
    to_user_id = serializers.UUIDField()

    state = serializers.SerializerMethodField(read_only=True)
    state_id = serializers.CharField(source='state')

    def get_state(self, obj):
        return obj.get_state_display()


class ConnectionRequestToSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = ConnectionRequest
        fields = ('id', 'from_user_obj', 'from_user_id', 'to_user_obj', 'to_user_id', 'state', 'state_id')

    from_user_obj = UserMinimalSerializer(read_only=True, source='from_user')
    from_user_id = serializers.UUIDField()

    to_user_obj = serializers.CharField(read_only=True, source='to_user')
    to_user_id = serializers.UUIDField()

    state = serializers.SerializerMethodField(read_only=True)
    state_id = serializers.CharField(source='state', required=False)

    def get_state(self, obj):
        return obj.get_state_display()
