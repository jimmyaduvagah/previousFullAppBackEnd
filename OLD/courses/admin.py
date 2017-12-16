from django.contrib import admin
from django import forms

from .models import Specialty, Course, CourseSection, CourseSectionType, CourseProgress
from ordered_model.admin import OrderedModelAdmin

# Register your models here.
# which acts a bit like a singleton

admin.site.register(Specialty)

class CourseAdmin(OrderedModelAdmin):
    list_display = ('title', 'specialty', 'move_up_down_links')
    list_filter = (
        ('specialty', admin.RelatedOnlyFieldListFilter),
    )

admin.site.register(Course, CourseAdmin)

class CourseSectionModelForm( forms.ModelForm ):
    class Meta:
        model = CourseSection
        widgets = {
            'course_document': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }

        exclude = ()

class CourseSection_Admin( OrderedModelAdmin ):
    form = CourseSectionModelForm
    list_display = ('title', 'course', 'move_up_down_links', 'order', 'course_section_type')
    list_filter = (
        ('course', admin.RelatedOnlyFieldListFilter),
    )
    ordering = ('order',)
admin.site.register(CourseSection, CourseSection_Admin)

class CourseSectionTypeAdmin(OrderedModelAdmin):
    list_display = ('title', 'move_up_down_links')

admin.site.register(CourseSectionType, CourseSectionTypeAdmin)


class CourseProgressTypeAdmin(OrderedModelAdmin):
    list_display = ('course', 'course_section', 'user')

admin.site.register(CourseProgress, CourseProgressTypeAdmin)


