from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ExpenseCategory(str, Enum):
    NEEDS = "needs"  # Essential expenses
    WANTS = "wants"  # Lifestyle expenses
    INVESTMENTS = "investments"  # Savings/Investments

class ExpenseBase(BaseModel):
    amount: float
    category: ExpenseCategory
    subcategory: str  # groceries, rent, entertainment, etc.
    description: str
    expense_date: datetime
    payment_method: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    expense_id: str
    user_id: str
    created_at: datetime

class LoanBase(BaseModel):
    loan_type: str  # home, car, personal, education
    lender: str
    principal_amount: float
    interest_rate: float
    emi_amount: float
    remaining_balance: float
    tenure_months: int
    remaining_tenure_months: int
    start_date: datetime
    notes: Optional[str] = None

class LoanCreate(LoanBase):
    pass

class LoanUpdate(BaseModel):
    remaining_balance: Optional[float] = None
    remaining_tenure_months: Optional[int] = None
    notes: Optional[str] = None

class LoanResponse(LoanBase):
    loan_id: str
    user_id: str
    total_interest_paid: float
    created_at: datetime
    updated_at: datetime

class InsuranceType(str, Enum):
    HEALTH = "health"
    TERM = "term"
    VEHICLE = "vehicle"
    HOME = "home"

class InsuranceBase(BaseModel):
    insurance_type: InsuranceType
    provider: str
    policy_number: str
    coverage_amount: float
    premium_amount: float
    premium_frequency: str  # monthly, quarterly, annual
    start_date: datetime
    renewal_date: datetime
    nominee_id: Optional[str] = None
    claim_instructions: Optional[str] = None
    notes: Optional[str] = None

class InsuranceCreate(InsuranceBase):
    pass

class InsuranceUpdate(BaseModel):
    renewal_date: Optional[datetime] = None
    premium_amount: Optional[float] = None
    notes: Optional[str] = None

class InsuranceResponse(InsuranceBase):
    insurance_id: str
    user_id: str
    days_to_renewal: int
    created_at: datetime
    updated_at: datetime