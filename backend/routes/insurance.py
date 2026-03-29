from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.liabilities import InsuranceCreate, InsuranceUpdate, InsuranceResponse
from database import insurance_collection
from utils.dependencies import get_current_user
from utils.helpers import generate_id, log_audit
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=InsuranceResponse, status_code=201)
async def create_insurance(insurance: InsuranceCreate, current_user: dict = Depends(get_current_user)):
    """Create a new insurance policy"""
    insurance_id = generate_id("ins_")
    
    # Calculate days to renewal
    days_to_renewal = (insurance.renewal_date - datetime.utcnow()).days
    
    insurance_doc = {
        "insurance_id": insurance_id,
        "user_id": current_user["user_id"],
        **insurance.dict(),
        "days_to_renewal": days_to_renewal,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    insurance_collection.insert_one(insurance_doc)
    log_audit(current_user["user_id"], "CREATE", "insurance", {"insurance_id": insurance_id})
    
    return insurance_doc

@router.get("/", response_model=List[InsuranceResponse])
async def get_insurance_policies(current_user: dict = Depends(get_current_user)):
    """Get all insurance policies"""
    policies = list(insurance_collection.find({"user_id": current_user["user_id"]}))
    
    # Update days_to_renewal for each policy
    for policy in policies:
        policy["days_to_renewal"] = (policy["renewal_date"] - datetime.utcnow()).days
    
    return policies

@router.get("/{insurance_id}", response_model=InsuranceResponse)
async def get_insurance(insurance_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific insurance policy"""
    insurance = insurance_collection.find_one({
        "insurance_id": insurance_id,
        "user_id": current_user["user_id"]
    })
    
    if not insurance:
        raise HTTPException(status_code=404, detail="Insurance policy not found")
    
    insurance["days_to_renewal"] = (insurance["renewal_date"] - datetime.utcnow()).days
    
    return insurance

@router.put("/{insurance_id}", response_model=InsuranceResponse)
async def update_insurance(insurance_id: str, insurance_update: InsuranceUpdate, current_user: dict = Depends(get_current_user)):
    """Update insurance policy"""
    insurance = insurance_collection.find_one({
        "insurance_id": insurance_id,
        "user_id": current_user["user_id"]
    })
    
    if not insurance:
        raise HTTPException(status_code=404, detail="Insurance policy not found")
    
    update_data = {k: v for k, v in insurance_update.dict(exclude_unset=True).items()}
    update_data["updated_at"] = datetime.utcnow()
    
    insurance_collection.update_one(
        {"insurance_id": insurance_id},
        {"$set": update_data}
    )
    
    log_audit(current_user["user_id"], "UPDATE", "insurance", {"insurance_id": insurance_id})
    
    updated_insurance = insurance_collection.find_one({"insurance_id": insurance_id})
    updated_insurance["days_to_renewal"] = (updated_insurance["renewal_date"] - datetime.utcnow()).days
    
    return updated_insurance

@router.delete("/{insurance_id}")
async def delete_insurance(insurance_id: str, current_user: dict = Depends(get_current_user)):
    """Delete insurance policy"""
    result = insurance_collection.delete_one({
        "insurance_id": insurance_id,
        "user_id": current_user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Insurance policy not found")
    
    log_audit(current_user["user_id"], "DELETE", "insurance", {"insurance_id": insurance_id})
    
    return {"message": "Insurance policy deleted successfully"}