# Financial Life Vault 🏦

A comprehensive **estate planning + personal finance management platform** that acts as your personal CFO, net worth tracker, insurance vault, and emergency recovery system.

## 🎯 Overview

Financial Life Vault is a production-ready web application that combines the functionality of:
- **Personal CFO** - Complete financial oversight
- **Net Worth Tracker** - Real-time asset & liability monitoring  
- **Insurance Vault** - Policy management & adequacy checks
- **Emergency Recovery System** - Family access & instructions
- **Investment Tracker** - Portfolio analytics & performance
- **Expense Manager** - Smart categorization & insights

---

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **Authentication**: JWT + Refresh Tokens
- **Security**: bcrypt password hashing + field-level encryption
- **OCR**: pytesseract for document text extraction

### Frontend
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Routing**: React Router v6
- **Charts**: Recharts
- **Icons**: Lucide React
- **Notifications**: React Hot Toast

---

## ✨ Core Features

### 1. Authentication & Security 🔐
- JWT-based authentication with refresh tokens
- Role-based access control (Owner/Family Member)
- Secure password hashing with bcrypt
- Field-level encryption for sensitive data (account numbers)
- Audit logging for all critical actions

### 2. Financial Accounts 💳
- Track bank accounts, demat, UPI, credit cards
- Encrypted account number storage
- Real-time balance tracking
- Nominee mapping for each account
- Full CRUD operations

### 3. Investments Module 📈
- Support for mutual funds, stocks, P2P lending, gold
- SIP (Systematic Investment Plan) management
- Automatic gain/loss calculation
- Portfolio analytics & allocation
- Platform-wise tracking (Groww, Zerodha, etc.)

### 4. Expense Tracking 💰
- Smart categorization (Needs/Wants/Investments)
- 50-30-20 budget rule compliance
- Monthly trend analysis
- Subcategory support
- CSV import ready

### 5. Loans & Liabilities 💸
- EMI tracking
- Interest calculation
- Remaining tenure monitoring
- Multiple loan type support

### 6. Insurance Management 🛡️
- Health, term, vehicle, home insurance
- Renewal date tracking with alerts
- Coverage adequacy analysis
- Nominee assignment
- Claim instructions storage

### 7. Document Vault 📄 (ADVANCED)
- **OCR-powered** text extraction from images
- **Auto-classification** into 6 categories:
  - Identity (Aadhaar, PAN, Passport, etc.)
  - Insurance
  - Investments
  - Loans
  - Property
  - Other
- **Auto-naming** with timestamps
- **Full-text search** across all documents
- Secure file storage

### 8. Analytics Engine 📊
- **Net Worth Calculation**: Assets - Liabilities
- **Portfolio Allocation**: Equity/Debt/Gold breakdown with charts
- **Emergency Fund Check**: 6-12 months expense coverage
- **Insurance Adequacy**: Term & health insurance analysis
- **Financial Health Score**: 0-100 rating based on:
  - Savings rate
  - Insurance coverage
  - Debt ratio
  - Emergency fund
- **Risk Score**: Portfolio & debt concentration analysis
- **Expense Analysis**: Category-wise spending patterns

### 9. Goals & Retirement Planner 🎯
- Goal tracking with progress indicators
- Target amount & date management
- **Retirement Calculator**:
  - Inflation-adjusted corpus calculation
  - 4% safe withdrawal rate
  - Recommended monthly SIP

### 10. Emergency Vault 🚨 (CRITICAL)
- Emergency instructions for family
- "If something happens to me" guide
- Asset summary generation
- Nominee management
- **PDF Export** of complete financial overview
- Family member restricted access
- Emergency contact storage

### 11. Smart Recommendations 💡
- **Rule-based recommendation engine** (Active):
  - Emergency fund suggestions
  - Insurance gap analysis
  - Debt management advice
  - Portfolio diversification tips
  - Savings rate optimization
  - Budget allocation (50-30-20 rule)
