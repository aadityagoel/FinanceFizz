from fastapi import APIRouter, Depends
from database import (
    accounts_collection, investments_collection, loans_collection,
    insurance_collection, expenses_collection, users_collection
)
from utils.dependencies import get_current_user
from datetime import datetime, timedelta
from typing import Dict, List

router = APIRouter()

@router.get("/net-worth")
async def get_net_worth(current_user: dict = Depends(get_current_user)):
    """Calculate net worth (Assets - Liabilities)"""
    user_id = current_user["user_id"]
    
    # Calculate Assets
    accounts = list(accounts_collection.find(
        {"user_id": user_id},
        {"balance": 1, "_id": 0}
    ))
    total_cash = sum(acc.get("balance", 0) for acc in accounts)
    
    investments = list(investments_collection.find(
        {"user_id": user_id},
        {"current_value": 1, "_id": 0}
    ))
    total_investments = sum(inv.get("current_value", 0) for inv in investments)
    
    total_assets = total_cash + total_investments
    
    # Calculate Liabilities
    loans = list(loans_collection.find(
        {"user_id": user_id},
        {"remaining_balance": 1, "_id": 0}
    ))
    total_liabilities = sum(loan.get("remaining_balance", 0) for loan in loans)
    
    # Net Worth
    net_worth = total_assets - total_liabilities
    
    return {
        "net_worth": net_worth,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "breakdown": {
            "cash": total_cash,
            "investments": total_investments,
            "loans": total_liabilities
        }
    }

@router.get("/portfolio-allocation")
async def get_portfolio_allocation(current_user: dict = Depends(get_current_user)):
    """Calculate portfolio allocation breakdown"""
    user_id = current_user["user_id"]
    
    investments = list(investments_collection.find(
        {"user_id": user_id},
        {"investment_type": 1, "current_value": 1, "_id": 0}
    ))
    
    if not investments:
        return {
            "equity": 0,
            "debt": 0,
            "gold": 0,
            "others": 0,
            "total": 0,
            "breakdown": []
        }
    
    total_value = sum(inv.get("current_value", 0) for inv in investments)
    
    # Categorize investments
    equity = sum(inv.get("current_value", 0) for inv in investments if inv.get("investment_type") in ["stock", "mutual_fund"])
    debt = sum(inv.get("current_value", 0) for inv in investments if inv.get("investment_type") == "p2p")
    gold = sum(inv.get("current_value", 0) for inv in investments if inv.get("investment_type") == "gold")
    others = total_value - (equity + debt + gold)
    
    return {
        "equity": round((equity / total_value * 100) if total_value > 0 else 0, 2),
        "debt": round((debt / total_value * 100) if total_value > 0 else 0, 2),
        "gold": round((gold / total_value * 100) if total_value > 0 else 0, 2),
        "others": round((others / total_value * 100) if total_value > 0 else 0, 2),
        "total": total_value,
        "breakdown": [
            {"type": "Equity", "value": equity, "percentage": round((equity / total_value * 100) if total_value > 0 else 0, 2)},
            {"type": "Debt", "value": debt, "percentage": round((debt / total_value * 100) if total_value > 0 else 0, 2)},
            {"type": "Gold", "value": gold, "percentage": round((gold / total_value * 100) if total_value > 0 else 0, 2)},
            {"type": "Others", "value": others, "percentage": round((others / total_value * 100) if total_value > 0 else 0, 2)}
        ]
    }

@router.get("/emergency-fund-check")
async def check_emergency_fund(current_user: dict = Depends(get_current_user)):
    """Check emergency fund adequacy (6-12 months of expenses)"""
    user_id = current_user["user_id"]
    
    # Calculate average monthly expenses (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    expenses = list(expenses_collection.find({
        "user_id": user_id,
        "expense_date": {"$gte": six_months_ago}
    }, {"amount": 1, "_id": 0}))
    
    if expenses:
        total_expenses = sum(exp.get("amount", 0) for exp in expenses)
        months_count = 6
        avg_monthly_expense = total_expenses / months_count
    else:
        avg_monthly_expense = 0
    
    # Get liquid assets (cash in accounts)
    accounts = list(accounts_collection.find(
        {"user_id": user_id},
        {"balance": 1, "_id": 0}
    ))
    liquid_assets = sum(acc.get("balance", 0) for acc in accounts)
    
    # Recommendations
    min_required = avg_monthly_expense * 6
    max_recommended = avg_monthly_expense * 12
    
    months_covered = (liquid_assets / avg_monthly_expense) if avg_monthly_expense > 0 else 0
    
    status = "adequate" if liquid_assets >= min_required else "insufficient"
    if liquid_assets >= max_recommended:
        status = "excellent"
    
    return {
        "liquid_assets": liquid_assets,
        "avg_monthly_expense": round(avg_monthly_expense, 2),
        "min_required": round(min_required, 2),
        "max_recommended": round(max_recommended, 2),
        "months_covered": round(months_covered, 1),
        "gap": max(0, min_required - liquid_assets),
        "status": status
    }

