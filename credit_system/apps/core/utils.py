import math
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from typing import Union, Optional
from django.core.exceptions import ValidationError

def round_to_nearest_lakh(amount: Union[int, float, Decimal]) -> int:
    if amount <= 0:
        return 0
    lakh = 100000
    return round(float(amount) / lakh) * lakh

def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    if principal <= 0 or tenure_months <= 0:
        return 0
    if annual_rate <= 0:
        return principal / tenure_months
    monthly_rate = annual_rate / (12 * 100)
    power_term = (1 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * power_term / (power_term - 1)
    return round(emi, 2)

def calculate_total_interest(principal: float, emi: float, tenure_months: int) -> float:
    total_payment = emi * tenure_months
    return total_payment - principal

def validate_phone_number(phone_number: Union[str, int]) -> bool:
    phone_str = str(phone_number)
    phone_str = phone_str.replace(' ', '').replace('-', '').replace('+', '')
    if not phone_str.isdigit():
        return False
    if len(phone_str) == 10:
        return phone_str[0] in ['6', '7', '8', '9']
    if len(phone_str) == 12 and phone_str.startswith('91'):
        return phone_str[2] in ['6', '7', '8', '9']
    return False

def format_currency(amount: Union[int, float, Decimal], currency: str = '₹') -> str:
    if amount is None:
        return f"{currency}0"
    amount = float(amount)
    if amount >= 10000000:
        return f"{currency}{amount/10000000:.1f}Cr"
    elif amount >= 100000:
        return f"{currency}{amount/100000:.1f}L"
    elif amount >= 1000:
        return f"{currency}{amount/1000:.1f}K"
    else:
        return f"{currency}{amount:,.0f}"

def calculate_age_from_dob(date_of_birth: datetime) -> int:
    today = datetime.now().date()
    dob = date_of_birth.date() if isinstance(date_of_birth, datetime) else date_of_birth
    age = today.year - dob.year
    if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
        age -= 1
    return max(0, age)

def months_between_dates(start_date: datetime, end_date: datetime) -> int:
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    if end_date.day < start_date.day:
        months -= 1
    return max(0, months)

def is_current_year(date_obj: datetime) -> bool:
    return date_obj.year == datetime.now().year

def calculate_debt_to_income_ratio(monthly_debt: float, monthly_income: float) -> float:
    if monthly_income <= 0:
        return 100.0
    return min(100.0, (monthly_debt / monthly_income) * 100)

def get_risk_category(credit_score: int) -> str:
    if credit_score > 80:
        return "Low Risk"
    elif credit_score > 60:
        return "Medium Risk"
    elif credit_score > 40:
        return "High Risk"
    else:
        return "Very High Risk"

def get_recommended_interest_rate(credit_score: int) -> float:
    if credit_score > 50:
        return 10.0
    elif credit_score > 30:
        return 12.0
    elif credit_score > 10:
        return 16.0
    else:
        return 0.0

def sanitize_string(input_string: str, max_length: int = 100) -> str:
    if not input_string:
        return ""
    cleaned = input_string.strip()[:max_length]
    cleaned = ''.join(char for char in cleaned if char.isprintable())
    return cleaned

def validate_loan_amount(amount: Union[int, float], min_amount: int = 1000, max_amount: int = 50000000) -> bool:
    try:
        amount = float(amount)
        return min_amount <= amount <= max_amount
    except (ValueError, TypeError):
        return False

def validate_tenure(tenure: int, min_tenure: int = 1, max_tenure: int = 600) -> bool:
    try:
        tenure = int(tenure)
        return min_tenure <= tenure <= max_tenure
    except (ValueError, TypeError):
        return False

def validate_interest_rate(rate: float, min_rate: float = 0.1, max_rate: float = 50.0) -> bool:
    try:
        rate = float(rate)
        return min_rate <= rate <= max_rate
    except (ValueError, TypeError):
        return False

class LoanCalculator:
    @staticmethod
    def get_amortization_schedule(principal: float, annual_rate: float, tenure_months: int) -> list:
        emi = calculate_emi(principal, annual_rate, tenure_months)
        monthly_rate = annual_rate / (12 * 100)
        balance = principal
        schedule = []
        for month in range(1, tenure_months + 1):
            interest_payment = balance * monthly_rate
            principal_payment = emi - interest_payment
            balance -= principal_payment
            schedule.append({
                'month': month,
                'emi': round(emi, 2),
                'principal': round(principal_payment, 2),
                'interest': round(interest_payment, 2),
                'balance': round(max(0, balance), 2)
            })
        return schedule
    @staticmethod
    def calculate_prepayment_savings(principal: float, annual_rate: float, tenure_months: int, 
                                   prepayment_amount: float, prepayment_month: int) -> dict:
        original_emi = calculate_emi(principal, annual_rate, tenure_months)
        original_total = original_emi * tenure_months
        monthly_rate = annual_rate / (12 * 100)
        balance = principal
        for month in range(prepayment_month):
            interest = balance * monthly_rate
            principal_part = original_emi - interest
            balance -= principal_part
        new_balance = max(0, balance - prepayment_amount)
        if new_balance <= 0:
            new_tenure = prepayment_month
            interest_saved = (tenure_months - prepayment_month) * original_emi
        else:
            if monthly_rate > 0:
                new_tenure = math.ceil(
                    math.log(1 + (new_balance * monthly_rate / original_emi)) / 
                    math.log(1 + monthly_rate)
                ) + prepayment_month
            else:
                new_tenure = math.ceil(new_balance / original_emi) + prepayment_month
            interest_saved = (tenure_months - new_tenure) * original_emi
        return {
            'original_total_payment': round(original_total, 2),
            'new_tenure_months': new_tenure,
            'months_saved': max(0, tenure_months - new_tenure),
            'interest_saved': round(max(0, interest_saved), 2),
            'new_balance_after_prepayment': round(new_balance, 2)
        }