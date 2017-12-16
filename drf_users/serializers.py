from connections.models import ConnectionRequest
from drf_users.models import PushToken
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializer, P33ModelSerializer, \
    CreatedModifiedByModelSerializerV2
from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import User
from user_experience.serializers import UserProfileExperienceFullSerializer, UserProfileExperienceSerializer


class UserProfileSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = User

        # exclude = ('user',)

    user_id = serializers.UUIDField(read_only=True, source='id')
    profile_image = serializers.CharField(read_only=True, source='get_profile_image_cache_url')


class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushToken
        fields = '__all__'

    token = serializers.CharField(required=True)
    user = serializers.UUIDField(read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    device_id = serializers.CharField(required=True)
    push_group = serializers.CharField(required=True)
    app_version = serializers.CharField(required=False)
    device_platform = serializers.CharField(required=True)
    device_manufacturer = serializers.CharField(required=False, default="", allow_blank=True)
    device_model = serializers.CharField(required=False, default="", allow_blank=True)
    device_version = serializers.CharField(required=False, default="", allow_blank=True)


class UserProfileMiniSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = User
        fields = ('profile_image',)

    profile_image = serializers.CharField(read_only=True, source='get_profile_image_cache_url')


class UserRegisterSerializer(serializers.Serializer):
    class Meta:
        pass

    email = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, min_length=8)
    first_name = serializers.CharField(required=True, min_length=2)
    last_name = serializers.CharField(required=True, min_length=2)
    invitation_code = serializers.CharField(required=False, allow_blank=True)




class UserProfileCreateSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = User

        # exclude = ('user',)

    user_id = serializers.UUIDField(read_only=False)
    profile_image = serializers.CharField(read_only=True, source='get_profile_image_cache_url')

class UserProfileFullSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = User

        # exclude = ('user',)

    user_id = serializers.UUIDField(read_only=True)
    profile_image = serializers.CharField(read_only=True, source='get_profile_image_cache_url')
    experience = UserProfileExperienceFullSerializer(many=True, read_only=True, source='getUserExpereinces')


class UserSerializer(CreatedModifiedByModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'groups', 'full_name', 'email', 'bio', 'bio_html',
                  'is_staff', 'verified_email', 'email_verification_code', 'is_verified', 'phone_number',
                  'phone_country_dial_code', 'phone_country_code', 'is_superuser',
                  'verified_phone', 'phone_number_verification_code', 'invitation_code_used_to_join',
                  'profile_image', 'banner_image', 'date_of_birth', 'gender', 'nationality', 'nationality_id',
                  'town_of_residence', 'town_of_residence_id', 'completed_initial_setup',
                  'place_of_birth', 'place_of_birth_id', 'connected', 'pending_request')


    full_name = serializers.CharField(read_only=True, source="get_full_name")
    # TODO: Check if this is correct now that is_verified is an actual field
    is_verified = serializers.BooleanField(read_only=True, source='verified_email')
    nationality = serializers.CharField(read_only=True)
    nationality_id = serializers.UUIDField()
    profile_image = serializers.CharField(read_only=True, source='get_profile_image_cache_url')
    # profile_image = serializers.ImageField(read_only=True)
    place_of_birth = serializers.CharField(read_only=True)
    place_of_birth_id = serializers.UUIDField()
    town_of_residence = serializers.CharField(read_only=True)
    town_of_residence_id = serializers.UUIDField()
    completed_initial_setup = serializers.BooleanField()
    connected = serializers.BooleanField(read_only=True)
    pending_request = serializers.UUIDField(read_only=True)


class UserNotMeSerializer(CreatedModifiedByModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'full_name', 'bio_html',
                  'profile_image', 'banner_image', 'date_of_birth', 'gender', 'nationality', 'nationality_id',
                  'town_of_residence', 'town_of_residence_id', 'place_of_birth', 'place_of_birth_id', 'connected', 'pending_request')


    full_name = serializers.CharField(read_only=True, source="get_full_name")
    # TODO: Check if this is correct now that is_verified is an actual field
    nationality = serializers.CharField(read_only=True)
    nationality_id = serializers.UUIDField()
    profile_image = serializers.CharField(read_only=True, source='get_profile_image_cache_url')
    # profile_image = serializers.ImageField(read_only=True)
    place_of_birth = serializers.CharField(read_only=True)
    place_of_birth_id = serializers.UUIDField()
    town_of_residence = serializers.CharField(read_only=True)
    town_of_residence_id = serializers.UUIDField()
    connected = serializers.BooleanField(read_only=True)
    pending_request = serializers.UUIDField(read_only=True)


class UserMessageSerializer(CreatedModifiedByModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'full_name', )


    full_name = serializers.CharField(read_only=True, source="get_full_name")


class UserUpdateSerializer(CreatedModifiedByModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name',)


class UserFullSerializer(CreatedModifiedByModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'groups', 'courses_completed')

    groups = GroupSerializer(many=True, read_only=True)


class UserMinimalSerializer(CreatedModifiedByModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'full_name', 'profile_image', 'town_of_residence')

    full_name = serializers.SerializerMethodField(read_only=True)
    town_of_residence = serializers.CharField(read_only=True)

    def get_full_name(self, obj):
        return "%s %s" % (obj.first_name, obj.last_name)


class UserMinimalWithFriendshipSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'full_name', 'profile_image', 'town_of_residence', 'connected', 'pending_request')

    full_name = serializers.SerializerMethodField(read_only=True)
    town_of_residence = serializers.CharField(read_only=True)
    connected = serializers.BooleanField(read_only=True)
    pending_request = serializers.UUIDField(read_only=True)
    profile_image = serializers.CharField(read_only=True, source='get_profile_image_cache_url')

    def get_full_name(self, obj):
        return "%s %s" % (obj.first_name, obj.last_name)