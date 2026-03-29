# Troubleshooting Guide - Financial Life Vault

## Registration & Login Issues

### ✅ FIXES APPLIED

1. **Fixed auth endpoint dependency error**
   - Issue: `/api/auth/me` was throwing AttributeError
   - Fix: Corrected the Depends() usage in auth.py
   - Status: ✅ FIXED

2. **Fixed refresh token endpoint**
   - Issue: Refresh endpoint expected different data format
   - Fix: Updated to accept JSON body with refresh_token
   - Status: ✅ FIXED

3. **CORS Configuration**
   - Status: ✅ Working (allow-origin: *)
   - Backend accepts requests from any origin

### 🧪 Verified Working

- ✅ Backend API on port 8001
- ✅ Frontend on port 3000
- ✅ User registration endpoint
- ✅ User login endpoint  
- ✅ CORS headers
- ✅ JWT token generation

### 📋 Test Credentials

**Demo Account:**
- Email: `demo@financialvault.com`
- Password: `demo123456`

**Test Account:**
- Email: `test@example.com`
- Password: `testpass123`

### 🔍 How to Test

1. **Open browser console** (F12)
2. Go to http://localhost:3000
3. Try to register/login
4. **Check console for errors**

### Common Issues & Solutions

#### Issue: "Network Error" or "Failed to fetch"

**Solution:**
- Backend might not be accessible
- Check: `curl http://localhost:8001/api/health`
- Restart backend: `sudo supervisorctl restart backend`

#### Issue: "CORS Error"

**Solution:**
- CORS is configured to allow all origins (*)
- If still seeing errors, check browser console for specific message

#### Issue: "401 Unauthorized"

**Solution:**
- Token might be expired or invalid
- Clear browser localStorage
- Try logging in again

#### Issue: Login succeeds but redirects to login

**Solution:**
- Check if token is being saved in localStorage
- Open browser console → Application → Local Storage
- Should see `access_token` and `refresh_token`

### 🔧 Manual API Testing

Test registration via command line:
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "yourpassword",
    "full_name": "Your Name",
    "role": "owner"
  }'
```

Test login:
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@financialvault.com",
    "password": "demo123456"
  }'
```

### 📊 Check Service Status

```bash
sudo supervisorctl status
```

Both backend and frontend should show RUNNING

### 🔄 Restart Services

```bash
# Restart everything
sudo supervisorctl restart all

# Or individual services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

### 📝 Check Logs

Backend errors:
```bash
tail -50 /var/log/supervisor/backend.err.log
```

Frontend errors:
```bash
tail -50 /var/log/supervisor/frontend.err.log
```

---

## Still Not Working?

If registration/login still doesn't work:

1. **Clear browser cache and localStorage**
2. **Try in incognito/private mode**
3. **Check browser console** for specific error messages
4. **Verify backend is responding**:
   ```bash
   curl http://localhost:8001/api/health
   ```

If backend health check fails, restart it:
```bash
sudo supervisorctl restart backend
```
