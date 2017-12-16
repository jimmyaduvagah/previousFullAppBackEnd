from django.contrib import admin

# Register your models here.
from module_progress.models import ModuleProgress


class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'completed', 'assessment_submitted', 'assessment_response_completed')
    list_filter = (
        ('module', admin.RelatedOnlyFieldListFilter),
        ('completed', admin.BooleanFieldListFilter),
        ('assessment_submitted', admin.BooleanFieldListFilter),
        ('assessment_response_completed', admin.BooleanFieldListFilter),
        ('user', admin.RelatedOnlyFieldListFilter),
    )

admin.site.register(ModuleProgress, ModuleProgressAdmin)