@router.get("/insurance-check")
async def check_insurance_adequacy(current_user: dict = Depends(get_current_user)):
    """Check insurance coverage adequacy"""
    user_id = current_user["user_id"]
    
    # Calculate annual income (estimate from expenses)
    one_year_ago = datetime.utcnow() - timedelta(days=365)
    expenses = list(expenses_collection.find({
        "user_id": user_id,
        "expense_date": {"$gte": one_year_ago}
    }, {"amount": 1, "_id": 0}))
    
    annual_expenses = sum(exp.get("amount", 0) for exp in expenses)
    estimated_annual_income = annual_expenses * 1.5  # Rough estimate
    
    # Get insurance policies
    policies = list(insurance_collection.find(
        {"user_id": user_id},
        {"insurance_type": 1, "coverage_amount": 1, "_id": 0}
    ))
    
    term_insurance = sum(pol.get("coverage_amount", 0) for pol in policies if pol.get("insurance_type") == "term")
    health_insurance = sum(pol.get("coverage_amount", 0) for pol in policies if pol.get("insurance_type") == "health")
    
    # Recommendations
    term_recommended = estimated_annual_income * 15  # 10-15x annual income
    health_recommended = 500000  # Minimum 5 lakhs
    
    return {
        "term_insurance": {
            "current": term_insurance,
            "recommended": term_recommended,
            "gap": max(0, term_recommended - term_insurance),
            "status": "adequate" if term_insurance >= term_recommended * 0.7 else "insufficient"
        },
        "health_insurance": {
            "current": health_insurance,
            "recommended": health_recommended,
            "gap": max(0, health_recommended - health_insurance),
            "status": "adequate" if health_insurance >= health_recommended else "insufficient"
        }
    }

@router.get("/financial-health-score")
async def calculate_financial_health_score(current_user: dict = Depends(get_current_user)):
    """Calculate overall financial health score (0-100)"""
    user_id = current_user["user_id"]
    
    score = 0
    factors = []
    
    # 1. Savings Rate (25 points)
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    expenses = list(expenses_collection.find({
        "user_id": user_id,
        "expense_date": {"$gte": one_month_ago}
    }, {"amount": 1, "_id": 0}))
    monthly_expenses = sum(exp.get("amount", 0) for exp in expenses)
    
    accounts = list(accounts_collection.find(
        {"user_id": user_id},
        {"balance": 1, "_id": 0}
    ))
    cash = sum(acc.get("balance", 0) for acc in accounts)
    
    if monthly_expenses > 0:
        savings_rate = ((cash / monthly_expenses) - 1) * 100
        savings_score = min(25, max(0, savings_rate * 1.25))
    else:
        savings_score = 0
    
    score += savings_score
    factors.append({"factor": "Savings Rate", "score": round(savings_score, 1), "max": 25})
    
    # 2. Insurance Coverage (25 points)
    policies = list(insurance_collection.find(
        {"user_id": user_id},
        {"insurance_type": 1, "_id": 0}
    ))
    has_term = any(pol.get("insurance_type") == "term" for pol in policies)
    has_health = any(pol.get("insurance_type") == "health" for pol in policies)
    
    insurance_score = 0
    if has_term:
        insurance_score += 15
    if has_health:
        insurance_score += 10
    
    score += insurance_score
    factors.append({"factor": "Insurance Coverage", "score": insurance_score, "max": 25})
    
    # 3. Debt Ratio (25 points)
    loans = list(loans_collection.find(
        {"user_id": user_id},
        {"remaining_balance": 1, "_id": 0}
    ))
    total_debt = sum(loan.get("remaining_balance", 0) for loan in loans)
    
    investments = list(investments_collection.find(
        {"user_id": user_id},
        {"current_value": 1, "_id": 0}
    ))
    total_assets = cash + sum(inv.get("current_value", 0) for inv in investments)
    
    if total_assets > 0:
        debt_ratio = (total_debt / total_assets) * 100
        debt_score = max(0, 25 - (debt_ratio * 0.5))
    else:
        debt_score = 0 if total_debt > 0 else 25
    
    score += debt_score
    factors.append({"factor": "Debt Management", "score": round(debt_score, 1), "max": 25})
    
    # 4. Emergency Fund (25 points)
    if monthly_expenses > 0:
        months_covered = cash / monthly_expenses
        emergency_score = min(25, (months_covered / 6) * 25)
    else:
        emergency_score = 0
    
    score += emergency_score
    factors.append({"factor": "Emergency Fund", "score": round(emergency_score, 1), "max": 25})
    
    return {
        "total_score": round(score, 1),
        "max_score": 100,
        "rating": "Excellent" if score >= 80 else "Good" if score >= 60 else "Fair" if score >= 40 else "Needs Improvement",
        "factors": factors
    }

