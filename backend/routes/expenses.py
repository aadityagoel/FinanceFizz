from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.liabilities import ExpenseCreate, ExpenseResponse
from database import expenses_collection
from utils.dependencies import get_current_user
from utils.helpers import generate_id, log_audit
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=ExpenseResponse, status_code=201)
async def create_expense(expense: ExpenseCreate, current_user: dict = Depends(get_current_user)):
    """Create a new expense"""
    expense_id = generate_id("exp_")
    
    expense_doc = {
        "expense_id": expense_id,
        "user_id": current_user["user_id"],
        **expense.dict(),
        "created_at": datetime.utcnow()
    }
    
    expenses_collection.insert_one(expense_doc)
    log_audit(current_user["user_id"], "CREATE", "expense", {"expense_id": expense_id})
    
    return expense_doc

@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(current_user: dict = Depends(get_current_user)):
    """Get all expenses"""
    expenses = list(expenses_collection.find({"user_id": current_user["user_id"]}).sort("expense_date", -1))
    return expenses

@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific expense"""
    expense = expenses_collection.find_one({
        "expense_id": expense_id,
        "user_id": current_user["user_id"]
    })
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return expense

@router.delete("/{expense_id}")
async def delete_expense(expense_id: str, current_user: dict = Depends(get_current_user)):
    """Delete expense"""
    result = expenses_collection.delete_one({
        "expense_id": expense_id,
        "user_id": current_user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    log_audit(current_user["user_id"], "DELETE", "expense", {"expense_id": expense_id})
    
    return {"message": "Expense deleted successfully"}