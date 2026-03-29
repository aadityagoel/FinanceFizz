from fastapi import APIRouter, Depends
from typing import List, Dict
from database import (
    accounts_collection, investments_collection, expenses_collection,
    insurance_collection, loans_collection
)
from utils.dependencies import get_current_user
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# AI Configuration
AI_ENABLED = os.getenv("AI_ENABLED", "false").lower() == "true"
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # openai or gemini

# Rule-based recommendation engine
def generate_rule_based_recommendations(user_id: str) -> List[Dict]:
    """Generate recommendations using rule-based logic"""
    recommendations = []
    
    # Get user data
    accounts = list(accounts_collection.find(
        {"user_id": user_id},
        {"balance": 1, "_id": 0}
    ))
    investments = list(investments_collection.find(
        {"user_id": user_id},
        {"current_value": 1, "investment_type": 1, "_id": 0}
    ))
    insurance_policies = list(insurance_collection.find(
        {"user_id": user_id},
        {"insurance_type": 1, "_id": 0}
    ))
    loans = list(loans_collection.find(
        {"user_id": user_id},
        {"remaining_balance": 1, "_id": 0}
    ))
    
    # Calculate totals
    total_cash = sum(acc.get("balance", 0) for acc in accounts)
    total_investments = sum(inv.get("current_value", 0) for inv in investments)
    total_debt = sum(loan.get("remaining_balance", 0) for loan in loans)
    
    # Get expenses
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    expenses = list(expenses_collection.find({
        "user_id": user_id,
        "expense_date": {"$gte": thirty_days_ago}
    }, {"amount": 1, "category": 1, "_id": 0}).limit(100))
    monthly_expenses = sum(exp.get("amount", 0) for exp in expenses)
    
    # 1. Emergency Fund Check
    emergency_fund_needed = monthly_expenses * 6
    if total_cash < emergency_fund_needed:
        recommendations.append({
            "priority": "high",
            "category": "emergency_fund",
            "title": "Build Emergency Fund",
            "description": f"You need ₹{emergency_fund_needed - total_cash:,.2f} more to have 6 months of expenses saved.",
            "action": "Save more liquid cash to reach 6 months of expenses",
            "impact": "Protects against unexpected financial emergencies"
        })
    
    # 2. Insurance Check - Health
    has_health_insurance = any(pol.get("insurance_type") == "health" for pol in insurance_policies)
    if not has_health_insurance:
        recommendations.append({
            "priority": "high",
            "category": "insurance",
            "title": "Get Health Insurance",
            "description": "You don't have any health insurance coverage.",
            "action": "Purchase health insurance with minimum ₹5 lakh coverage",
            "impact": "Protects against medical emergencies and expenses"
        })
    
    # 3. Insurance Check - Term
    has_term_insurance = any(pol.get("insurance_type") == "term" for pol in insurance_policies)
    if not has_term_insurance and monthly_expenses > 0:
        annual_income_estimate = monthly_expenses * 1.5 * 12
        recommended_coverage = annual_income_estimate * 15
        recommendations.append({
            "priority": "high",
            "category": "insurance",
            "title": "Get Term Life Insurance",
            "description": "You don't have term life insurance.",
            "action": f"Purchase term insurance with ₹{recommended_coverage:,.0f} coverage",
            "impact": "Financially protects your family in case of unfortunate events"
        })
    
    # 4. Debt Management
    if total_debt > total_cash * 2:
        recommendations.append({
            "priority": "medium",
            "category": "debt",
            "title": "Reduce Debt",
            "description": f"Your debt (₹{total_debt:,.2f}) is high compared to liquid assets.",
            "action": "Focus on paying down high-interest debt first",
            "impact": "Reduces interest payments and financial stress"
        })
    
    # 5. Investment Diversification
    if investments:
        equity_investments = [inv for inv in investments if inv.get("investment_type") in ["stock", "mutual_fund"]]
        equity_value = sum(inv.get("current_value", 0) for inv in equity_investments)
        equity_percentage = (equity_value / total_investments * 100) if total_investments > 0 else 0
        
        if equity_percentage > 80:
            recommendations.append({
                "priority": "medium",
                "category": "investment",
                "title": "Diversify Portfolio",
                "description": f"Your portfolio is {equity_percentage:.1f}% in equity.",
                "action": "Consider adding debt instruments or gold for better diversification",
                "impact": "Reduces portfolio risk and volatility"
            })
    
    # 6. Savings Rate
    if monthly_expenses > 0:
        investment_expenses = sum(exp.get("amount", 0) for exp in expenses if exp.get("category") == "investments")
        savings_rate = (investment_expenses / monthly_expenses * 100) if monthly_expenses > 0 else 0
        
        if savings_rate < 20:
            recommendations.append({
                "priority": "medium",
                "category": "savings",
                "title": "Increase Savings Rate",
                "description": f"You're saving only {savings_rate:.1f}% of your income.",
                "action": "Try to save at least 20% of your income through SIPs or recurring deposits",
                "impact": "Builds wealth faster and achieves financial goals sooner"
            })
    
    # 7. Budget Optimization (50-30-20 rule)
    if expenses:
        needs = sum(exp.get("amount", 0) for exp in expenses if exp.get("category") == "needs")
        wants = sum(exp.get("amount", 0) for exp in expenses if exp.get("category") == "wants")
        investments_exp = sum(exp.get("amount", 0) for exp in expenses if exp.get("category") == "investments")
        
        total_exp = needs + wants + investments_exp
        if total_exp > 0:
            wants_percentage = (wants / total_exp * 100)
            if wants_percentage > 40:
                recommendations.append({
                    "priority": "low",
                    "category": "budget",
                    "title": "Optimize Spending",
                    "description": f"You're spending {wants_percentage:.1f}% on wants (lifestyle).",
                    "action": "Follow 50-30-20 rule: 50% needs, 30% wants, 20% investments",
                    "impact": "Better financial discipline and increased savings"
                })
    
    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
    
    return recommendations

