from django.urls import include, path
from envoy_bu_policy_api.claims.urls import urlpatterns as claim_urls
from envoy_bu_policy_api.policy.urls import urlpatterns as policy_urls
from envoy_bu_policy_api.finance.urls import urlpatterns as finance_urls

urlpatterns = [
    path('api/', include(claim_urls)),
    path('api/', include(policy_urls)),
    path('api/', include(finance_urls)),
]
