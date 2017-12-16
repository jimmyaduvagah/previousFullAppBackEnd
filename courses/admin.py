from django.contrib import admin

# Register your models here.
from ordered_model.admin import OrderedModelAdmin

from courses.models import Course, Category, CourseModule, CourseProgress


class CourseAdmin(OrderedModelAdmin):
    list_display = ('title', 'order', 'rating', 'move_up_down_links')
    list_filter = (
        ('category', admin.RelatedOnlyFieldListFilter),
    )


class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'completed', 'ended', 'course', 'current_course_module', 'created_on',
                    'completed_on', 'ended_on')
    list_filter = (
        ('course', admin.RelatedOnlyFieldListFilter),
        ('completed', admin.BooleanFieldListFilter),
        ('ended', admin.BooleanFieldListFilter),
        ('created_by', admin.RelatedFieldListFilter),
    )

admin.site.register(Course, CourseAdmin)
admin.site.register(Category)
admin.site.register(CourseProgress, CourseProgressAdmin)
admin.site.register(CourseModule)
