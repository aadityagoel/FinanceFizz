from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
import os
import shutil
from models.vault import DocumentResponse
from database import documents_collection
from utils.dependencies import get_current_user
from utils.helpers import generate_id, log_audit
from datetime import datetime
import pytesseract
from PIL import Image
import io

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def classify_document(filename: str, extracted_text: str = "") -> str:
    """Auto-classify document based on filename and content"""
    filename_lower = filename.lower()
    text_lower = extracted_text.lower()
    
    # Identity documents
    if any(word in filename_lower or word in text_lower for word in ["aadhaar", "aadhar", "pan", "passport", "license", "voter"]):
        return "identity"
    
    # Insurance documents
    if any(word in filename_lower or word in text_lower for word in ["insurance", "policy", "health", "term", "premium"]):
        return "insurance"
    
    # Investment documents
    if any(word in filename_lower or word in text_lower for word in ["mutual fund", "stock", "demat", "investment", "portfolio"]):
        return "investments"
    
    # Loan documents
    if any(word in filename_lower or word in text_lower for word in ["loan", "emi", "mortgage", "credit"]):
        return "loans"
    
    # Property documents
    if any(word in filename_lower or word in text_lower for word in ["property", "deed", "registry", "sale"]):
        return "property"
    
    return "other"

def extract_text_from_image(file_path: str) -> str:
    """Extract text from image using OCR"""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    description: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Upload a document with auto-classification and OCR"""
    document_id = generate_id("doc_")
    
    # Create user-specific directory
    user_dir = os.path.join(UPLOAD_DIR, current_user["user_id"])
    os.makedirs(user_dir, exist_ok=True)
    
    # Save file
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(user_dir, f"{document_id}{file_extension}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extract text if image
    extracted_text = ""
    if file.content_type and file.content_type.startswith("image/"):
        extracted_text = extract_text_from_image(file_path)
    
    # Auto-classify
    category = classify_document(file.filename, extracted_text)
    
    # Auto-generate filename
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    auto_filename = f"{category.title()}_{timestamp}{file_extension}"
    
    document_doc = {
        "document_id": document_id,
        "user_id": current_user["user_id"],
        "filename": auto_filename,
        "original_filename": file.filename,
        "category": category,
        "tags": [category],
        "description": description or "",
        "extracted_text": extracted_text,
        "file_path": file_path,
        "file_size": os.path.getsize(file_path),
        "mime_type": file.content_type,
        "uploaded_at": datetime.utcnow()
    }
    
    documents_collection.insert_one(document_doc)
    log_audit(current_user["user_id"], "UPLOAD", "document", {"document_id": document_id, "category": category})
    
    return document_doc

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(category: str = None, current_user: dict = Depends(get_current_user)):
    """Get all documents, optionally filtered by category"""
    query = {"user_id": current_user["user_id"]}
    if category:
        query["category"] = category
    
    documents = list(documents_collection.find(
        query,
        {"_id": 0}
    ).sort("uploaded_at", -1).limit(100))
    return documents

@router.get("/search")
async def search_documents(q: str, current_user: dict = Depends(get_current_user)):
    """Search documents by text"""
    documents = list(documents_collection.find({
        "user_id": current_user["user_id"],
        "$or": [
            {"filename": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"extracted_text": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}}
        ]
    }, {"_id": 0}).limit(50))
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific document"""
    document = documents_collection.find_one({
        "document_id": document_id,
        "user_id": current_user["user_id"]
    })
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Delete document"""
    document = documents_collection.find_one({
        "document_id": document_id,
        "user_id": current_user["user_id"]
    })
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file
    if os.path.exists(document["file_path"]):
        os.remove(document["file_path"])
    
    # Delete from database
    documents_collection.delete_one({"document_id": document_id})
    log_audit(current_user["user_id"], "DELETE", "document", {"document_id": document_id})
    
    return {"message": "Document deleted successfully"}