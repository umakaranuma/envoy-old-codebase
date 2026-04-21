from django.urls import include, path
from envoy_bu_report_api.reports.urls import urlpatterns as report_urls

urlpatterns = [
    # Report API URLs Prefix
    path('api/', include(report_urls)),
]
