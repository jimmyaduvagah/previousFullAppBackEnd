from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from ordered_model.admin import OrderedModelAdmin

from images.models import GalleryImage, Gallery
from .models import Image

# Register your models here.


class ImageAdmin(ModelAdmin):
    list_display = ('id', 'image', 'width', 'height', 'created_on', 'created_by')


class GalleryAdmin(ModelAdmin):
    list_display = ('title', 'created_on', 'created_by')


class GalleryImageAdmin(OrderedModelAdmin):
    list_display = ('gallery', 'image', 'order', 'move_up_down_links')
    list_filter = (
        ('gallery', admin.RelatedOnlyFieldListFilter),
    )

admin.site.register(Image, ImageAdmin)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(GalleryImage, GalleryImageAdmin)
