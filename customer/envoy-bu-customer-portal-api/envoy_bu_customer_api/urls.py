from django.urls import include, path

from envoy_bu_customer_api.customer.urls import urlpatterns as customer_urls

urlpatterns = [
    path('api/', include(customer_urls)),
    path('api/login', include('envoy_bu_customer_api.accounts.urls')),
]
