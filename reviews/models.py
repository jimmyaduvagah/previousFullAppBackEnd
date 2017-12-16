from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django.contrib.postgres.fields.jsonb import JSONField
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from ordered_model.models import OrderedModel

from courses.models import Course
from twz_server_django.model_mixins import CreatedModifiedModel, CreatedModifiedModelManager


class ReviewManager(CreatedModifiedModelManager):

    def get_queryset(self, *args, **kwargs):
        qs = super(ReviewManager, self).get_queryset()
        qs.order_by('-created_on')
        return qs


class Review(CreatedModifiedModel):

    objects = ReviewManager()

    template = models.ForeignKey('reviews.ReviewTemplate', null=False, blank=False)
    response = JSONField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType, null=False, blank=False, related_name="review_content_type")
    object_id = models.UUIDField(null=False, blank=False)
    related = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "%s Review By %s on %s" % (self.content_type, self.created_by, self.created_on)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, request=None):
        response = super(Review, self).save(force_insert, force_update, using, update_fields, request)
        # if course type
        if self.content_type.model_class() is Course:
            reviews = Review.objects.filter(object_id=self.object_id, content_type=self.content_type)
            total = 0
            for r in reviews:
                for answer in r.response:
                    if answer['type'] == '5stars':
                        total += answer['response']
                        break

            average = total / len(reviews)
            self.related.rating = average
            self.related.save()

        return response


REVIEW_STATE_CHOICES = (
    ("ACT", "Active"),
    ("NAC", "Not-Active"),
)


class ReviewTemplateManager(CreatedModifiedModelManager):

    def get_queryset(self, *args, **kwargs):
        qs = super(ReviewTemplateManager, self).get_queryset()
        qs.order_by('-created_on')
        return qs


class ReviewTemplate(CreatedModifiedModel):
    objects = ReviewTemplateManager()

    questions = JSONField(blank=False, null=False)
    content_type = models.ForeignKey(ContentType, null=False, blank=False, related_name="review_template_content_type")
    state = models.CharField(choices=REVIEW_STATE_CHOICES, default='ACT', max_length=3, null=False, blank=False)

    def __str__(self):
        return "Review Questions for %s" % self.content_type