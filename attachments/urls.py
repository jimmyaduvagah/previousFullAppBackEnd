from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from .models import *
from .views import *
from django_downloadview import ObjectDownloadView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'p33_start_date.views.home', name='home'),
    # url(r'^p33_start_date/', include('p33_start_date.foo.urls')),

    # #django download view
    url('^download/(?P<pk>[\w-]+)/$', ObjectDownloadView.as_view(model=Attachment, file_field='attachment'), name='attachment_download'),




)