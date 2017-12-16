from django.contrib import admin

# Register your models here.
from ordered_model.admin import OrderedModelAdmin

from module.models import ModuleCategory, Module, UserAssessment


class MediaCategoryAdmin(OrderedModelAdmin):
    list_display = ('title', 'order', 'move_up_down_links')

admin.site.register(ModuleCategory, MediaCategoryAdmin)


class ModuleAdmin(OrderedModelAdmin):
    list_display = ('title', 'category', 'order', 'move_up_down_links')
    list_filter = (
        ('category', admin.RelatedOnlyFieldListFilter),
    )

admin.site.register(Module, ModuleAdmin)



class UserAssessmentAdmin(OrderedModelAdmin):
    list_display = ('title',)

admin.site.register(UserAssessment, UserAssessmentAdmin)

