from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from routes import auth, accounts, investments, expenses, loans, insurance, documents, analytics, emergency, goals, recommendations
from database import db

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Financial Life Vault API...")
    yield
    # Shutdown
    print("👋 Shutting down Financial Life Vault API...")

app = FastAPI(
    title="Financial Life Vault API",
    description="Secure estate planning + personal finance management platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Financial Life Vault API"
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(investments.router, prefix="/api/investments", tags=["Investments"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["Expenses"])
app.include_router(loans.router, prefix="/api/loans", tags=["Loans"])
app.include_router(insurance.router, prefix="/api/insurance", tags=["Insurance"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(emergency.router, prefix="/api/emergency", tags=["Emergency Vault"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)