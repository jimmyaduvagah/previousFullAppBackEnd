from django.db import models

from django.contrib.postgres.fields.jsonb import JSONField
from ordered_model.models import OrderedModel

from course_module_sections.models import make_markdown
from twz_server_django.model_mixins import CreatedModifiedModel, CreatedModifiedModelManager


class Quiz(CreatedModifiedModel):
    title = models.CharField(max_length=255, blank=False, null=False)
    instructions = models.TextField(blank=True, null=False, default='')
    instructions_html = models.TextField(blank=True, null=False, default='')

    def __str__(self):
        return "%s" % self.title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, request=None):
        self.instructions_html = make_markdown(self.instructions)
        return super(Quiz, self).save(force_insert, force_update, using, update_fields)


class QuizQuestionManager(CreatedModifiedModelManager):

    def get_queryset(self, *args, **kwargs):
        qs = super(QuizQuestionManager, self).get_queryset()
        qs.order_by('quiz_question', 'order')
        return qs


class QuizQuestion(CreatedModifiedModel, OrderedModel):

    objects = QuizQuestionManager()

    quiz = models.ForeignKey('quizzes.Quiz', null=False, blank=False)
    question = models.TextField(blank=False, null=False)
    correct_answer = models.ForeignKey('quizzes.QuizQuestionAnswer', null=True, blank=True)

    order_with_respect_to = 'quiz'

    def __str__(self):
        return "%s" % self.question


class QuizQuestionAnswer(CreatedModifiedModel, OrderedModel):
    quiz_question = models.ForeignKey('quizzes.QuizQuestion', null=False, blank=False)
    answer = models.TextField(blank=False, null=False)

    order_with_respect_to = 'quiz_question'

    def __str__(self):
        return "%s" % self.answer