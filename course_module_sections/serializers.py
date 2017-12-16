from rest_framework import serializers

from course_module_sections.models import SectionAssessment, SectionImage, SectionAttachment, SectionText, \
    SectionVideoContainer, CourseModuleSection, SectionQuiz, SectionGallery, SectionSurveyGroup
from images.serializers import ImageSerializer, GallerySerializer
from quizzes.serializers import QuizSerializer
from twz_server_django.rest_extensions import P33ModelSerializer



class SectionVideoContainerSerializer(P33ModelSerializer):
    class Meta:
        model = SectionVideoContainer
        fields = '__all__'

    vimeo = serializers.DictField(source='get_video', read_only=True)
    type = serializers.CharField(source="get_type", read_only=True)


class SectionVideoContainerNoAPICallSerializer(P33ModelSerializer):
    class Meta:
        model = SectionVideoContainer
        fields = '__all__'

    type = serializers.CharField(source="get_type", read_only=True)


class SectionSurveyGroupSerializer(P33ModelSerializer):
    class Meta:
        model = SectionSurveyGroup
        fields = '__all__'

    survey_group = serializers.DictField(source='get_survey_group', read_only=True)
    type = serializers.CharField(source="get_type", read_only=True)

class SectionTextSerializer(P33ModelSerializer):
    class Meta:
        model = SectionText
        fields = '__all__'

    type = serializers.CharField(source="get_type", read_only=True)



class SectionQuizSerializer(P33ModelSerializer):
    class Meta:
        model = SectionQuiz
        fields = '__all__'

    quiz = QuizSerializer(read_only=True)
    quiz_id = serializers.UUIDField()
    type = serializers.CharField(source="get_type", read_only=True)


class SectionAttachmentSerializer(P33ModelSerializer):
    class Meta:
        model = SectionAttachment
        fields = '__all__'

    type = serializers.CharField(source="get_type", read_only=True)


class SectionImageSerializer(P33ModelSerializer):
    class Meta:
        model = SectionImage
        fields = ('id', 'title', 'text', 'html', 'image', 'image_id', 'type')

    image = ImageSerializer(read_only=True)
    image_id = serializers.UUIDField()
    type = serializers.CharField(source="get_type", read_only=True)


class SectionGallerySerializer(P33ModelSerializer):
    class Meta:
        model = SectionGallery
        fields = ('id', 'title', 'text', 'html', 'gallery', 'gallery_id', 'type')

    gallery = GallerySerializer(read_only=True)
    gallery_id = serializers.UUIDField()
    type = serializers.CharField(source="get_type", read_only=True)


class SectionAssessmentSerializer(P33ModelSerializer):
    class Meta:
        model = SectionAssessment
        fields = '__all__'

    type = serializers.CharField(source="get_type", read_only=True)


class SectionRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        """
        Serialize bookmark instances using a bookmark serializer,
        and note instances using a note serializer.
        """
        found = True
        if isinstance(value, SectionText):
            serializer = SectionTextSerializer(value)
        elif isinstance(value, SectionImage):
            serializer = SectionImageSerializer(value)
        elif isinstance(value, SectionAttachment):
            serializer = SectionAttachmentSerializer(value)
        elif isinstance(value, SectionGallery):
            serializer = SectionGallerySerializer(value)
        elif isinstance(value, SectionSurveyGroup):
            serializer = SectionSurveyGroupSerializer(value)
        elif isinstance(value, SectionQuiz):
            serializer = SectionQuizSerializer(value)
        elif isinstance(value, SectionVideoContainer):
            serializer = SectionVideoContainerNoAPICallSerializer(value)
        elif isinstance(value, SectionAssessment):
            serializer = SectionAssessmentSerializer(value)
        else:
            found = False
            raise Exception('Unexpected type of tagged object')

        if found is True:
            return serializer.data
        else:
            return None


class CourseModuleSectionSerializer(P33ModelSerializer):
    class Meta:
        model = CourseModuleSection
        fields = '__all__'


class CourseModuleSectionFullSerializer(P33ModelSerializer):
    class Meta:
        model = CourseModuleSection
        fields = '__all__'

    related = SectionRelatedField(queryset='')

