from notifications.models import Notification
from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('__all__')

    from_user = serializers.CharField(read_only=True)
    from_user_id = serializers.UUIDField(read_only=False)
    to_user = serializers.CharField(read_only=True)
    to_user_id = serializers.UUIDField(read_only=False)
    profile_image = serializers.SerializerMethodField(read_only=True, required=False, source="get_profile_image")

    def get_profile_image(self, obj):
        return obj.from_user.get_profile_image_cache_url()