@router.get("/risk-score")
async def calculate_risk_score(current_user: dict = Depends(get_current_user)):
    """Calculate financial risk score"""
    user_id = current_user["user_id"]
    
    risk_score = 0
    risk_factors = []
    
    # 1. Portfolio Concentration Risk
    investments = list(investments_collection.find(
        {"user_id": user_id},
        {"current_value": 1, "_id": 0}
    ))
    if investments:
        total_value = sum(inv.get("current_value", 0) for inv in investments)
        max_single_investment = max(inv.get("current_value", 0) for inv in investments)
        concentration = (max_single_investment / total_value * 100) if total_value > 0 else 0
        
        if concentration > 50:
            risk_score += 30
            risk_factors.append({"factor": "High portfolio concentration", "impact": "high"})
        elif concentration > 30:
            risk_score += 15
            risk_factors.append({"factor": "Moderate portfolio concentration", "impact": "medium"})
    
    # 2. Debt Exposure
    loans = list(loans_collection.find(
        {"user_id": user_id},
        {"remaining_balance": 1, "_id": 0}
    ))
    accounts = list(accounts_collection.find(
        {"user_id": user_id},
        {"balance": 1, "_id": 0}
    ))
    
    total_debt = sum(loan.get("remaining_balance", 0) for loan in loans)
    total_cash = sum(acc.get("balance", 0) for acc in accounts)
    
    if total_cash > 0:
        debt_to_cash_ratio = (total_debt / total_cash) * 100
        if debt_to_cash_ratio > 200:
            risk_score += 40
            risk_factors.append({"factor": "Very high debt exposure", "impact": "high"})
        elif debt_to_cash_ratio > 100:
            risk_score += 20
            risk_factors.append({"factor": "High debt exposure", "impact": "medium"})
    
    # 3. Lack of Insurance
    policies = list(insurance_collection.find(
        {"user_id": user_id},
        {"insurance_type": 1, "_id": 0}
    ))
    if not any(pol.get("insurance_type") == "health" for pol in policies):
        risk_score += 20
        risk_factors.append({"factor": "No health insurance", "impact": "high"})
    
    if not any(pol.get("insurance_type") == "term" for pol in policies):
        risk_score += 10
        risk_factors.append({"factor": "No term insurance", "impact": "medium"})
    
    risk_level = "High" if risk_score >= 50 else "Medium" if risk_score >= 25 else "Low"
    
    return {
        "risk_score": min(100, risk_score),
        "risk_level": risk_level,
        "risk_factors": risk_factors
    }

@router.get("/expense-analysis")
async def analyze_expenses(current_user: dict = Depends(get_current_user)):
    """Analyze expense patterns"""
    user_id = current_user["user_id"]
    
    # Last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    expenses = list(expenses_collection.find({
        "user_id": user_id,
        "expense_date": {"$gte": thirty_days_ago}
    }, {"amount": 1, "category": 1, "_id": 0}))
    
    if not expenses:
        return {
            "total": 0,
            "needs": 0,
            "wants": 0,
            "investments": 0,
            "breakdown": []
        }
    
    total = sum(exp.get("amount", 0) for exp in expenses)
    needs = sum(exp.get("amount", 0) for exp in expenses if exp.get("category") == "needs")
    wants = sum(exp.get("amount", 0) for exp in expenses if exp.get("category") == "wants")
    investments = sum(exp.get("amount", 0) for exp in expenses if exp.get("category") == "investments")
    
    return {
        "total": total,
        "needs": needs,
        "wants": wants,
        "investments": investments,
        "needs_percentage": round((needs / total * 100) if total > 0 else 0, 2),
        "wants_percentage": round((wants / total * 100) if total > 0 else 0, 2),
        "investments_percentage": round((investments / total * 100) if total > 0 else 0, 2),
        "breakdown": [
            {"category": "Needs", "amount": needs, "percentage": round((needs / total * 100) if total > 0 else 0, 2)},
            {"category": "Wants", "amount": wants, "percentage": round((wants / total * 100) if total > 0 else 0, 2)},
            {"category": "Investments", "amount": investments, "percentage": round((investments / total * 100) if total > 0 else 0, 2)}
        ]
    }