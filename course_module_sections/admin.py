from django.contrib import admin

# Register your models here.
from ordered_model.admin import OrderedModelAdmin

from course_module_sections.models import CourseModuleSection, SectionVideoContainer, SectionAssessment, SectionImage, \
    SectionAttachment, SectionText, SectionQuiz, SectionGallery, SectionSurveyGroup


class CourseModuleSectionAdmin(OrderedModelAdmin):
    list_display = ('object_id', 'course_module', 'content_type', 'order', 'move_up_down_links')
    list_filter = (
        ('course_module', admin.RelatedOnlyFieldListFilter),
        ('content_type', admin.RelatedOnlyFieldListFilter),
    )


admin.site.register(CourseModuleSection, CourseModuleSectionAdmin)

admin.site.register(SectionSurveyGroup)
admin.site.register(SectionVideoContainer)
admin.site.register(SectionText)
admin.site.register(SectionAttachment)
admin.site.register(SectionImage)
admin.site.register(SectionAssessment)
admin.site.register(SectionQuiz)
admin.site.register(SectionGallery)
