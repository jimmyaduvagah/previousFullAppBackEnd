from django.contrib import admin

# Register your models here.
from django.contrib.admin.options import ModelAdmin
from reviews.models import Review, ReviewTemplate


class ReviewAdmin(ModelAdmin):
    list_display = ('content_type', 'created_by', 'created_on')
    list_filter = (
        ('content_type', admin.RelatedOnlyFieldListFilter),
        ('template', admin.RelatedOnlyFieldListFilter),
    )


admin.site.register(Review, ReviewAdmin)


class ReviewTemplateAdmin(ModelAdmin):
    list_display = ('content_type', 'state',)
    list_filter = (
        ('content_type', admin.ChoicesFieldListFilter),
        ('state', admin.ChoicesFieldListFilter),
    )

admin.site.register(ReviewTemplate, ReviewTemplateAdmin)
