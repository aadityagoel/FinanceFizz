from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.finance import AccountCreate, AccountUpdate, AccountResponse
from database import accounts_collection
from utils.dependencies import get_current_user
from utils.helpers import generate_id, log_audit
from utils.encryption import encrypt_data, decrypt_data, mask_account_number
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(account: AccountCreate, current_user: dict = Depends(get_current_user)):
    """Create a new financial account"""
    account_id = generate_id("acc_")
    
    # Encrypt account number
    encrypted_account_number = encrypt_data(account.account_number)
    
    account_doc = {
        "account_id": account_id,
        "user_id": current_user["user_id"],
        "institution_name": account.institution_name,
        "account_type": account.account_type,
        "account_number": encrypted_account_number,
        "balance": account.balance,
        "nominee_id": account.nominee_id,
        "notes": account.notes,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    accounts_collection.insert_one(account_doc)
    log_audit(current_user["user_id"], "CREATE", "account", {"account_id": account_id})
    
    # Prepare response with masked account number
    decrypted_number = decrypt_data(encrypted_account_number)
    return {
        **account.dict(),
        "account_id": account_id,
        "user_id": current_user["user_id"],
        "account_number_masked": mask_account_number(decrypted_number),
        "created_at": account_doc["created_at"],
        "updated_at": account_doc["updated_at"]
    }

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(current_user: dict = Depends(get_current_user)):
    """Get all accounts for current user"""
    accounts = list(accounts_collection.find({"user_id": current_user["user_id"]}))
    
    result = []
    for acc in accounts:
        decrypted_number = decrypt_data(acc["account_number"])
        result.append({
            "account_id": acc["account_id"],
            "user_id": acc["user_id"],
            "institution_name": acc["institution_name"],
            "account_type": acc["account_type"],
            "account_number": acc["account_number"],
            "account_number_masked": mask_account_number(decrypted_number),
            "balance": acc["balance"],
            "nominee_id": acc.get("nominee_id"),
            "notes": acc.get("notes"),
            "created_at": acc["created_at"],
            "updated_at": acc["updated_at"]
        })
    
    return result

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific account"""
    account = accounts_collection.find_one({
        "account_id": account_id,
        "user_id": current_user["user_id"]
    })
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    decrypted_number = decrypt_data(account["account_number"])
    return {
        "account_id": account["account_id"],
        "user_id": account["user_id"],
        "institution_name": account["institution_name"],
        "account_type": account["account_type"],
        "account_number": account["account_number"],
        "account_number_masked": mask_account_number(decrypted_number),
        "balance": account["balance"],
        "nominee_id": account.get("nominee_id"),
        "notes": account.get("notes"),
        "created_at": account["created_at"],
        "updated_at": account["updated_at"]
    }

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(account_id: str, account_update: AccountUpdate, current_user: dict = Depends(get_current_user)):
    """Update account"""
    account = accounts_collection.find_one({
        "account_id": account_id,
        "user_id": current_user["user_id"]
    })
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    update_data = {k: v for k, v in account_update.dict(exclude_unset=True).items()}
    update_data["updated_at"] = datetime.utcnow()
    
    accounts_collection.update_one(
        {"account_id": account_id},
        {"$set": update_data}
    )
    
    log_audit(current_user["user_id"], "UPDATE", "account", {"account_id": account_id})
    
    updated_account = accounts_collection.find_one({"account_id": account_id})
    decrypted_number = decrypt_data(updated_account["account_number"])
    
    return {
        "account_id": updated_account["account_id"],
        "user_id": updated_account["user_id"],
        "institution_name": updated_account["institution_name"],
        "account_type": updated_account["account_type"],
        "account_number": updated_account["account_number"],
        "account_number_masked": mask_account_number(decrypted_number),
        "balance": updated_account["balance"],
        "nominee_id": updated_account.get("nominee_id"),
        "notes": updated_account.get("notes"),
        "created_at": updated_account["created_at"],
        "updated_at": updated_account["updated_at"]
    }

@router.delete("/{account_id}")
async def delete_account(account_id: str, current_user: dict = Depends(get_current_user)):
    """Delete account"""
    result = accounts_collection.delete_one({
        "account_id": account_id,
        "user_id": current_user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    
    log_audit(current_user["user_id"], "DELETE", "account", {"account_id": account_id})
    
    return {"message": "Account deleted successfully"}