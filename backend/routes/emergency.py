from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.vault import EmergencyVaultCreate, EmergencyVaultResponse, NomineeCreate, NomineeResponse
from database import emergency_vault_collection, nominees_collection, accounts_collection, investments_collection, insurance_collection
from utils.dependencies import get_current_user
from utils.helpers import generate_id, log_audit
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

router = APIRouter()

# Nominee Routes
@router.post("/nominees", response_model=NomineeResponse, status_code=201)
async def create_nominee(nominee: NomineeCreate, current_user: dict = Depends(get_current_user)):
    """Create a nominee"""
    nominee_id = generate_id("nom_")
    
    nominee_doc = {
        "nominee_id": nominee_id,
        "user_id": current_user["user_id"],
        **nominee.dict(),
        "created_at": datetime.utcnow()
    }
    
    nominees_collection.insert_one(nominee_doc)
    log_audit(current_user["user_id"], "CREATE", "nominee", {"nominee_id": nominee_id})
    
    return nominee_doc

@router.get("/nominees", response_model=List[NomineeResponse])
async def get_nominees(current_user: dict = Depends(get_current_user)):
    """Get all nominees"""
    nominees = list(nominees_collection.find({"user_id": current_user["user_id"]}))
    return nominees

@router.delete("/nominees/{nominee_id}")
async def delete_nominee(nominee_id: str, current_user: dict = Depends(get_current_user)):
    """Delete nominee"""
    result = nominees_collection.delete_one({
        "nominee_id": nominee_id,
        "user_id": current_user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Nominee not found")
    
    log_audit(current_user["user_id"], "DELETE", "nominee", {"nominee_id": nominee_id})
    return {"message": "Nominee deleted successfully"}

# Emergency Vault Routes
@router.post("/", response_model=EmergencyVaultResponse, status_code=201)
async def create_emergency_vault(vault: EmergencyVaultCreate, current_user: dict = Depends(get_current_user)):
    """Create or update emergency vault"""
    # Check if vault already exists
    existing_vault = emergency_vault_collection.find_one({"user_id": current_user["user_id"]})
    
    if existing_vault:
        # Update existing vault
        update_data = vault.dict()
        update_data["updated_at"] = datetime.utcnow()
        
        emergency_vault_collection.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": update_data}
        )
        
        vault_doc = emergency_vault_collection.find_one({"user_id": current_user["user_id"]})
        log_audit(current_user["user_id"], "UPDATE", "emergency_vault", {"vault_id": vault_doc["vault_id"]})
    else:
        # Create new vault
        vault_id = generate_id("vault_")
        vault_doc = {
            "vault_id": vault_id,
            "user_id": current_user["user_id"],
            **vault.dict(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        emergency_vault_collection.insert_one(vault_doc)
        log_audit(current_user["user_id"], "CREATE", "emergency_vault", {"vault_id": vault_id})
    
    return vault_doc

@router.get("/", response_model=EmergencyVaultResponse)
async def get_emergency_vault(current_user: dict = Depends(get_current_user)):
    """Get emergency vault"""
    vault = emergency_vault_collection.find_one({"user_id": current_user["user_id"]})
    
    if not vault:
        raise HTTPException(status_code=404, detail="Emergency vault not found")
    
    return vault

@router.get("/generate-summary")
async def generate_emergency_summary(current_user: dict = Depends(get_current_user)):
    """Generate comprehensive emergency asset summary"""
    user_id = current_user["user_id"]
    
    # Get all financial data
    accounts = list(accounts_collection.find({"user_id": user_id}))
    investments = list(investments_collection.find({"user_id": user_id}))
    insurance_policies = list(insurance_collection.find({"user_id": user_id}))
    nominees = list(nominees_collection.find({"user_id": user_id}))
    
    # Build nominee map
    nominee_map = {nom["nominee_id"]: nom["name"] for nom in nominees}
    
    summary = {
        "user": {
            "name": current_user["full_name"],
            "email": current_user["email"]
        },
        "accounts": [
            {
                "institution": acc["institution_name"],
                "type": acc["account_type"],
                "balance": acc["balance"],
                "nominee": nominee_map.get(acc.get("nominee_id"), "Not assigned")
            }
            for acc in accounts
        ],
        "investments": [
            {
                "name": inv["name"],
                "type": inv["investment_type"],
                "platform": inv["platform"],
                "current_value": inv["current_value"],
                "nominee": nominee_map.get(inv.get("nominee_id"), "Not assigned")
            }
            for inv in investments
        ],
        "insurance": [
            {
                "type": ins["insurance_type"],
                "provider": ins["provider"],
                "policy_number": ins["policy_number"],
                "coverage": ins["coverage_amount"],
                "nominee": nominee_map.get(ins.get("nominee_id"), "Not assigned"),
                "claim_instructions": ins.get("claim_instructions", "")
            }
            for ins in insurance_policies
        ],
        "nominees": [
            {
                "name": nom["name"],
                "relationship": nom["relationship"],
                "phone": nom["phone"],
                "email": nom.get("email", "")
            }
            for nom in nominees
        ],
        "total_assets": sum(acc["balance"] for acc in accounts) + sum(inv["current_value"] for inv in investments),
        "total_insurance_coverage": sum(ins["coverage_amount"] for ins in insurance_policies)
    }
    
    return summary

@router.get("/export-pdf")
async def export_emergency_vault_pdf(current_user: dict = Depends(get_current_user)):
    """Export emergency vault as PDF"""
    user_id = current_user["user_id"]
    
    # Get summary data
    summary_response = await generate_emergency_summary(current_user)
    
    # Create PDF
    pdf_dir = "./uploads/pdfs"
    os.makedirs(pdf_dir, exist_ok=True)
    
    pdf_path = os.path.join(pdf_dir, f"emergency_vault_{user_id}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 750, "Emergency Financial Vault")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Owner: {summary_response['user']['name']}")
    c.drawString(100, 700, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    
    # Summary
    y = 660
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "Financial Summary")
    
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(100, y, f"Total Assets: ₹{summary_response['total_assets']:,.2f}")
    y -= 20
    c.drawString(100, y, f"Insurance Coverage: ₹{summary_response['total_insurance_coverage']:,.2f}")
    
    # Accounts
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "Bank Accounts")
    y -= 25
    c.setFont("Helvetica", 10)
    for acc in summary_response['accounts']:
        c.drawString(100, y, f"{acc['institution']} - {acc['type']}: ₹{acc['balance']:,.2f} (Nominee: {acc['nominee']})")
        y -= 15
        if y < 100:
            c.showPage()
            y = 750
    
    # Insurance
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "Insurance Policies")
    y -= 25
    c.setFont("Helvetica", 10)
    for ins in summary_response['insurance']:
        c.drawString(100, y, f"{ins['provider']} - {ins['type']}: ₹{ins['coverage']:,.2f}")
        y -= 15
        if y < 100:
            c.showPage()
            y = 750
    
    c.save()
    
    log_audit(current_user["user_id"], "EXPORT", "emergency_vault_pdf", {"path": pdf_path})
    
    return {
        "message": "PDF generated successfully",
        "path": pdf_path,
        "download_url": f"/api/emergency/download-pdf/{user_id}"
    }