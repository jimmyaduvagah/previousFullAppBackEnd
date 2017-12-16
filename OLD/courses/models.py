from django.db import models
from twz_server_django.model_mixins import CreatedModifiedModel
from ordered_model.models import OrderedModel
from django.contrib.postgres.fields import JSONField
from attachments.models import Attachment


class Specialty(CreatedModifiedModel):


    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Specialties"

    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    image = models.FileField(null=True, blank=True, upload_to='specialty_images/')
    icon = models.FileField(null=True, blank=True, upload_to='specialty__icon_images/')
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    color = models.CharField(null=False, blank=False, default='#014386', max_length=50)

    def __str__(self):
        return u"%s Specialty" % self.title


COURSE_STATE_CHOICES = (
    ("PUB","Published"),
    ("NOP","Not-Published"),
)


class Course(CreatedModifiedModel, OrderedModel):

    specialty = models.ForeignKey('courses.Specialty', null=False, blank=False)
    authors = models.ManyToManyField('drf_users.User')
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    image = models.FileField(null=True, blank=True, upload_to='specialty_images/')
    icon = models.FileField(null=True, blank=True, upload_to='specialty__icon_images/')
    state = models.CharField(choices=COURSE_STATE_CHOICES, default='PUB', max_length=3, null=False, blank=False)
    deleted = models.BooleanField(default=False)
    color = models.CharField(null=False, blank=False, default='#014386', max_length=50)

    order_with_respect_to = 'specialty'

    def __str__(self):
        return u"%s Course" % self.title

    def get_course_sections(self):
        return CourseSection.objects.filter(course=self).order_by('order')

    def get_first_course_sections(self):
        object = None
        queryset = CourseSection.objects.filter(course=self).order_by('order')
        if len(queryset) > 0:
            object = queryset[0]

        return object

class CourseSectionType(CreatedModifiedModel, OrderedModel):
    title = models.CharField(max_length=255, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)


    def __str__(self):
        return u"%s Course Section Type" % self.title

class CourseSection(CreatedModifiedModel, OrderedModel):
    course = models.ForeignKey('courses.Course', null=False, blank=False)
    course_section_type = models.ForeignKey('courses.CourseSectionType', null=False, blank=False)
    title = models.CharField(max_length=255, null=False, blank=False)
    course_document = JSONField(null=False, blank=True, default=dict)
    deleted = models.BooleanField(default=False)


    order_with_respect_to = 'course'


    def __str__(self):
        return u"%s Course Section" % self.title

    def getSupportingFiles(self):
        return Attachment.objects.get_attachments_for_object(self)


class CourseProgressManager(models.Manager):
    def get_for_user_and_course(self, user_id, course_id):
        query = self.filter(user_id=user_id, course_id=course_id)
        if len(query) > 0:
            object = query[0]
        else:
            course = Course.objects.filter(id=course_id)
            if len(course) > 0:
                course = course[0]
            else:
                raise Exception('Course does not exist')

            object = self.create(
                user_id=user_id,
                course_id=course_id,
                modified_by_id=user_id,
                created_by_id=user_id,
                course_section_id=course.get_first_course_sections().id,
            )

        return object




class CourseProgress(CreatedModifiedModel):
    objects = CourseProgressManager()

    object = JSONField(null=False, blank=True, default=dict)
    course = models.ForeignKey('courses.Course', null=False, blank=False)
    course_section = models.ForeignKey('courses.CourseSection', null=False, blank=False)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey('drf_users.User', null=False, blank=False)

