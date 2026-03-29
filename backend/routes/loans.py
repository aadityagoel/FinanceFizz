from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.liabilities import LoanCreate, LoanUpdate, LoanResponse
from database import loans_collection
from utils.dependencies import get_current_user
from utils.helpers import generate_id, log_audit
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=LoanResponse, status_code=201)
async def create_loan(loan: LoanCreate, current_user: dict = Depends(get_current_user)):
    """Create a new loan"""
    loan_id = generate_id("loan_")
    
    # Calculate total interest paid
    total_paid = loan.principal_amount - loan.remaining_balance
    emi_paid_count = (loan.tenure_months - loan.remaining_tenure_months)
    total_emi_paid = emi_paid_count * loan.emi_amount
    total_interest_paid = total_emi_paid - total_paid
    
    loan_doc = {
        "loan_id": loan_id,
        "user_id": current_user["user_id"],
        **loan.dict(),
        "total_interest_paid": max(0, total_interest_paid),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    loans_collection.insert_one(loan_doc)
    log_audit(current_user["user_id"], "CREATE", "loan", {"loan_id": loan_id})
    
    return loan_doc

@router.get("/", response_model=List[LoanResponse])
async def get_loans(current_user: dict = Depends(get_current_user)):
    """Get all loans"""
    loans = list(loans_collection.find(
        {"user_id": current_user["user_id"]},
        {"_id": 0}
    ).limit(50))
    return loans

@router.get("/{loan_id}", response_model=LoanResponse)
async def get_loan(loan_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific loan"""
    loan = loans_collection.find_one({
        "loan_id": loan_id,
        "user_id": current_user["user_id"]
    })
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    return loan

@router.put("/{loan_id}", response_model=LoanResponse)
async def update_loan(loan_id: str, loan_update: LoanUpdate, current_user: dict = Depends(get_current_user)):
    """Update loan"""
    loan = loans_collection.find_one({
        "loan_id": loan_id,
        "user_id": current_user["user_id"]
    })
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    update_data = {k: v for k, v in loan_update.dict(exclude_unset=True).items()}
    update_data["updated_at"] = datetime.utcnow()
    
    loans_collection.update_one(
        {"loan_id": loan_id},
        {"$set": update_data}
    )
    
    log_audit(current_user["user_id"], "UPDATE", "loan", {"loan_id": loan_id})
    
    return loans_collection.find_one({"loan_id": loan_id})

@router.delete("/{loan_id}")
async def delete_loan(loan_id: str, current_user: dict = Depends(get_current_user)):
    """Delete loan"""
    result = loans_collection.delete_one({
        "loan_id": loan_id,
        "user_id": current_user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    log_audit(current_user["user_id"], "DELETE", "loan", {"loan_id": loan_id})
    
    return {"message": "Loan deleted successfully"}