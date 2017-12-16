from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

# Create your models here.
from twz_server_django.model_mixins import CreatedModifiedModel
from module.models import Module


class ModuleProgressManager(models.Manager):
    def get_for_user_and_module(self, user_id, module_id):
        query = self.filter(user_id=user_id, module_id=module_id)
        if len(query) > 0:
            new_object = query[0]
        else:
            # module = Module.objects.filter(id=module_id)
            # if len(module) > 0:
            #     module = module[0]
            # else:
            #     raise Exception('Module does not exist')

            new_object = self.create(
                user_id=user_id,
                module_id=module_id,
                modified_by_id=user_id,
                created_by_id=user_id,
            )

        return new_object


class ModuleProgress(CreatedModifiedModel):
    objects = ModuleProgressManager()

    object = JSONField(null=False, blank=True, default=dict)
    current_media = models.ForeignKey('media.Media', null=True, blank=True)
    module = models.ForeignKey('module.Module', null=False, blank=False)
    completed = models.BooleanField(default=False)
    percent_completed = models.DecimalField(default=0, decimal_places=4, max_digits=5)
    has_assessment = models.BooleanField(default=False)
    assessment_submitted = models.BooleanField(default=False)
    assessment_response_completed = models.BooleanField(default=False)
    assessment_submitted_on = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey('drf_users.User', null=False, blank=False)

