from surveys.models import Survey, SurveyResponse
from twz_server_django.rest_extensions import CreatedModifiedByModelSerializerV2


class SurveySerializer(CreatedModifiedByModelSerializerV2):

    class Meta:
        model = Survey
        fields = '__all__'


class SurveyResponseSerializer(CreatedModifiedByModelSerializerV2):

    class Meta:
        model = SurveyResponse
        fields = '__all__'

