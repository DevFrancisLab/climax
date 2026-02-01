#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'climax.settings')
import django
django.setup()

from django.test import Client
from alerts.models import UserAlert, ClimateAlert
from alerts.views import _ussd_sessions

# Clean up and create test data
_ussd_sessions.clear()
UserAlert.objects.filter(phone_number='0700555555').delete()
ClimateAlert.objects.filter(county='nairobi').delete()

client = Client()
SESSION = 'risk-status-test-001'
PHONE = '0700555555'

print('\n' + '='*70)
print('TEST: Check Risk Status Flow')
print('='*70)

# Step 1: Register user for Nairobi
print('\n[Step 1] Register user for Nairobi')
r = client.post('/alerts/ussd', {'sessionId': SESSION, 'phoneNumber': PHONE, 'text': ''})
print('Language selection:', r.content.decode()[:50])

r = client.post('/alerts/ussd', {'sessionId': SESSION, 'phoneNumber': PHONE, 'text': '1'})
print('Main menu:', r.content.decode()[:50])

r = client.post('/alerts/ussd', {'sessionId': SESSION, 'phoneNumber': PHONE, 'text': '1'})
print('County menu:', r.content.decode()[:50])

r = client.post('/alerts/ussd', {'sessionId': SESSION, 'phoneNumber': PHONE, 'text': '7'})  # Nairobi
print('Registration response:', r.content.decode()[:70])

# Verify user is registered
user = UserAlert.objects.get(phone_number=PHONE)
print(f'✓ User registered: {user.phone_number} for {user.county}')

# Step 2: Create an approved alert for Nairobi
print('\n[Step 2] Create approved alert for Nairobi')
alert = ClimateAlert.objects.create(
    county='nairobi',
    risk_type='flood',
    risk_level='high',
    message='Heavy rainfall expected in Nairobi next 48 hours. Avoid low-lying areas.',
    suggested_message='(Auto-generated)',
    approved=True
)
print(f'✓ Alert created: {alert.message[:60]}...')

# Step 3: Check risk status (should show alert)
print('\n[Step 3] Check risk status (with alert)')
_ussd_sessions.clear()  # Clear to start fresh session
SESSION2 = 'risk-status-test-002'

r = client.post('/alerts/ussd', {'sessionId': SESSION2, 'phoneNumber': PHONE, 'text': ''})
print('Language selection')

r = client.post('/alerts/ussd', {'sessionId': SESSION2, 'phoneNumber': PHONE, 'text': '1'})
print('Main menu')

r = client.post('/alerts/ussd', {'sessionId': SESSION2, 'phoneNumber': PHONE, 'text': '2'})  # Check risk status
response = r.content.decode()
print('Risk status response:')
print(response)

if 'Heavy rainfall' in response:
    print('✓ PASS: Alert message is displayed')
else:
    print('✗ FAIL: Alert message NOT found')
    
if response.startswith('CON'):
    print('✓ PASS: Response starts with CON (continue), user can go back')
else:
    print('⚠ WARNING: Response does not start with CON')

# Step 4: Go back to menu from risk status
print('\n[Step 4] Go back to menu (press 1)')
r = client.post('/alerts/ussd', {'sessionId': SESSION2, 'phoneNumber': PHONE, 'text': '1'})
response = r.content.decode()
print('Back to menu response:')
print(response[:100])

if 'Climate Alert System' in response:
    print('✓ PASS: Returned to main menu')
else:
    print('✗ FAIL: Did not return to main menu')

# Step 5: Check risk status when NO alerts exist
print('\n[Step 5] Check risk status (no alerts)')
ClimateAlert.objects.filter(county='nairobi').delete()

r = client.post('/alerts/ussd', {'sessionId': SESSION2, 'phoneNumber': PHONE, 'text': '2'})  # Check risk status again
response = r.content.decode()
print('Risk status response (no alerts):')
print(response)

if 'No current alerts' in response:
    print('✓ PASS: No alerts message shown')
else:
    print('⚠ WARNING: No alerts message not found')

if response.startswith('END'):
    print('✓ PASS: Response ends flow (END) when no alerts')
else:
    print('⚠ WARNING: Response should END when no alerts')

print('\n' + '='*70)
print('Risk Status Tests Complete')
print('='*70 + '\n')
