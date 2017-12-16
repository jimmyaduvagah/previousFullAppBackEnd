from .models import *
from django.contrib import admin
#import reversion

class AttachmentAdmin(admin.ModelAdmin):
    ordering = ('-created_on',)
    list_display = ('filename', 'related', 'created_on',)
    search_fields = ('attachment', 'related',)


admin.site.register(Attachment, AttachmentAdmin)
