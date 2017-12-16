from django.db import models
from django.core.urlresolvers import reverse
from django.dispatch import receiver

import os.path
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from twz_server_django.model_mixins import CreatedModifiedModel

class AttachmentManager(models.Manager):
    def get_attachments_for_object(self, obj):
        ct_id = ContentType.objects.get_for_model(obj).id
        qs = self.get_queryset()
        qs = qs.filter(content_type=ct_id, object_id=obj.id)

        return qs

    def save_attachment_for_object(self, obj, file, mime_type=None, request=None):
        file.name = file.name.replace(' ','-')
        file.name = file.name.replace('_','-')

        attachment = Attachment(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            attachment=file
        )
        if file.size:
            attachment.size = file.size
        if mime_type:
            attachment.mime_type = mime_type

        if request:
            attachment.save(request=request)
        else:
            attachment.save()

        return attachment

def attachment_location(obj, filename):
    return "%s/%s/%s" % (obj.content_type.name, obj.object_id, filename)

#TODO: Make this generic
class Attachment(CreatedModifiedModel):
    objects = AttachmentManager()
    #related to content type
    content_type = models.ForeignKey(ContentType, null=False, blank=False, related_name="rel_attachment_related_ct")
    object_id = models.UUIDField(null=False, blank=False)
    related = GenericForeignKey('content_type', 'object_id')
    size = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=255, help_text="Size of file in bytes")
    mime_type = models.CharField(max_length=255, null=True, blank=True)

    attachment = models.FileField(upload_to=attachment_location, null=False, blank=False, max_length=255)


    def filename(self):
        return os.path.basename(self.attachment.name)

    # def get_download_url(self):
    #     return reverse('attachment_download', args=[self.id])

    def get_absolute_url(self):
        try:
            url = self.related.get_absolute_url()
        except:
            url = self.get_download_url()
        return url

    # def save(self, *args, **kwargs):
    #     """
    #     Deletes duplicate on save.
    #     TODO: Allow Override this method and add the kwarg dupe=True to allow duplicates.
    #     maybe this:
    #         dupe = self.kwargs['dupe'], False
    #     """
    #     duplicates = Attachment.objects.filter(attachment=self.attachment.name) #get list of dupes before we save
    #     super(Attachment,self).save(*args,**kwargs) #save it
    #     for obj in duplicates: #delete any dupes we see, as long as we didn't accidently select the object we just created.
    #         if obj.pk != self.pk:
    #             obj.delete()



    def __str__(self):
        return u"%s - %s" % (self.related, self.filename())


@receiver(models.signals.pre_delete, sender=Attachment)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.attachment.delete(save=False)
