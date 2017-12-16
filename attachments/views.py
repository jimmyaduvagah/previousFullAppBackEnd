from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.template import Context, Template
from django.views.generic import DeleteView
from rest_framework.permissions import IsAuthenticated

from attachments.permissions import IsAllowedOrSuperuser
from attachments.serializers import AttachmentSerializer
from twz_server_django.rest_extensions import CreatedModifiedByModelViewSetMixin
from .models import Attachment
from .forms import AttachmentForm


# class AttachmentCreateView(P33UserCreateMixin):
#     model = Attachment
#     form_class = AttachmentForm
#     template_name = 'mail_templates/mailtemplate_form.html'
    #http_method_names = ['POST',]

    # def form_valid(self, form):
    #     """
    #     If the form is valid, save the associated model.
    #     """
    #     #TODO: Figure out if its a duplicate, upload the file, then remove the old MailAttachment object so we only se the latest.
    #     self.object = form.save(commit=True)
    #     # self.object.attachment.
    #     return super(AttachmentCreateView, self).form_valid(form)

#
# class AttachmentDeleteView(DeleteView):
#     model = Attachment
#
#     def dispatch(self, request, *args, **kwargs):
#         # self.related = self.get_object().related
#         return super(AttachmentDeleteView, self).dispatch(request, *args, **kwargs)
#
#     def delete(self, request, *args, **kwargs):
#         """
#         Calls the delete() method on the fetched object's attachment.
#         Calls the delete() method on the fetched object and then
#         redirects to the success URL.
#         """
#         self.object = self.get_object()
#         self.object.attachment.delete()  # delete the file from amazon before we delete the object.
#         self.object.delete()
#         return HttpResponseRedirect(self.get_success_url())
#
#     def get_success_url(self):
#         return self.related.get_absolute_url()


class AttachmentViewSet(CreatedModifiedByModelViewSetMixin):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = (IsAuthenticated,IsAllowedOrSuperuser,)

