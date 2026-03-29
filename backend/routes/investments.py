from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.finance import InvestmentCreate, InvestmentUpdate, InvestmentResponse, SIPCreate, SIPResponse
from database import investments_collection, sips_collection
from utils.dependencies import get_current_user
from utils.helpers import generate_id, log_audit
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=InvestmentResponse, status_code=201)
async def create_investment(investment: InvestmentCreate, current_user: dict = Depends(get_current_user)):
    """Create a new investment"""
    investment_id = generate_id("inv_")
    
    # Calculate gain/loss
    gain_loss = investment.current_value - investment.amount_invested
    gain_loss_percentage = (gain_loss / investment.amount_invested * 100) if investment.amount_invested > 0 else 0
    
    investment_doc = {
        "investment_id": investment_id,
        "user_id": current_user["user_id"],
        **investment.dict(),
        "gain_loss": gain_loss,
        "gain_loss_percentage": round(gain_loss_percentage, 2),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    investments_collection.insert_one(investment_doc)
    log_audit(current_user["user_id"], "CREATE", "investment", {"investment_id": investment_id})
    
    return investment_doc

@router.get("/", response_model=List[InvestmentResponse])
async def get_investments(current_user: dict = Depends(get_current_user)):
    """Get all investments"""
    investments = list(investments_collection.find(
        {"user_id": current_user["user_id"]},
        {"_id": 0}
    ).limit(100))
    return investments

@router.get("/{investment_id}", response_model=InvestmentResponse)
async def get_investment(investment_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific investment"""
    investment = investments_collection.find_one({
        "investment_id": investment_id,
        "user_id": current_user["user_id"]
    })
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    return investment

@router.put("/{investment_id}", response_model=InvestmentResponse)
async def update_investment(investment_id: str, investment_update: InvestmentUpdate, current_user: dict = Depends(get_current_user)):
    """Update investment"""
    investment = investments_collection.find_one({
        "investment_id": investment_id,
        "user_id": current_user["user_id"]
    })
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    update_data = {k: v for k, v in investment_update.dict(exclude_unset=True).items()}
    
    # Recalculate gain/loss if current_value is updated
    if "current_value" in update_data:
        gain_loss = update_data["current_value"] - investment["amount_invested"]
        gain_loss_percentage = (gain_loss / investment["amount_invested"] * 100) if investment["amount_invested"] > 0 else 0
        update_data["gain_loss"] = gain_loss
        update_data["gain_loss_percentage"] = round(gain_loss_percentage, 2)
    
    update_data["updated_at"] = datetime.utcnow()
    
    investments_collection.update_one(
        {"investment_id": investment_id},
        {"$set": update_data}
    )
    
    log_audit(current_user["user_id"], "UPDATE", "investment", {"investment_id": investment_id})
    
    return investments_collection.find_one({"investment_id": investment_id})

@router.delete("/{investment_id}")
async def delete_investment(investment_id: str, current_user: dict = Depends(get_current_user)):
    """Delete investment"""
    result = investments_collection.delete_one({
        "investment_id": investment_id,
        "user_id": current_user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    log_audit(current_user["user_id"], "DELETE", "investment", {"investment_id": investment_id})
    
    return {"message": "Investment deleted successfully"}

# SIP Routes
@router.post("/sips", response_model=SIPResponse, status_code=201)
async def create_sip(sip: SIPCreate, current_user: dict = Depends(get_current_user)):
    """Create a new SIP"""
    sip_id = generate_id("sip_")
    
    sip_doc = {
        "sip_id": sip_id,
        "user_id": current_user["user_id"],
        **sip.dict(),
        "total_invested": 0.0,  # Will be calculated based on payments
        "created_at": datetime.utcnow()
    }
    
    sips_collection.insert_one(sip_doc)
    log_audit(current_user["user_id"], "CREATE", "sip", {"sip_id": sip_id})
    
    return sip_doc

@router.get("/sips", response_model=List[SIPResponse])
async def get_sips(current_user: dict = Depends(get_current_user)):
    """Get all SIPs"""
    sips = list(sips_collection.find({"user_id": current_user["user_id"]}))
    return sips