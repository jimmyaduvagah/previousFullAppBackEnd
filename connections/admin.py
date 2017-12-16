from connections.models import Connection, ConnectionRequest
from django.contrib import admin


class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'state', 'created_on', 'modified_on')
    list_filter = (
        ('from_user', admin.RelatedOnlyFieldListFilter),
        ('to_user', admin.RelatedOnlyFieldListFilter),
        ('state', admin.ChoicesFieldListFilter),
    )


class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'state', 'created_on', 'modified_on')
    list_filter = (
        ('from_user', admin.RelatedOnlyFieldListFilter),
        ('to_user', admin.RelatedOnlyFieldListFilter),
        ('state', admin.ChoicesFieldListFilter),
    )

admin.site.register(Connection, ConnectionAdmin)
admin.site.register(ConnectionRequest, ConnectionRequestAdmin)
