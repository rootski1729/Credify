from django.urls import path
from .views import check_loan_eligibility

urlpatterns = [
    path('check-eligibility/', check_loan_eligibility, name='check_loan_eligibility'),
] 