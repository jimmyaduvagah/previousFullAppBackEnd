import datetime

import time

import hashlib
import uuid

import markdown
from django.core.exceptions import FieldError
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import urlencode
from rest_framework.authtoken.models import Token
from django.utils import timezone
from storages.backends.s3boto import S3BotoStorage
from django_boto.s3.storage import S3Storage

from ionic_api.request import PushTokenRequest
from twz_server_django.settings import AWS_PUBLIC_STORAGE_BUCKET_NAME, AWS_PUBLIC_ACL, DEFAULT_CONTACT_FROM_EMAIL, \
    get_app_base_url, get_api_base_url, SERVER_PROTOCOL, SERVER_NAME, SERVER_PORT
from twz_server_django.model_mixins import CreatedModifiedModel
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from user_experience.models import UserProfileExperience

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

GENDER_CHOICES = (
    ('MA', 'Male'),
    ('FM', 'Female')
)


def profile_file_name(instance, filename):
    return 'profile_images/%s-%s' % (time.time(), filename)


class User(AbstractUser, CreatedModifiedModel):
    __bio = None

    def save(self, *args, **kwargs):
        if 'update_fields' in kwargs:
            if 'bio' in kwargs['update_fields']:
                self.update_bio_html()

        return super(User, self).save(*args, **kwargs)

    # main verification, when one or the other is done, mark this done for simple queries
    is_verified = models.BooleanField(default=False)
    completed_initial_setup = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=255, null=True, blank=True)

    # email verification
    verified_email = models.BooleanField(default=False)
    email_verification_code = models.CharField(default=None, max_length=32, null=True, blank=True)

    # phone and verification
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    phone_country_dial_code = models.CharField(max_length=6, null=True, blank=True)
    phone_country_code = models.CharField(max_length=6, null=True, blank=True)

    verified_phone = models.BooleanField(default=False)
    phone_number_verification_code = models.CharField(default=None, max_length=6, null=True, blank=True)

    # invitation code if used on sign up
    invitation_code_used_to_join = models.CharField(max_length=32, null=True, blank=True)

    # profile and banner images
    profile_image = models.ImageField(null=True, blank=True, upload_to=profile_file_name,
                                      storage=S3BotoStorage(bucket=AWS_PUBLIC_STORAGE_BUCKET_NAME, acl=AWS_PUBLIC_ACL))
    banner_image = models.ImageField(null=True, blank=True, upload_to='banner_images/',
                                      storage=S3BotoStorage(bucket=AWS_PUBLIC_STORAGE_BUCKET_NAME, acl=AWS_PUBLIC_ACL))
    # TODO: need a good way to make 'retnia' and normal versions.

    # other PII
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(null=True, blank=True, choices=GENDER_CHOICES, max_length=2)
    nationality = models.ForeignKey('nationalities.Nationality', blank=True, null=True)
    town_of_residence = models.ForeignKey('towns.Town', blank=True, null=True, related_name="user_town_of_residence")
    place_of_birth = models.ForeignKey('towns.Town', blank=True, null=True, related_name="user_place_of_birth")

    bio = models.TextField(blank=True, default=None, null=True)
    bio_html = models.TextField(blank=True, default=None, null=True)


    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.get_full_name()

    def get_profile_image_cache_url(self):
        if self.profile_image:
            return '%s%s:%s/api/v1/images/cache/?url=%s' % (
                SERVER_PROTOCOL, SERVER_NAME, SERVER_PORT, urlencode(self.getPublicProfileImageUrl())
                )
        else:
            return None

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def get_private_name(self):
        """
        Returns first_name and first letter of last_name for privacy.
        """
        return '%s %s.' % (self.first_name, self.last_name[0])

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    # def get_courses_completed(self):
    #     return CourseProgress.objects.filter(user=self, completed=True)
    #
    # def get_courses_started(self):
    #     return CourseProgress.objects.filter(user=self, completed=False)

    def getPublicProfileImageUrl(self):
        """
        This seems to be needed for a serializer right now... need to look into if really needed.
        :return:
        """
        if self.profile_image:
            url = "https://%s.%s/%s" % (AWS_PUBLIC_STORAGE_BUCKET_NAME , 's3.amazonaws.com',  self.profile_image)
            return url
        else:
            return None


    def add_verification_code(self):
        # TODO: Change this to add_email_verification and create a add_phone_vericaiton method.
        self.email_verification_code = User.make_verification_code(self.username, self.email)
        self.save()
        return self

    def verify_user(self):
        # TODO: Change this to verify_email and create a verify_phone method.
        self.email_verification_code = None
        self.verified_email = True
        self.is_verified = True
        self.active = True
        self.save()
        return self

    @staticmethod
    def make_verification_code(username, email):
        hash = hashlib.md5()
        hash.update(("%s-%s-%s" % (username, email, timezone.now())).encode('utf-8'))
        return hash.hexdigest()

    def send_verification_email(self):
        if self.email:
            message = "Please verify your account by clicking the link provided below: \n %s/api/v1/auth-register/?r=True&vc=%s" % (get_api_base_url(), self.verification_code)

            self.email_user("Tunaweza Account Verification", message, DEFAULT_CONTACT_FROM_EMAIL)
        else:
            raise FieldError('no email address')

    def update_bio_html(self):
        self.bio_html = markdown.markdown(self.bio)
        return self


