from django.contrib import admin
from .models import InstitutionType, Institution

class InstitutionAdmin(admin.ModelAdmin):
    ordering = ('type', 'title')
    list_display = ('title', 'type',)
    list_filter = ('type',)
    search_fields = ('title',)


admin.site.register(Institution, InstitutionAdmin)
admin.site.register(InstitutionType)