from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocumentCategory(str):
    IDENTITY = "identity"
    INSURANCE = "insurance"
    INVESTMENTS = "investments"
    LOANS = "loans"
    PROPERTY = "property"
    OTHER = "other"

class DocumentBase(BaseModel):
    filename: str
    category: str
    tags: List[str] = []
    description: Optional[str] = None
    extracted_text: Optional[str] = None

class DocumentResponse(DocumentBase):
    document_id: str
    user_id: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_at: datetime

class GoalBase(BaseModel):
    goal_name: str
    target_amount: float
    current_amount: float = 0.0
    target_date: datetime
    description: Optional[str] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    current_amount: Optional[float] = None
    description: Optional[str] = None

class GoalResponse(GoalBase):
    goal_id: str
    user_id: str
    progress_percentage: float
    months_remaining: int
    created_at: datetime
    updated_at: datetime

class EmergencyVaultBase(BaseModel):
    instructions: str
    emergency_contacts: List[dict] = []  # [{"name": "", "phone": "", "relation": ""}]
    asset_summary: Optional[str] = None
    access_granted_to: List[str] = []  # User IDs with restricted access

class EmergencyVaultCreate(EmergencyVaultBase):
    pass

class EmergencyVaultResponse(EmergencyVaultBase):
    vault_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

class NomineeBase(BaseModel):
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None

class NomineeCreate(NomineeBase):
    pass

class NomineeResponse(NomineeBase):
    nominee_id: str
    user_id: str
    created_at: datetime