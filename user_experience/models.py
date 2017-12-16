from django.db import models

from twz_server_django.model_mixins import CreatedModifiedModel
from institutions.models import Institution, InstitutionType
from ordered_model.models import OrderedModel

class UserProfileExperienceType(CreatedModifiedModel):
    title = models.CharField(max_length=255, blank=False, null=False)
    is_active = models.BooleanField(default=True, null=False)
    institution_search_type = models.ForeignKey('institutions.InstitutionType', blank=True, null=True)

    def __str__(self):
        return "%s" % self.title

# class DegreeType(CreatedModifiedModel, OrderedModel):
#     title = models.CharField(max_length=255, blank=False, null=False)
#     is_active = models.BooleanField(default=True, null=False)
#
#     def __str__(self):
#         return "%s" % self.title

# class Degree(CreatedModifiedModel):
#     title = models.CharField(max_length=255, blank=False, null=False)
#     degree_type = models.ForeignKey(DegreeType)
#     is_active = models.BooleanField(default=True, null=False)
#
#     def __str__(self):
#         return "%s" % self.title
#


class UserProfileExperienceManager(models.Manager):

    def getExperienceForUserId(self, user_id):
        return self.filter(user_profile__user_id=user_id).order_by('-type__title', '-date_to', '-date_from')

    def getExperienceForUserProfile(self, profile):
        return self.filter(user_profile=profile).order_by('-type__title', '-date_to', '-date_from')


class UserProfileExperience(CreatedModifiedModel):

    objects = UserProfileExperienceManager()

    user = models.ForeignKey('drf_users.User')
    institution = models.ForeignKey(Institution)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    type = models.ForeignKey(UserProfileExperienceType)
    job_title = models.CharField(null=True, blank=True, max_length=255)
    degree = models.CharField(null=True, blank=True, max_length=255)
    is_deleted = models.BooleanField(default=False, null=False)

    def __str__(self):
        return "%s - %s" % (self.user, self.institution.title, )

