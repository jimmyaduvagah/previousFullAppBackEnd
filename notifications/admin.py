from django.contrib import admin

# Register your models here.
from notifications.models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'is_seen', 'when_seen', 'created_on', 'modified_on')
    list_filter = (
        ('from_user', admin.RelatedOnlyFieldListFilter),
        ('to_user', admin.RelatedOnlyFieldListFilter),
        ('is_seen', admin.BooleanFieldListFilter),
    )


# Re-register UserAdmin
admin.site.register(Notification, NotificationAdmin)
