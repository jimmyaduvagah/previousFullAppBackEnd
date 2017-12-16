from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from quizzes.models import Quiz, QuizQuestion, QuizQuestionAnswer


class QuizQuestionAnswerAdmin(OrderedModelAdmin):
    list_display = ('quiz_question', 'answer', 'created_on', 'order', 'move_up_down_links')
    list_filter = (
        ('quiz_question', admin.RelatedOnlyFieldListFilter),
    )


class QuizQuestionAdmin(OrderedModelAdmin):
    list_display = ('quiz', 'question', 'correct_answer', 'order', 'move_up_down_links')
    list_filter = (
        ('quiz', admin.RelatedOnlyFieldListFilter),
    )


class QuizAdmin(OrderedModelAdmin):
    list_display = ('title', 'id')

admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizQuestion, QuizQuestionAdmin)
admin.site.register(QuizQuestionAnswer, QuizQuestionAnswerAdmin)
