from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext, ugettext_lazy as _

import requests

from drf_users.models import PhoneVerificationCode, PushToken
from .models import User, InvitationCode
from twz_server_django.settings import SERVER_NAME, SERVER_PROTOCOL

# Register your models here.
# which acts a bit like a singleton
# Define a new User admin
class UserAdminWithProfile(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'password', 'last_login', 'date_joined', 'verified_email', 'email_verification_code')
    actions = ['reset_password']

    def get_fieldsets(self, request, obj=None):
        fs = super(UserAdminWithProfile, self).get_fieldsets(request, obj)
        # fs now contains [(None, {'fields': fields})], do with it whatever you want
        fs = fs + ((_('Info'), {'fields': (
            'completed_initial_setup',
            'verified_email',
            'email_verification_code',
            'is_verified',
            'phone_number',
            'phone_country_dial_code',
            'phone_country_code',
            'verified_phone',
            'phone_number_verification_code',
            'invitation_code_used_to_join',
            'profile_image',
            'banner_image',
            'date_of_birth',
            'gender',
            'nationality',
            'town_of_residence',
            'place_of_birth',
            'bio',
            'bio_html'
        )}),)

        return fs

    def reset_password(self, request, queryset):
        reset_password_url = '%s://%s/api/v1/rest-auth/password/reset/' % (SERVER_PROTOCOL, SERVER_NAME)
        rows_updated = 0
        for user in queryset:
            requests.post(reset_password_url, {'email':user.email})
            rows_updated += 1

        if rows_updated == 1:
            message_bit = "1 user had its"
        else:
            message_bit = "%s users had their" % rows_updated
        self.message_user(request, "%s password reset" % message_bit)


class PhoneVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'is_used', 'is_active', 'created_on', 'created_by')
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter),
        ('is_used', admin.BooleanFieldListFilter),
        ('is_active', admin.BooleanFieldListFilter),
    )


class PushTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'is_active', 'app_version', 'device_id', 'push_group', 'created_on', 'modified_on')
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter),
        ('device_manufacturer', admin.AllValuesFieldListFilter),
        ('push_group', admin.AllValuesFieldListFilter),
        ('is_active', admin.BooleanFieldListFilter),
    )



# Re-register UserAdmin
admin.site.register(PushToken, PushTokenAdmin)
admin.site.register(User, UserAdminWithProfile)
admin.site.register(InvitationCode)
admin.site.register(PhoneVerificationCode, PhoneVerificationCodeAdmin)
