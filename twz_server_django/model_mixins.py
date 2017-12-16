from django.db import models
import uuid


class SelectRelatedManager(models.Manager):
    use_for_related_fields = True

    def get_select_related_list(self):
        """
        Override this to provide custom select related fields.
        Defaults to empty list, which works for simple cases.
        """
        return []

    def get_model_choice_fields(self):
        """
        Override this to provide list of fields to be used in 'only'.
        Defaults to id.
        """
        return ['id', ]

    def model_choice_queryset(self):
        #we don't want select related here, so get the super of the parent class.
        qs = super(SelectRelatedManager, self).get_queryset()
        return qs.only(*self.get_model_choice_fields())

    def get_queryset(self):
        return super(SelectRelatedManager, self).get_queryset().select_related(*self.get_select_related_list())


class CreatedModifiedModelManager(SelectRelatedManager):
    def get_select_related_list(self):
        return ['created_by', 'modified_by']


class CreatedModifiedModel(models.Model):
    objects = CreatedModifiedModelManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('drf_users.User', null=True, blank=True, related_name="%(app_label)s_%(class)s_created_by_related")
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False)
    modified_by = models.ForeignKey('drf_users.User', null=True, blank=True, related_name="%(app_label)s_%(class)s_modified_by_related")

    # def save(self, *args, **kwargs):
    #     if not self.created_on:
    #         self.created_on = timezone.now()
    #
    #     self.modified_on = timezone.now()
    #
    #     #TODO: Make sure you handle the created/modifed users.  Probably needs to be done at the view level.
    #     return super(CreatedModifiedModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, request=None):
        if request:
            if self.created_by:
                self.modified_by = request.user
            else:
                self.modified_by = request.user
                self.created_by = request.user

        return super(CreatedModifiedModel, self).save(force_insert, force_update, using, update_fields)