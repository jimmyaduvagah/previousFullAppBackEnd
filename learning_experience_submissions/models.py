import math


import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

# Create your models here.
from django.db.models.deletion import SET_NULL
from ordered_model.models import OrderedModel

from course_module_sections.models import make_markdown
from twz_server_django.model_mixins import CreatedModifiedModel, CreatedModifiedModelManager


LESubmissionRatingMetrics = {
    'Immersiveness': 1,
    'Style': 1,
    'Conciseness & Structure': 1,
    'Accessibility': 1,
    'Technical Overview': 1,
    'Visuals': 1,
}


class LESubmissionManager(CreatedModifiedModelManager):

    def get_queryset(self, *args, **kwargs):
        qs = super(LESubmissionManager, self).get_queryset().filter().order_by('-created_on', )
        return qs

    def get_active(self, *args, **kwargs):
        qs = super(LESubmissionManager, self).get_queryset().filter(deleted=False).order_by('-created_on', )
        return qs

    def get_with_have_rated(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        qs = self.get_active()
        qs = qs.extra(
            select={
                'have_i_rated': "SELECT id "
                                "FROM learning_experience_submissions_lesubmissionrating "
                                "WHERE "
                                "learning_experience_submissions_lesubmissionrating.le_submission_id = learning_experience_submissions_lesubmission.id AND "
                                "learning_experience_submissions_lesubmissionrating.created_by_id = %s"
            },
            select_params=[(user_id, )]
        )

        return qs


class LESubmission(CreatedModifiedModel):
    objects = LESubmissionManager()

    title = models.CharField(max_length=255, null=False, blank=False)
    version = models.IntegerField(null=False, blank=False, default=1)
    versions = JSONField(blank=True, null=False, default=[])
    description = models.TextField(null=False, blank=True, help_text='This is a short description of the LE.')
    markdown = models.TextField(null=False, blank=True, help_text='The plain text markdown.')
    html = models.TextField(null=False, blank=True, help_text='The html.')
    image = models.ForeignKey('images.Image', null=True, blank=True, on_delete=SET_NULL)
    number_of_ratings = models.IntegerField(blank=True, null=True, default=0)
    average_rating = models.IntegerField(blank=True, null=True, default=None)
    average_ratings = JSONField(blank=True, null=False, default={})
    approved = models.BooleanField(default=False)
    approved_on = models.DateTimeField(blank=True, null=True, default=None)
    submitted = models.BooleanField(default=False)
    submitted_on = models.DateTimeField(blank=True, null=True, default=None)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(blank=True, null=True, default=None)

    def __str__(self):
        return u"%s LE Submission v%s" % (self.title, self.version)

    def mark_as_deleted(self, *args, **kwargs):
        self.deleted = True
        self.deleted_on = datetime.datetime.now()
        self.save()
        return self

    def un_delete(self, *args, **kwargs):
        self.deleted = False
        self.deleted_on = None
        self.save()
        return self

    def approve(self, *args, **kwargs):
        self.approved = True
        self.approved_on = datetime.datetime.now()
        self.save()
        return self

    def un_approve(self, *args, **kwargs):
        self.approved = False
        self.approved_on = None
        self.save()
        return self

    def submit(self, *args, **kwargs):
        self.submitted = True
        self.submitted_on = datetime.datetime.now()
        self.save()
        return self

    def un_submit(self, *args, **kwargs):
        self.submitted = False
        self.submitted_on = None
        self.save()
        return self

    def reset_for_new_version(self, *args, **kwargs):
        self.number_of_ratings = 0
        self.average_rating = None
        self.average_ratings = {}
        self.approved = False
        self.approved_on = None
        self.submitted = False
        self.submitted_on = None
        self.deleted = False
        self.deleted_on = None

    def update_rating(self):
        ratings = self.get_ratings()
        self.number_of_ratings = len(ratings)
        if self.number_of_ratings > 0:

            total_rating = 0
            average_ratings = {}
            # build the list of ratings from each rating
            for rating in ratings:
                for rating_field in rating.ratings:
                    if rating_field not in average_ratings:
                        average_ratings[rating_field] = rating.ratings[rating_field]
                    else:
                        average_ratings[rating_field] += rating.ratings[rating_field]

            # average the list of ratings based on the number of ratings that exist
            for rating in average_ratings:
                average_ratings[rating] = le_rating_float_to_int(average_ratings[rating] / self.number_of_ratings)
                total_rating += average_ratings[rating]

            total_rating = le_rating_float_to_int(total_rating / len(average_ratings))
            self.average_rating = total_rating
            self.average_ratings = average_ratings
        else:
            self.average_rating = None
            self.average_ratings = {}

        self.save()

    def make_new_version(self):
        from learning_experience_submissions.serializers import LESubmissionNewVersionSerializer

        serialized_data = LESubmissionNewVersionSerializer(self).data
        self.versions.append(serialized_data)
        self.version += 1
        self.reset_for_new_version()
        self.save()
        self.delete_ratings()

        return self

    def get_ratings(self):
        return LESubmissionRating.objects.get_ratings_for_le_submission(self.id)

    def delete_ratings(self):
        ratings = self.get_ratings()
        for rating in ratings:
            rating.delete()

    def check_for_approval(self):
        return LESubmissionRating.objects.check_le_submission_for_approval(self.id)

    def save(self, *args, **kwargs):
        self.html = make_markdown(self.markdown)
        super(LESubmission, self).save(*args, **kwargs)


class LESubmissionRatingManager(CreatedModifiedModelManager):
    def get_queryset(self, *args, **kwargs):
        qs = super(LESubmissionRatingManager, self).get_queryset().order_by('-created_on', )
        return qs

    def get_ratings_for_le_submission(self, le_submission_id):
        qs = super(LESubmissionRatingManager, self)\
            .get_queryset().filter(le_submission__id=le_submission_id)\
            .order_by('created_on', )
        return qs

    def check_le_submission_for_approval(self, le_submission_id):
        qs = super(LESubmissionRatingManager, self)\
            .get_queryset().filter(le_submission__id=le_submission_id, approved=True)\
            .order_by('created_on', )
        count = len(qs)
        # if 3 or more approvals then return True
        return count >= 3


class LESubmissionRating(CreatedModifiedModel):
    objects = LESubmissionRatingManager()

    le_submission = models.ForeignKey('learning_experience_submissions.LESubmission', null=False, blank=True)
    comments = models.TextField(null=False, blank=True, help_text='The reviewer\'s comments.')
    approved = models.BooleanField(default=False)
    ratings = JSONField(blank=False, null=False, default=LESubmissionRatingMetrics)
    average_rating = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return u"%s LE Submission v%s Rating" % (self.le_submission.title, self.le_submission.version)

    def save(self, *args, **kwargs):
        self.update_average_rating()
        obj = super(LESubmissionRating, self).save(*args, **kwargs)
        self.le_submission.update_rating()
        # if the LE submission was approved then mark it as approved.
        if self.le_submission.check_for_approval():
            self.le_submission.approve()

        return obj

    def delete(self, *args, **kwargs):
        le_submission = self.le_submission
        obj = super(LESubmissionRating, self).delete(*args, **kwargs)
        le_submission.update_rating()
        return obj

    def update_average_rating(self):
        total = 0
        for rating_field in self.ratings:
            total += self.ratings[rating_field]

        self.average_rating = le_rating_float_to_int(total / len(self.ratings))


def le_rating_float_to_int(the_float):
    fraction, integer = math.modf(the_float)
    if fraction > .7:
        return math.ceil(the_float)
    else:
        return math.floor(the_float)
