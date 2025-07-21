from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from apps.customers.models import Customer
from apps.loans.models import Loan


class CreditScoring:

    def __init__(self, customer_id):
        self.customer = Customer.objects.get(customer_id=customer_id)
        self.loans = Loan.objects.filter(customer=self.customer)
        
    def calculate_credit_score(self):
        
        current_debt = self.get_current_debt()
        if current_debt > self.customer.approved_limit:
            return 0
        
        score = 0
        
        score += self._calculate_payment_history_score() * 0.30
        score += self._calculate_loan_count_score() * 0.20
        score += self._calculate_current_year_activity_score() * 0.25
        score += self._calculate_loan_volume_score() * 0.25
        
        return min(100, max(0, round(score)))
    
    def _calculate_payment_history_score(self):
        total_emis = 0
        paid_on_time = 0
        
        for loan in self.loans:
            total_emis += loan.tenure
            paid_on_time += loan.emis_paid_on_time
        
        if total_emis == 0:
            return 50
        
        payment_ratio = paid_on_time / total_emis
        return payment_ratio * 100
    
    def _calculate_loan_count_score(self):
        loan_count = self.loans.count()
        
        if loan_count == 0:
            return 80
        elif loan_count <= 2:
            return 90
        elif loan_count <= 5:
            return 70
        elif loan_count <= 10:
            return 50
        else:
            return 20
    
    def _calculate_current_year_activity_score(self):
        current_year = datetime.now().year
        current_year_loans = self.loans.filter(
            start_date__year=current_year
        ).count()
        
        if current_year_loans == 0:
            return 80
        elif current_year_loans <= 1:
            return 90
        elif current_year_loans <= 2:
            return 60
        elif current_year_loans <= 3:
            return 30
        else:
            return 10
    
    def _calculate_loan_volume_score(self):
        total_loan_amount = self.loans.aggregate(
            total=Sum('loan_amount')
        )['total'] or 0
        
        if self.customer.approved_limit == 0:
            return 50
        
        volume_ratio = float(total_loan_amount) / self.customer.approved_limit
        
        if volume_ratio <= 0.3:
            return 100
        elif volume_ratio <= 0.5:
            return 80
        elif volume_ratio <= 0.7:
            return 60
        elif volume_ratio <= 1.0:
            return 40
        else:
            return 10
    
    def get_current_debt(self):
        current_debt = 0
        for loan in self.loans:
            if loan.is_active:
                current_debt += loan.current_debt
        return current_debt
    
    def get_current_emi_sum(self):
        current_emis = 0
        for loan in self.loans:
            if loan.is_active:
                current_emis += loan.monthly_payment
        return current_emis
    
    def check_eligibility(self, loan_amount, interest_rate, tenure):
        credit_score = self.calculate_credit_score()
        
        principal = float(loan_amount)
        monthly_rate = float(interest_rate) / (12 * 100)
        
        if monthly_rate == 0:
            monthly_emi = principal / tenure
        else:
            monthly_emi = principal * monthly_rate * (1 + monthly_rate) ** tenure / ((1 + monthly_rate) ** tenure - 1)
        
        current_emis = self.get_current_emi_sum()
        total_emis = current_emis + monthly_emi
        max_allowed_emi = self.customer.monthly_salary * 0.5
        
        if total_emis > max_allowed_emi:
            return {
                'approved': False,
                'credit_score': credit_score,
                'corrected_interest_rate': interest_rate,
                'monthly_installment': monthly_emi,
                'reason': 'EMI exceeds 50% of monthly salary'
            }
        
        if credit_score > 50:
            return {
                'approved': True,
                'credit_score': credit_score,
                'corrected_interest_rate': interest_rate,
                'monthly_installment': monthly_emi
            }
        elif credit_score > 30:
            corrected_rate = max(interest_rate, 12.0)
            if corrected_rate != interest_rate:
                corrected_monthly_rate = corrected_rate / (12 * 100)
                monthly_emi = principal * corrected_monthly_rate * (1 + corrected_monthly_rate) ** tenure / ((1 + corrected_monthly_rate) ** tenure - 1)
            
            return {
                'approved': True,
                'credit_score': credit_score,
                'corrected_interest_rate': corrected_rate,
                'monthly_installment': monthly_emi
            }
        elif credit_score > 10:
            corrected_rate = max(interest_rate, 16.0)
            if corrected_rate != interest_rate:
                corrected_monthly_rate = corrected_rate / (12 * 100)
                monthly_emi = principal * corrected_monthly_rate * (1 + corrected_monthly_rate) ** tenure / ((1 + corrected_monthly_rate) ** tenure - 1)
            
            return {
                'approved': True,
                'credit_score': credit_score,
                'corrected_interest_rate': corrected_rate,
                'monthly_installment': monthly_emi
            }
        else:
            return {
                'approved': False,
                'credit_score': credit_score,
                'corrected_interest_rate': interest_rate,
                'monthly_installment': monthly_emi,
                'reason': 'Credit score too low'
            }