- **AI-ready architecture** for GPT-5.2/Gemini integration
- Priority-based recommendations (High/Medium/Low)
- Actionable insights with impact analysis

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB
- Tesseract OCR

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd financial-life-vault
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
yarn install
```

4. **Environment Configuration**

Backend `.env`:
```
MONGO_URL=mongodb://localhost:27017/financial_vault
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=your-encryption-key-32-bytes
```

Frontend `.env`:
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

5. **Run the Application**

Using Supervisor (Recommended):
```bash
sudo supervisorctl start all
```

Manual:
```bash
# Terminal 1 - Backend
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend
cd frontend
yarn start
```

6. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Documentation: http://localhost:8001/docs

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

### Accounts
- `GET /api/accounts` - List all accounts
- `POST /api/accounts` - Create account
- `PUT /api/accounts/{id}` - Update account
- `DELETE /api/accounts/{id}` - Delete account

### Investments
- `GET /api/investments` - List investments
- `POST /api/investments` - Add investment
- `PUT /api/investments/{id}` - Update investment
- `GET /api/investments/sips` - List SIPs

### Analytics
- `GET /api/analytics/net-worth` - Calculate net worth
- `GET /api/analytics/portfolio-allocation` - Portfolio breakdown
- `GET /api/analytics/emergency-fund-check` - Emergency fund status
- `GET /api/analytics/insurance-check` - Insurance adequacy
- `GET /api/analytics/financial-health-score` - Health score (0-100)
- `GET /api/analytics/risk-score` - Risk analysis
- `GET /api/analytics/expense-analysis` - Expense patterns

### Recommendations
- `GET /api/recommendations` - Get personalized recommendations
- `GET /api/recommendations/salary-allocation` - 50-30-20 allocation

### Emergency Vault
- `POST /api/emergency/nominees` - Add nominee
- `GET /api/emergency/generate-summary` - Asset summary
- `GET /api/emergency/export-pdf` - Export to PDF

... and 40+ more endpoints!

---

## 🔒 Security Features

1. **Authentication**
   - JWT tokens with secure expiration
   - Refresh token rotation
   - Password hashing with bcrypt

2. **Data Protection**
   - Field-level encryption for account numbers
   - Secure file storage
   - Environment-based secrets

3. **Access Control**
   - Role-based permissions
   - User-specific data isolation
   - Audit logging

4. **Database Security**
   - Query optimization with projections
   - Pagination limits to prevent DoS
   - Input validation

---

## 🎨 UI Features

- **Responsive Design**: Mobile, tablet, desktop optimized
- **Modern UI**: Clean, intuitive interface with Tailwind CSS
- **Interactive Charts**: Portfolio visualization with Recharts
- **Real-time Updates**: Live data refresh
- **Loading States**: Smooth user experience
- **Toast Notifications**: User feedback on actions
- **Modal Forms**: Easy data entry
- **Color-coded Categories**: Visual distinction

---

## 📊 Performance Optimizations

✅ All database queries optimized with:
- Field projections (fetch only needed fields)
- `.limit()` constraints on all queries
- Indexed fields (user_id, timestamps)

✅ Frontend optimizations:
- Code splitting
- Lazy loading
- Optimized re-renders

---

## 🔧 Configuration

### Enable AI Recommendations

Update `backend/.env`:
```
AI_ENABLED=true
AI_PROVIDER=openai  # or gemini
OPENAI_API_KEY=your-key-here
# OR
GEMINI_API_KEY=your-key-here
```

The system will automatically use AI for enhanced recommendations.

---

## 🧪 Testing

### Backend Health Check
```bash
curl http://localhost:8001/api/health
```

### Create Test User
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure123",
    "full_name": "John Doe",
    "role": "owner"
  }'
```

---

## 📈 Roadmap

- [ ] Mobile app (React Native)
- [ ] Multi-currency support
- [ ] Tax planning module
- [ ] Will & estate planning
- [ ] Family sharing features
- [ ] Bank statement import (PDF/CSV)
- [ ] Auto-sync with platforms
- [ ] Email/SMS notifications
- [ ] Two-factor authentication
- [ ] Biometric access

---

## 🤝 Contributing

This is a private financial management system. For inquiries, please contact the repository owner.

---

## 📄 License

Proprietary - All rights reserved

---

## 👤 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review backend logs: `/var/log/supervisor/backend.*.log`
3. Review frontend logs: `/var/log/supervisor/frontend.*.log`

---

## 🎉 Acknowledgments

Built with modern web technologies:
- FastAPI
- React
- MongoDB
- Tailwind CSS
- And many more amazing open-source libraries

---

**Financial Life Vault** - Your Complete Financial Life, Secured. 🏦✨
