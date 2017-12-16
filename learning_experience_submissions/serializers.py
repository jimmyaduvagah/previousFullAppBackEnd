from rest_framework import serializers

from images.serializers import ImageSerializer
from learning_experience_submissions.models import LESubmission, LESubmissionRating
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializerV2


class LESubmissionRatingSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = LESubmissionRating
        fields = '__all__'

    average_rating = serializers.IntegerField(read_only=True)
    average_ratings = serializers.ListField(read_only=True)
    approved = serializers.BooleanField(read_only=True)
    approved_on = serializers.DateTimeField(read_only=True)
    created_on = serializers.DateTimeField(required=False)
    modified_on = serializers.DateTimeField(required=False)


class LESubmissionRatingNewVersionSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = LESubmissionRating
        fields = '__all__'

    average_rating = serializers.IntegerField(read_only=True)
    average_ratings = serializers.ListField(read_only=True)
    approved = serializers.BooleanField(read_only=True)
    approved_on = serializers.DateTimeField(read_only=True)
    le_submission = serializers.UUIDField()
    created_on = serializers.DateTimeField()
    modified_on = serializers.DateTimeField()
    created_by_id = serializers.UUIDField()
    modified_by_id = serializers.UUIDField()


class LESubmissionSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = LESubmission
        fields = '__all__'

    ratings = LESubmissionRatingSerializer(source='get_ratings', read_only=True, many=True)
    versions = serializers.ListField(read_only=True)
    number_of_ratings = serializers.IntegerField(read_only=True)
    average_rating = serializers.IntegerField(read_only=True)
    average_ratings = serializers.DictField(read_only=True)
    approved = serializers.BooleanField(read_only=True)
    approved_on = serializers.DateTimeField(read_only=True)
    submitted = serializers.BooleanField(read_only=True)
    submitted_on = serializers.DateTimeField(read_only=True)
    image = ImageSerializer(read_only=True)
    image_id = serializers.UUIDField(required=False, default=None)
    created_on = serializers.DateTimeField(required=False)
    modified_on = serializers.DateTimeField(required=False)


class LESubmissionListSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = LESubmission
        exclude = ('markdown', 'html', )

    versions = serializers.ListField(read_only=True)
    number_of_ratings = serializers.IntegerField(read_only=True)
    average_rating = serializers.IntegerField(read_only=True)
    average_ratings = serializers.DictField(read_only=True)
    approved = serializers.BooleanField(read_only=True)
    approved_on = serializers.DateTimeField(read_only=True)
    submitted = serializers.BooleanField(read_only=True)
    submitted_on = serializers.DateTimeField(read_only=True)
    image = ImageSerializer(read_only=True)
    image_id = serializers.UUIDField(required=False, default=None)
    created_on = serializers.DateTimeField(required=False)
    modified_on = serializers.DateTimeField(required=False)
    have_i_rated = serializers.BooleanField(read_only=True)


class LESubmissionNewVersionSerializer(CreatedModifiedByModelSerializerV2):
    class Meta:
        model = LESubmission
        exclude = ('versions', )

    ratings = LESubmissionRatingNewVersionSerializer(source='get_ratings', many=True)
    number_of_ratings = serializers.IntegerField()
    average_rating = serializers.IntegerField()
    average_ratings = serializers.DictField()
    approved = serializers.BooleanField()
    approved_on = serializers.DateTimeField()
    submitted = serializers.BooleanField()
    submitted_on = serializers.DateTimeField()
    created_on = serializers.DateTimeField()
    modified_on = serializers.DateTimeField()
    created_by_id = serializers.UUIDField()
    modified_by_id = serializers.UUIDField()
