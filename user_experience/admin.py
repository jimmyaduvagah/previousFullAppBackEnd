from django.contrib import admin
from .models import UserProfileExperience, UserProfileExperienceType

admin.site.register(UserProfileExperienceType)
admin.site.register(UserProfileExperience)