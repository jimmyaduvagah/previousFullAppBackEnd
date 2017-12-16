from django.contrib import admin
from django import forms

from media.models import Media
from ordered_model.admin import OrderedModelAdmin, OrderedTabularInline



class MediaAdmin(OrderedModelAdmin):
    list_display = ('title', 'module', 'order', 'move_up_down_links',)

    list_filter = (
        ('module', admin.RelatedOnlyFieldListFilter),
    )

admin.site.register(Media, MediaAdmin)