class InvitationCodeManager(models.Manager):

    def checkCode(self, code):
        invitation_code = self.filter(code__iexact=code)

        if invitation_code:
            invitation_code = invitation_code[0]
            if invitation_code.uses < invitation_code.max_uses:
                if invitation_code.active_till != None:
                    if timezone.now() < invitation_code.active_till:
                        return invitation_code
                    else:
                        return False
                else:
                    return invitation_code
            else:
                return False
        else:
            return False


class InvitationCode(CreatedModifiedModel):

    objects = InvitationCodeManager()

    code = models.CharField(max_length=255, null=False, blank=True)
    uses = models.IntegerField(null=False, blank=True, default=0)
    max_uses = models.IntegerField(null=False, blank=True, default=0)
    active_till = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return u"%s" % self.code

    def incrementUsed(self):
        self.uses += 1
        self.save()


class PhoneVerificationCode(CreatedModifiedModel):

    code = models.CharField(max_length=6, null=False, blank=False)
    user = models.ForeignKey('drf_users.User', null=False, blank=False)
    is_used = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return u"%s for %s" % (self.code, self.user)


class PushToken(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=255, null=False, blank=False)
    user = models.ForeignKey('drf_users.User', null=False, blank=False)
    created_on = models.DateTimeField(auto_created=True)
    modified_on = models.DateTimeField(auto_now=True, editable=True)
    is_active = models.BooleanField(default=True)
    push_group = models.CharField(max_length=10, null=False, blank=False, default="tw_prod")
    app_version = models.CharField(max_length=10, null=True, blank=True)
    device_id = models.CharField(max_length=255, null=False, blank=False)
    device_manufacturer = models.CharField(max_length=255, null=False, blank=True, default="")
    device_model = models.CharField(max_length=255, null=False, blank=True, default="")
    device_version = models.CharField(max_length=255, null=False, blank=True, default="")
    device_platform = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return u"%s for %s" % (self.token, self.user)

    def delete(self, using=None, keep_parents=False):
        r = PushTokenRequest()
        r.delete(self.token)
        return super(PushToken, self).delete(using, keep_parents)

    def invalidate(self, using=None, keep_parents=False):
        self.is_active = False
        self.save()
        r = PushTokenRequest()
        r.patch(self.token, {
            "valid": False
        })
        return r

    def make_valid(self, using=None, keep_parents=False):
        self.is_active = True
        self.save()
        r = PushTokenRequest()
        r.patch(self.token, {
            "valid": True
        })
        return r