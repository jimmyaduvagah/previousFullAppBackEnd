from django.contrib import admin

from learning_experience_submissions.models import LESubmission, LESubmissionRating


class LESubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'created_by',
        'created_on',
        'modified_on',
        'number_of_ratings',
        'average_rating',
        'submitted',
        'submitted_on',
        'approved',
        'approved_on',
        'deleted'
    )
    list_filter = (
        ('created_by', admin.RelatedOnlyFieldListFilter),
        ('approved', admin.BooleanFieldListFilter),
        ('deleted', admin.BooleanFieldListFilter),
    )


admin.site.register(LESubmission, LESubmissionAdmin)


class LESubmissionRatingAdmin(admin.ModelAdmin):
    list_display = (
        'le_submission',
        'average_rating',
        'created_by',
        'created_on'
    )
    list_filter = (
        ('created_by', admin.RelatedOnlyFieldListFilter),
        ('le_submission', admin.BooleanFieldListFilter),
    )


admin.site.register(LESubmissionRating, LESubmissionRatingAdmin)