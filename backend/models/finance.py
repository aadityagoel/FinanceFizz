from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AccountType(str, Enum):
    BANK = "bank"
    DEMAT = "demat"
    UPI = "upi"
    CREDIT_CARD = "credit_card"

class AccountBase(BaseModel):
    institution_name: str
    account_type: AccountType
    account_number: str  # Will be encrypted
    balance: float = 0.0
    nominee_id: Optional[str] = None
    notes: Optional[str] = None

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    institution_name: Optional[str] = None
    balance: Optional[float] = None
    nominee_id: Optional[str] = None
    notes: Optional[str] = None

class AccountResponse(AccountBase):
    account_id: str
    user_id: str
    account_number_masked: str
    created_at: datetime
    updated_at: datetime

class InvestmentType(str, Enum):
    MUTUAL_FUND = "mutual_fund"
    STOCK = "stock"
    P2P = "p2p"
    GOLD = "gold"
    OTHER = "other"

class InvestmentBase(BaseModel):
    investment_type: InvestmentType
    name: str
    platform: str
    amount_invested: float
    current_value: float
    investment_date: datetime
    nominee_id: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []

class InvestmentCreate(InvestmentBase):
    pass

class InvestmentUpdate(BaseModel):
    current_value: Optional[float] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class InvestmentResponse(InvestmentBase):
    investment_id: str
    user_id: str
    gain_loss: float
    gain_loss_percentage: float
    created_at: datetime
    updated_at: datetime

class SIPBase(BaseModel):
    investment_id: str
    amount: float
    frequency: str  # monthly, quarterly
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"  # active, paused, completed

class SIPCreate(SIPBase):
    pass

class SIPResponse(SIPBase):
    sip_id: str
    user_id: str
    total_invested: float
    created_at: datetime