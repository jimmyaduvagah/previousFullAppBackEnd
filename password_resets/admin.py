from django.contrib import admin
from django import forms

from .models import PasswordResetToken

# Register your models here.
# which acts a bit like a singleton

class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'id', 'valid', 'used', 'used_on', 'requested_on')
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter),
    )

admin.site.register(PasswordResetToken, PasswordResetTokenAdmin)


