from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.contrib import admin
import os
import logging

logger = logging.getLogger("cali_water_reports")

admin.autodiscover()

urlpatterns = [
    url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    url(r"^admin/", include(admin.site.urls)),

    # batch edit in admin
    url(r"^admin/", include("massadmin.urls")),

    # url pattern to kick root to index of cali_water application
    url(r"^monthly-water-use/", include("monthly_water_reports.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

if settings.DEBUG and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
