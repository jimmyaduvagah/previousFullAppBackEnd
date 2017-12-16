import json

from datetime import date

import datetime

import vimeo
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

# Create your models here.
from django.db.models.deletion import SET_NULL
from django.db.models.signals import post_save, m2m_changed
from django.dispatch.dispatcher import receiver
from ordered_model.models import OrderedModel
from storages.backends.s3boto import S3BotoStorage

from twz_server_django.model_mixins import CreatedModifiedModel, CreatedModifiedModelManager
from twz_server_django.settings import AWS_STORAGE_BUCKET_NAME, AWS_DEFAULT_ACL
from twz_server_django.settings_private import VIMEO_ACCESS_TOKEN, VIMEO_CLIENT_KEY, VIMEO_CLIENT_SECRET


class CategoryManager(CreatedModifiedModelManager):

    def get_queryset(self, *args, **kwargs):
        qs = super(CategoryManager, self).get_queryset()
        return qs

    def get_active(self, *args, **kwargs):
        qs = super(CategoryManager, self).get_queryset()
        qs.filter(deleted=False, is_active=True)
        return qs


class Category(CreatedModifiedModel):

    objects = CategoryManager()

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Categories"

    title = models.CharField(max_length=255, null=False, blank=False, unique=True)
    description = models.TextField(null=False, blank=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    color = models.CharField(null=False, blank=False, default='#014386', max_length=50)

    def __str__(self):
        return u"%s Specialty" % self.title


class CourseManager(CreatedModifiedModelManager):

    def get_queryset(self, *args, **kwargs):
        qs = super(CourseManager, self).get_queryset()
        return qs

    def get_active(self, *args, **kwargs):
        qs = super(CourseManager, self).get_queryset()
        qs = qs.filter(deleted=False, state='PUB')

        return qs

    def get_with_is_started_queryset(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        qs = self.get_active()
        qs = qs.extra(
            select={
                'is_started':   "SELECT id "
                                "FROM courses_courseprogress "
                                "WHERE "
                                "courses_courseprogress.course_id = courses_course.id AND "
                                "courses_courseprogress.created_by_id = %s",
                'is_completed': "SELECT id "
                                "FROM courses_courseprogress "
                                "WHERE "
                                "courses_courseprogress.completed = TRUE AND "
                                "courses_courseprogress.course_id = courses_course.id AND "
                                "courses_courseprogress.created_by_id = %s"
            },
            select_params=[(user_id, ),(user_id, )]
        )

        return qs


COURSE_STATE_CHOICES = (
    ("PUB", "Published"),
    ("NOP", "Not-Published"),
)


class Course(CreatedModifiedModel, OrderedModel):

    objects = CourseManager()

    category = models.ForeignKey('courses.Category', null=False, blank=False)
    authors = models.ManyToManyField('drf_users.User')
    authors_json = JSONField(default=[], null=True, blank=True)
    tags = models.ManyToManyField('tags.Tag', blank=True)
    tags_json = JSONField(default=[], null=True, blank=True)
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    image = models.ForeignKey('images.Image', null=True, blank=True, on_delete=SET_NULL)
    watches = models.PositiveIntegerField(null=False, blank=True, default=0)
    vimeo_id = models.CharField(max_length=255, null=False, blank=True, default='')
    state = models.CharField(choices=COURSE_STATE_CHOICES, default='PUB', max_length=3, null=False, blank=False)
    deleted = models.BooleanField(default=False)
    color = models.CharField(null=False, blank=False, default='#014386', max_length=50)
    rating = models.DecimalField(null=False, blank=True, default=5, max_digits=3, decimal_places=2)

    order_with_respect_to = 'category'

    def __str__(self):
        return u"%s Course" % self.title

    def get_video(self):
        data = None

        if self.vimeo_id:
            v = vimeo.VimeoClient(
                token=VIMEO_ACCESS_TOKEN,
                key=VIMEO_CLIENT_KEY,
                secret=VIMEO_CLIENT_SECRET)

            try:
                response = v.get("/videos/%s" % (self.vimeo_id,), params={})
                data = response.json()
            except Exception:
                pass

        return data

    def save(self, *args, **kwargs):
        to_return = super(Course, self).save(*args, **kwargs)
        obj = Course.objects.get(id=self.id)
        return to_return


def update_authors_json(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add' or kwargs['action'] == 'post_remove':
        authors = []
        author_list = instance.authors.all()
        for author in author_list:
            authors.append({
                "id": str(author.id),
                "name": author.get_full_name()
            })

        instance.authors_json = authors
        instance.save()


m2m_changed.connect(update_authors_json, sender=Course.authors.through)


def update_tags_json(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add' or kwargs['action'] == 'post_remove':
        tags = []
        tag_list = instance.tags.all()
        for tag in tag_list:
            tags.append({
                "id": str(tag.id),
                "title": tag.title
            })

        instance.tags_json = tags
        instance.save()


m2m_changed.connect(update_tags_json, sender=Course.tags.through)


class CourseModuleManager(CreatedModifiedModelManager):

    def get_queryset(self, *args, **kwargs):
        qs = super(CourseModuleManager, self).get_queryset().order_by('course', 'order')
        return qs

    def get_active(self, *args, **kwargs):
        qs = super(CourseModuleManager, self).get_queryset().filter(deleted=False, state='PUB').order_by('course', 'order')
        return qs


class CourseModule(CreatedModifiedModel, OrderedModel):

    objects = CourseModuleManager()

    title = models.CharField(max_length=255, null=False, blank=False)
    course = models.ForeignKey('courses.Course', null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    image = models.ForeignKey('images.Image', null=True, blank=True, on_delete=SET_NULL)
    state = models.CharField(choices=COURSE_STATE_CHOICES, default='PUB', max_length=3, null=False, blank=False)
    deleted = models.BooleanField(default=False)

    order_with_respect_to = 'course'

    def __str__(self):
        return u"%s Course Module" % self.title


class CourseProgress(CreatedModifiedModel):

    object = JSONField(null=False, blank=True, default=dict)
    course = models.ForeignKey('courses.Course', null=False, blank=False)
    current_course_module = models.ForeignKey('courses.CourseModule', null=True, blank=True)
    current_course_module_section = models.ForeignKey('course_module_sections.CourseModuleSection', null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_on = models.DateTimeField(blank=True, null=True, default=None)
    ended = models.BooleanField(default=False)
    ended_on = models.DateTimeField(blank=True, null=True, default=None)
    last_opened = models.DateTimeField(blank=False, null=False, default=datetime.datetime.now)
    total_time_viewing = models.IntegerField(blank=True, null=True, default=None)

