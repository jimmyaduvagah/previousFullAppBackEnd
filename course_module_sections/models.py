from uuid import UUID

import vimeo
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
import markdown2

# Create your models here.
from django.db.models.deletion import SET_NULL
from ordered_model.models import OrderedModel
from storages.backends.s3boto import S3BotoStorage

from surveys.models import Survey
from twz_server_django.model_mixins import CreatedModifiedModel, CreatedModifiedModelManager
from twz_server_django.settings import AWS_STORAGE_BUCKET_NAME, AWS_DEFAULT_ACL
from twz_server_django.settings_private import VIMEO_ACCESS_TOKEN, VIMEO_CLIENT_KEY, VIMEO_CLIENT_SECRET


def make_markdown(content):
    # TODO: make sure we escape any bad stuff like JS.  We do this in the intranet with beautiful soup.
    return markdown2.markdown(content, extras=["fenced-code-blocks"])

class CourseModuleSectionManager(CreatedModifiedModelManager):

    def get_queryset(self, *args, **kwargs):
        qs = super(CourseModuleSectionManager, self).get_queryset().order_by('course_module', 'order')
        return qs


class CourseModuleSection(CreatedModifiedModel, OrderedModel):

    objects = CourseModuleSectionManager()

    course_module = models.ForeignKey('courses.CourseModule', null=False, blank=False)
    content_type = models.ForeignKey(ContentType, null=False, blank=False, related_name="rel_course_module_sections")
    object_id = models.UUIDField(null=False, blank=False)
    related = GenericForeignKey('content_type', 'object_id')

    order_with_respect_to = 'course_module'

    def __str__(self):
        return u"%s Course Module Section %s %s" % (self.course_module, self.content_type, self.object_id)


class SectionVideoContainer(CreatedModifiedModel):

    title = models.CharField(max_length=255, null=False, blank=True, default='')
    text = models.TextField(null=False, blank=True)
    html = models.TextField(null=False, blank=True, help_text="This is auto generated from Text.")
    length = models.PositiveIntegerField(null=False, blank=True, default=0, help_text='length in seconds')
    watches = models.PositiveIntegerField(null=False, blank=True, default=0)
    vimeo_id = models.CharField(max_length=255, null=False, blank=True, default='')

    def __str__(self):
        return u"%s Video Container" % self.title

    def get_type(self):
        return "video"

    def get_video(self):
        if self.vimeo_id:
            v = vimeo.VimeoClient(
                token=VIMEO_ACCESS_TOKEN,
                key=VIMEO_CLIENT_KEY,
                secret=VIMEO_CLIENT_SECRET)

            response = v.get("/videos/%s" % (self.vimeo_id,), params={})
            data = response.json()
        else:
            data = None
        return data

    def save(self, *args, **kwargs):
        self.html = make_markdown(self.text)
        super(SectionVideoContainer, self).save(*args, **kwargs)


class SectionText(CreatedModifiedModel):

    title = models.CharField(max_length=255, null=False, blank=True, default='')
    text = models.TextField(null=False, blank=True, help_text="Markdown can be used here.")
    html = models.TextField(null=False, blank=True, help_text="This is auto generated from Text.")
    textColor = models.CharField(max_length=255, null=False, blank=True, default='')
    backgroundColor = models.CharField(max_length=255, null=False, blank=True, default='')

    def __str__(self):
        return u"%s Text Section" % self.title

    def get_type(self):
        return "text"

    def save(self, *args, **kwargs):
        self.html = make_markdown(self.text)
        super(SectionText, self).save(*args, **kwargs)


class SectionSurveyGroup(CreatedModifiedModel):

    text = models.TextField(null=False, blank=True, help_text="Markdown can be used here.")
    html = models.TextField(null=False, blank=True, help_text="This is auto generated from Text.")
    textColor = models.CharField(max_length=255, null=False, blank=True, default='')
    backgroundColor = models.CharField(max_length=255, null=False, blank=True, default='')
    survey = models.ForeignKey('surveys.Survey', null=False, blank=False)
    survey_group_id = models.UUIDField(null=False, blank=False)

    def __str__(self):
        return u"%s - %s - Survey Group Section" % (self.survey.title, self.survey_group_id)

    def get_type(self):
        return "survey-group"

    def save(self, *args, **kwargs):
        self.html = make_markdown(self.text)
        super(SectionSurveyGroup, self).save(*args, **kwargs)

    def get_survey_group(self):
        survey = Survey.objects.get(id=self.survey_id)
        survey_group = None
        for sg in survey.groups:
            if sg['uuid'] == str(self.survey_group_id):
                survey_group = sg
                break

        return survey_group


class SectionAttachment(CreatedModifiedModel):

    title = models.CharField(max_length=255, null=False, blank=True, default='')
    text = models.TextField(null=False, blank=True)
    html = models.TextField(null=False, blank=True, help_text="This is auto generated from Text.")
    file = models.FileField(null=True, blank=True, upload_to='course_section_attachments/',
                              storage=S3BotoStorage(bucket=AWS_STORAGE_BUCKET_NAME, acl=AWS_DEFAULT_ACL))

    def __str__(self):
        return u"%s Text Section" % self.title

    def get_type(self):
        return "attachment"

    def save(self, *args, **kwargs):
        self.html = make_markdown(self.text)
        super(SectionAttachment, self).save(*args, **kwargs)


class SectionImage(CreatedModifiedModel):

    title = models.CharField(max_length=255, null=False, blank=True, default='')
    text = models.TextField(null=False, blank=True)
    html = models.TextField(null=False, blank=True, help_text="This is auto generated from Text.")
    image = models.ForeignKey('images.Image', null=True, blank=True, on_delete=SET_NULL)

    def __str__(self):
        return u"%s Image Section" % self.title

    def get_type(self):
        return "image"

    def save(self, *args, **kwargs):
        self.html = make_markdown(self.text)
        super(SectionImage, self).save(*args, **kwargs)


class SectionGallery(CreatedModifiedModel):

    title = models.CharField(max_length=255, null=False, blank=True, default='')
    text = models.TextField(null=False, blank=True)
    html = models.TextField(null=False, blank=True, help_text="This is auto generated from Text.")
    gallery = models.ForeignKey('images.Gallery', null=True, blank=True, on_delete=SET_NULL)

    def __str__(self):
        return u"%s Gallery Section" % self.title

    def get_type(self):
        return "gallery"

    def save(self, *args, **kwargs):
        self.html = make_markdown(self.text)
        super(SectionGallery, self).save(*args, **kwargs)


class SectionQuiz(CreatedModifiedModel):

    title = models.CharField(max_length=255, null=False, blank=True, default='')
    quiz = models.ForeignKey('quizzes.Quiz', null=True, blank=True, on_delete=SET_NULL)


    def __str__(self):
        return u"%s Image Section" % self.title

    def get_type(self):
        return "quiz"


class SectionAssessment(CreatedModifiedModel):

    title = models.CharField(max_length=255, null=False, blank=True, default='')
    text = models.TextField(null=False, blank=True)
    html = models.TextField(null=False, blank=True, help_text="This is auto generated from Text.")

    def save(self, *args, **kwargs):
        self.html = make_markdown(self.text)
        super(SectionAssessment, self).save(*args, **kwargs)

    def get_type(self):
        return "assessment"

    def __str__(self):
        return u"%s Image Assessment" % self.title
