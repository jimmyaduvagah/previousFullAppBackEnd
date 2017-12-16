from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

# Create your models here.
from twz_server_django.model_mixins import CreatedModifiedModel


class Assessment(CreatedModifiedModel):
    class Meta:
        ordering = ['-created_on']


    user_assessed = models.ForeignKey('drf_users.User', null=False, related_name='assessment_user_assessed')
    user_who_assessed = models.ForeignKey('drf_users.User', null=False, related_name='assessment_user_who_assessed')
    course = models.ForeignKey('courses.Course', null=False)
    course_section = models.ForeignKey('courses.CourseSection', null=False)
    course_progress = models.ForeignKey('courses.CourseProgress', null=False)
    rating = models.PositiveSmallIntegerField(null=False, blank=False)
    comment = models.TextField(blank=False, null=False)

