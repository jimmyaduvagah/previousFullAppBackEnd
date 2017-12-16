from django import forms
# from p33_start_date.utils import P33UserModelFormMixin, P33UserInlineFormSet
from .models import Attachment


class AttachmentForm(forms.Form):
    class Meta:
        model = Attachment
        fields = ['attachment', 'content_type', 'object_id']