# AI-powered recommendation engine (skeleton for future)
async def generate_ai_recommendations(user_id: str, user_data: dict) -> List[Dict]:
    """Generate AI-powered recommendations using GPT/Gemini"""
    # This is a skeleton for AI integration
    # When AI_ENABLED=true, this function will call OpenAI/Gemini APIs
    
    if not AI_ENABLED:
        return []
    
    try:
        # Prepare context for AI
        context = f"""
        User Financial Profile:
        - Total Cash: {user_data.get('total_cash', 0)}
        - Total Investments: {user_data.get('total_investments', 0)}
        - Total Debt: {user_data.get('total_debt', 0)}
        - Monthly Expenses: {user_data.get('monthly_expenses', 0)}
        - Has Health Insurance: {user_data.get('has_health_insurance', False)}
        - Has Term Insurance: {user_data.get('has_term_insurance', False)}
        
        Generate personalized financial recommendations for this user.
        """
        
        # TODO: Implement actual AI API calls here
        if AI_PROVIDER == "openai":
            # OpenAI GPT integration
            # from openai import OpenAI
            # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            # response = client.chat.completions.create(...)
            pass
        elif AI_PROVIDER == "gemini":
            # Google Gemini integration
            # import google.generativeai as genai
            # model = genai.GenerativeModel('gemini-pro')
            # response = model.generate_content(context)
            pass
        
        # For now, return empty (AI integration ready but not active)
        return []
    
    except Exception as e:
        print(f"AI recommendation error: {e}")
        return []

@router.get("/")
async def get_recommendations(current_user: dict = Depends(get_current_user)):
    """Get personalized financial recommendations"""
    user_id = current_user["user_id"]
    
    # Get user data summary
    accounts = list(accounts_collection.find(
        {"user_id": user_id},
        {"balance": 1, "_id": 0}
    ))
    investments = list(investments_collection.find(
        {"user_id": user_id},
        {"current_value": 1, "_id": 0}
    ))
    insurance_policies = list(insurance_collection.find(
        {"user_id": user_id},
        {"insurance_type": 1, "_id": 0}
    ))
    loans = list(loans_collection.find(
        {"user_id": user_id},
        {"remaining_balance": 1, "_id": 0}
    ))
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    expenses = list(expenses_collection.find({
        "user_id": user_id,
        "expense_date": {"$gte": thirty_days_ago}
    }, {"amount": 1, "_id": 0}).limit(100))
    
    user_data = {
        "total_cash": sum(acc.get("balance", 0) for acc in accounts),
        "total_investments": sum(inv.get("current_value", 0) for inv in investments),
        "total_debt": sum(loan.get("remaining_balance", 0) for loan in loans),
        "monthly_expenses": sum(exp.get("amount", 0) for exp in expenses),
        "has_health_insurance": any(pol.get("insurance_type") == "health" for pol in insurance_policies),
        "has_term_insurance": any(pol.get("insurance_type") == "term" for pol in insurance_policies)
    }
    
    # Generate rule-based recommendations
    rule_recommendations = generate_rule_based_recommendations(user_id)
    
    # Generate AI recommendations if enabled
    ai_recommendations = await generate_ai_recommendations(user_id, user_data) if AI_ENABLED else []
    
    return {
        "ai_enabled": AI_ENABLED,
        "ai_provider": AI_PROVIDER if AI_ENABLED else None,
        "recommendations": rule_recommendations,
        "ai_recommendations": ai_recommendations,
        "total_count": len(rule_recommendations) + len(ai_recommendations)
    }

@router.get("/salary-allocation")
async def get_salary_allocation_suggestion(monthly_income: float):
    """Suggest salary allocation based on 50-30-20 rule"""
    return {
        "monthly_income": monthly_income,
        "allocation": {
            "needs": {
                "amount": monthly_income * 0.5,
                "percentage": 50,
                "description": "Essential expenses (rent, groceries, utilities, EMIs)"
            },
            "wants": {
                "amount": monthly_income * 0.3,
                "percentage": 30,
                "description": "Lifestyle expenses (dining, entertainment, shopping)"
            },
            "investments": {
                "amount": monthly_income * 0.2,
                "percentage": 20,
                "description": "Savings and investments (SIPs, FDs, emergency fund)"
            }
        },
        "note": "This is a guideline. Adjust based on your circumstances and goals."
    }