from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.vault import GoalCreate, GoalUpdate, GoalResponse
from database import goals_collection
from utils.dependencies import get_current_user
from utils.helpers import generate_id, log_audit
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=GoalResponse, status_code=201)
async def create_goal(goal: GoalCreate, current_user: dict = Depends(get_current_user)):
    """Create a new financial goal"""
    goal_id = generate_id("goal_")
    
    # Calculate progress
    progress_percentage = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
    
    # Calculate months remaining
    months_remaining = max(0, (goal.target_date - datetime.utcnow()).days // 30)
    
    goal_doc = {
        "goal_id": goal_id,
        "user_id": current_user["user_id"],
        **goal.dict(),
        "progress_percentage": round(progress_percentage, 2),
        "months_remaining": months_remaining,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    goals_collection.insert_one(goal_doc)
    log_audit(current_user["user_id"], "CREATE", "goal", {"goal_id": goal_id})
    
    return goal_doc

@router.get("/", response_model=List[GoalResponse])
async def get_goals(current_user: dict = Depends(get_current_user)):
    """Get all financial goals"""
    goals = list(goals_collection.find(
        {"user_id": current_user["user_id"]},
        {"_id": 0}
    ).limit(50))
    
    # Update dynamic fields
    for goal in goals:
        goal["progress_percentage"] = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
        goal["months_remaining"] = max(0, (goal["target_date"] - datetime.utcnow()).days // 30)
    
    return goals

@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(goal_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific goal"""
    goal = goals_collection.find_one({
        "goal_id": goal_id,
        "user_id": current_user["user_id"]
    })
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    goal["progress_percentage"] = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
    goal["months_remaining"] = max(0, (goal["target_date"] - datetime.utcnow()).days // 30)
    
    return goal

@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(goal_id: str, goal_update: GoalUpdate, current_user: dict = Depends(get_current_user)):
    """Update goal progress"""
    goal = goals_collection.find_one({
        "goal_id": goal_id,
        "user_id": current_user["user_id"]
    })
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    update_data = {k: v for k, v in goal_update.dict(exclude_unset=True).items()}
    update_data["updated_at"] = datetime.utcnow()
    
    goals_collection.update_one(
        {"goal_id": goal_id},
        {"$set": update_data}
    )
    
    log_audit(current_user["user_id"], "UPDATE", "goal", {"goal_id": goal_id})
    
    updated_goal = goals_collection.find_one({"goal_id": goal_id})
    updated_goal["progress_percentage"] = (updated_goal["current_amount"] / updated_goal["target_amount"] * 100) if updated_goal["target_amount"] > 0 else 0
    updated_goal["months_remaining"] = max(0, (updated_goal["target_date"] - datetime.utcnow()).days // 30)
    
    return updated_goal

@router.delete("/{goal_id}")
async def delete_goal(goal_id: str, current_user: dict = Depends(get_current_user)):
    """Delete goal"""
    result = goals_collection.delete_one({
        "goal_id": goal_id,
        "user_id": current_user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    log_audit(current_user["user_id"], "DELETE", "goal", {"goal_id": goal_id})
    
    return {"message": "Goal deleted successfully"}

@router.post("/retirement-calculator")
async def calculate_retirement(current_age: int, retirement_age: int, monthly_expenses: float, inflation_rate: float = 6.0):
    """Calculate retirement corpus needed"""
    years_to_retirement = retirement_age - current_age
    years_in_retirement = 85 - retirement_age  # Assume life expectancy of 85
    
    # Calculate future monthly expenses considering inflation
    future_monthly_expense = monthly_expenses * ((1 + inflation_rate / 100) ** years_to_retirement)
    
    # Calculate total corpus needed (annual expense * years in retirement)
    annual_expense_at_retirement = future_monthly_expense * 12
    total_corpus_needed = annual_expense_at_retirement * years_in_retirement
    
    # Assuming 6% post-retirement returns to sustain
    safe_withdrawal_rate = 0.04  # 4% rule
    corpus_needed_with_swr = future_monthly_expense * 12 / safe_withdrawal_rate
    
    return {
        "current_age": current_age,
        "retirement_age": retirement_age,
        "years_to_retirement": years_to_retirement,
        "current_monthly_expense": monthly_expenses,
        "future_monthly_expense": round(future_monthly_expense, 2),
        "corpus_needed": round(corpus_needed_with_swr, 2),
        "inflation_rate": inflation_rate,
        "recommended_monthly_sip": round(corpus_needed_with_swr / (years_to_retirement * 12), 2)
    }