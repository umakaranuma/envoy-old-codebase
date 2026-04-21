"""
URL configuration for envoy_bu_crm_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
from django.urls import include, path
from envoy_bu_crm_api.task.urls import urlpatterns as task_urls
from envoy_bu_crm_api.sales.urls import urlpatterns as sales_urls
from envoy_bu_crm_api.quotation.urls import urlpatterns as quotation_urls
# from envoy_bu_crm_api.claims.urls import urlpatterns as claim_urls
# from envoy_bu_crm_api.policy.urls import urlpatterns as policy_urls


urlpatterns = [
    # path('', include(users_urls)),
    path('api/', include(task_urls)),
    path('api/', include(sales_urls)),
    path('api/', include(quotation_urls)),
    # path('api/', include(claim_urls)),
    # path('api/', include(policy_urls)),
]
