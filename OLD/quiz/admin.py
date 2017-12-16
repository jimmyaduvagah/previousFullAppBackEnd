from django.contrib import admin

# Register your models here.
from .models import Quiz


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', )
    list_filter = (
        # ('media_quiz', admin.RelatedOnlyFieldListFilter),
    )

admin.site.register(Quiz, QuizAdmin)
