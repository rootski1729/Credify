"""
URL configuration for credit_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path
from apps.customers import views as customer_views
from apps.loans import views as loan_views


schema_view = get_schema_view(
    openapi.Info(
        title="Credit Approval System API",
        default_version='v1',
        description="API for Credit Approval System",
        contact=openapi.Contact(email="admin@creditapp.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.customers.urls')),
    path('api/', include('apps.loans.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('register/', customer_views.register_customer, name='register_customer'),
    path('check-eligibility/', loan_views.check_loan_eligibility, name='check_loan_eligibility'),
    path('create-loan/', loan_views.create_loan, name='create_loan'),
    path('view-loan/<int:loan_id>/', loan_views.view_loan_details, name='view_loan_details'),
    path('view-loans/<int:customer_id>/', loan_views.view_customer_loans, name='view_customer_loans'),
]
