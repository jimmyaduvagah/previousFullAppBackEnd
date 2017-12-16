from django.contrib import admin
from posts.models import PostLike, PostReport
from .models import Post


class PostReportAdmin(admin.ModelAdmin):
    list_display = ('post', 'post_id', 'created_by', 'created_on')
    list_filter = (
        ('post', admin.RelatedOnlyFieldListFilter),
        ('created_by', admin.RelatedOnlyFieldListFilter),
    )

class PostAdmin(admin.ModelAdmin):
    list_display = ('post_type', 'likes_count', 'shares_count', 'comments_count', 'reported', 'parent_post', 'linked_content_object', 'associated_object', 'created_by', 'created_on')
    list_filter = (
        ('post_type', admin.ChoicesFieldListFilter),
        ('reported', admin.AllValuesFieldListFilter),
        ('parent_post', admin.RelatedOnlyFieldListFilter),
        ('created_by', admin.RelatedOnlyFieldListFilter),
    )


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'created_by', 'created_on')
    list_filter = (
        ('post', admin.RelatedOnlyFieldListFilter),
        ('created_by', admin.RelatedOnlyFieldListFilter),
    )

admin.site.register(Post, PostAdmin)
admin.site.register(PostReport, PostReportAdmin)
admin.site.register(PostLike, PostLikeAdmin)
