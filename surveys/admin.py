from django.contrib import admin

from surveys.models import Survey, SurveyResponse


class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_on')
    list_filter = (
        ('created_by', admin.RelatedFieldListFilter),
    )


class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_on')
    list_filter = (
        ('user', admin.RelatedFieldListFilter),
        ('survey', admin.RelatedFieldListFilter),
    )

admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyResponse, SurveyResponseAdmin)
