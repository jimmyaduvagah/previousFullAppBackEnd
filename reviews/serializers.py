from reviews.models import ReviewTemplate, Review
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializerV2, CreatedModifiedByModelSerializer


class ReviewTemplateSerializer(CreatedModifiedByModelSerializerV2):

    class Meta:
        model = ReviewTemplate
        fields = '__all__'


class ReviewSerializer(CreatedModifiedByModelSerializerV2):

    class Meta:
        model = Review
        fields = '__all__'

