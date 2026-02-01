# Africa's Talking Integration Setup Guide

## Current Configuration

### ✅ Credentials
- **Username**: `sandbox` (configured in `.env` as `AT_USERNAME`)
- **API Key**: Configured in `.env` as `AT_API_KEY`
- **Sender ID**: `CLIMAX`

### ✅ USSD Callback URL
- **Production URL**: `https://055f33e82726.ngrok-free.app/ussd`
- **Endpoint Method**: POST
- **Request Parameters**: `sessionId`, `phoneNumber`, `text`
- **Response Format**: Plain text with `CON` or `END` prefix

## Steps to Configure in Africa's Talking Dashboard

### 1. Log into Africa's Talking Sandbox
```
URL: https://africastalking.com/
Username: Your AT username
```

### 2. Navigate to USSD Settings
```
Dashboard → Settings → USSD → Callback URL
```

### 3. Enter Callback URL
```
https://055f33e82726.ngrok-free.app/ussd
```

### 4. Configure USSD Code
```
Short Code: *130*1#  (or any available code)
Type: Session-based (STK Push)
```

### 5. Test Callback
Africa's Talking will send a test request to verify the endpoint is responding:
```
POST /ussd
Parameters:
  - sessionId: test
  - phoneNumber: +254700000000
  - text: (empty for initial)
```

Expected Response:
```
CON Select Language:
1. English
2. Kiswahili
```

## API Implementation Details

### Request Format
Africa's Talking sends POST requests with form data:
```
POST https://055f33e82726.ngrok-free.app/ussd HTTP/1.1
Content-Type: application/x-www-form-urlencoded

sessionId=550e8400-e29b-41d4-a716-446655440000&
phoneNumber=254700000000&
text=
```

### Response Format
- **Continue Session** (show more options):
  ```
  CON Climate Alert System
  1. Register for alerts
  2. Check risk status
  3. Unsubscribe
  ```

- **End Session** (final response):
  ```
  END You are registered for Nairobi alerts.
  You will receive SMS updates.
  ```

## USSD Flow with Africa's Talking Integration

```
User dials: *130*1#
    ↓
Africa's Talking → POST /ussd
  sessionId: unique_id
  phoneNumber: 254700000000
  text: ""
    ↓
Server responds:
  CON Select Language:
  1. English
  2. Kiswahili
    ↓
User selects: 2 (Swahili)
    ↓
Africa's Talking → POST /ussd
  sessionId: unique_id (same)
  phoneNumber: 254700000000
  text: "2"
    ↓
Server responds:
  CON Mfumo wa Onyo wa Tabia Nchi
  1. Jisajili kwa onyo
  2. Angalia hali ya hatari
  3. Sitisha
    ↓
User completes flow...
    ↓
Server responds:
  END Umejisajili kwa onyo za Nairobi.
  Utapokea ujumbe wa SMS.
```

## SMS Integration

### SMS Confirmation
When users register, they receive SMS confirmation:
```python
AfricasTalkingService.send_sms(
    phone_number='254700000000',
    message='Welcome to Climate Alert System. You are registered for Nairobi alerts.'
)
```

### Sent via Africa's Talking SMS Service
Uses the same API key configured in `.env`

## Testing the Integration

### Option 1: Via Africa's Talking Sandbox
1. Log into Africa's Talking dashboard
2. Use "Test Callback" feature
3. Simulate USSD session

### Option 2: Via cURL (Local Testing)
```bash
curl -X POST https://055f33e82726.ngrok-free.app/ussd \
  -d "sessionId=test123" \
  -d "phoneNumber=254700000000" \
  -d "text="
```

### Option 3: Via Africa's Talking Simulator
1. Go to Dashboard → USSD → Simulator
2. Enter USSD code: `*130*1#`
3. Select phone number from dropdown
4. Follow the menu flow

## Production Deployment

### Before Going Live

1. **Replace ngrok with production URL**
   ```
   Update in Africa's Talking Dashboard:
   OLD: https://055f33e82726.ngrok-free.app/ussd
   NEW: https://yourdomain.com/alerts/ussd
   ```

2. **Switch from Sandbox to Live**
   ```
   Africa's Talking Dashboard → Settings → Switch to Live
   ```

3. **Update Production Credentials**
   ```
   .env:
   AT_USERNAME=your_live_username
   AT_API_KEY=your_live_api_key
   ```

4. **Configure Real USSD Code**
   ```
   Work with AT support to provision USSD short code
   ```

5. **Test End-to-End**
   - Register users on live Africa's Talking
   - Send SMS confirmations
   - Verify user data in production database

### Session Storage Recommendation

Current implementation uses in-memory session storage:
```python
_ussd_sessions = {}  # In /home/frank/climax/alerts/views.py
```

For production with multiple servers, replace with Redis:
```python
import redis
cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Store session
cache.setex(f"ussd:{phone_number}", 3600, json.dumps(session_data))

# Retrieve session
session_data = json.loads(cache.get(f"ussd:{phone_number}"))
```

## Troubleshooting

### Issue: "Callback URL unreachable"
**Solution**: 
- Verify ngrok tunnel is running: `ngrok http 8000`
- Check if server is running: `python manage.py runserver`
- Verify firewall allows inbound HTTPS

### Issue: "Invalid phone number"
**Solution**:
- Ensure phone numbers include country code (e.g., 254700000000)
- No plus sign in Africa's Talking requests (just digits)

### Issue: "Session state lost between requests"
**Solution**:
- Migrate to Redis for distributed session storage
- Or ensure same server handles all requests from a user

### Issue: "SMS not sending"
**Solution**:
- Verify SMS balance in Africa's Talking account
- Check API credentials in `.env`
- Verify `SENDER_ID` is whitelisted

## Monitoring & Logging

### View USSD Requests
```python
# Add to alerts/views.py
import logging
logger = logging.getLogger(__name__)

@csrf_exempt
def ussd_callback(request):
    logger.info(f"USSD Request: phone={phone_number}, text={text}")
    # ... handler code ...
    logger.info(f"USSD Response: {response}")
```

### Monitor Africa's Talking Dashboard
1. Dashboard → Analytics → USSD
2. View:
   - Number of sessions
   - Average session duration
   - Success rate
   - Error messages

## Contact & Support

- **Africa's Talking Support**: support@africastalking.com
- **Documentation**: https://africastalking.com/ussd
- **API Reference**: https://africastalking.com/ussd/docs

---

**Status**: ✅ Ready for Africa's Talking Integration
**Callback URL**: https://055f33e82726.ngrok-free.app/ussd
**Last Updated**: January 30, 2026
