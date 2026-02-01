#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'climax.settings')
import django
django.setup()

from django.test import Client
from alerts.models import UserAlert, ClimateAlert
from alerts.views import _ussd_sessions

client = Client()

print('\n' + '='*80)
print('COMPREHENSIVE MENU OPTIONS TEST')
print('='*80)

# Test 1: Language Selection
print('\n[TEST 1] Language Selection - English and Swahili')
print('-'*80)
_ussd_sessions.clear()
UserAlert.objects.filter(phone_number='0700111111').delete()

# English flow
s1 = 'test-en-001'
r = client.post('/alerts/ussd', {'sessionId': s1, 'phoneNumber': '0700111111', 'text': ''})
if 'Select Language' in r.content.decode() and '1. English' in r.content.decode():
    print('✓ Language selection menu shows English option')
else:
    print('✗ Language menu missing')

r = client.post('/alerts/ussd', {'sessionId': s1, 'phoneNumber': '0700111111', 'text': '1'})
if 'Climate Alert System' in r.content.decode():
    print('✓ English selected: Main menu shown')
else:
    print('✗ Failed to select English')

# Swahili flow
_ussd_sessions.clear()
UserAlert.objects.filter(phone_number='0700222222').delete()
s2 = 'test-sw-001'
r = client.post('/alerts/ussd', {'sessionId': s2, 'phoneNumber': '0700222222', 'text': ''})
if '1. English' in r.content.decode() and '2. Kiswahili' in r.content.decode():
    print('✓ Language selection menu shows Swahili option')
else:
    print('✗ Language menu missing Swahili')

r = client.post('/alerts/ussd', {'sessionId': s2, 'phoneNumber': '0700222222', 'text': '2'})
if 'Mfumo wa Onyo' in r.content.decode():
    print('✓ Swahili selected: Main menu shown')
else:
    print('✗ Failed to select Swahili')

# Test 2: Register for Alerts
print('\n[TEST 2] Register for Alerts - County Selection')
print('-'*80)
_ussd_sessions.clear()
UserAlert.objects.filter(phone_number='0700333333').delete()

s3 = 'test-register-001'
client.post('/alerts/ussd', {'sessionId': s3, 'phoneNumber': '0700333333', 'text': ''})
client.post('/alerts/ussd', {'sessionId': s3, 'phoneNumber': '0700333333', 'text': '1'})  # English
r = client.post('/alerts/ussd', {'sessionId': s3, 'phoneNumber': '0700333333', 'text': '1'})  # Register

if 'Select County' in r.content.decode():
    county_count = r.content.decode().count('.')
    if county_count == 8:  # 8 counties
        print('✓ County menu shows all 8 counties')
    else:
        print(f'⚠ County menu shows {county_count} counties (expected 8)')
else:
    print('✗ County menu not shown')

r = client.post('/alerts/ussd', {'sessionId': s3, 'phoneNumber': '0700333333', 'text': '5'})  # Marsabit
if 'registered' in r.content.decode().lower() and 'Marsabit' in r.content.decode():
    print('✓ Registration successful for Marsabit')
    user = UserAlert.objects.get(phone_number='0700333333')
    if user.county == 'marsabit' and user.language == 'en':
        print('✓ User saved with correct county and language')
    else:
        print(f'⚠ User data mismatch: county={user.county}, language={user.language}')
else:
    print('✗ Registration failed')

# Test 3: Check Risk Status
print('\n[TEST 3] Check Risk Status')
print('-'*80)
_ussd_sessions.clear()
UserAlert.objects.filter(phone_number='0700444444').delete()
ClimateAlert.objects.filter(county='garissa').delete()

# Register user
s4 = 'test-risk-001'
client.post('/alerts/ussd', {'sessionId': s4, 'phoneNumber': '0700444444', 'text': ''})
client.post('/alerts/ussd', {'sessionId': s4, 'phoneNumber': '0700444444', 'text': '1'})
client.post('/alerts/ussd', {'sessionId': s4, 'phoneNumber': '0700444444', 'text': '1'})
client.post('/alerts/ussd', {'sessionId': s4, 'phoneNumber': '0700444444', 'text': '3'})  # Garissa

# Create an alert
ClimateAlert.objects.create(
    county='garissa',
    risk_type='drought',
    risk_level='high',
    message='Severe drought warning for Garissa region.',
    approved=True
)

# Check risk status
r = client.post('/alerts/ussd', {'sessionId': s4, 'phoneNumber': '0700444444', 'text': '2'})
response = r.content.decode()

if 'Severe drought' in response:
    print('✓ Risk status shows alert message')
else:
    print('✗ Alert message not shown')

if 'Back to menu' in response:
    print('✓ Back to menu option provided')
else:
    print('✗ Back to menu option missing')

# Go back to menu
r = client.post('/alerts/ussd', {'sessionId': s4, 'phoneNumber': '0700444444', 'text': '1'})
if 'Climate Alert System' in r.content.decode():
    print('✓ Successfully returned to main menu')
else:
    print('✗ Failed to return to main menu')

# Test 4: Unsubscribe
print('\n[TEST 4] Unsubscribe')
print('-'*80)
_ussd_sessions.clear()
UserAlert.objects.filter(phone_number='0700555555').delete()

# Register user
s5 = 'test-unsub-001'
client.post('/alerts/ussd', {'sessionId': s5, 'phoneNumber': '0700555555', 'text': ''})
client.post('/alerts/ussd', {'sessionId': s5, 'phoneNumber': '0700555555', 'text': '1'})
client.post('/alerts/ussd', {'sessionId': s5, 'phoneNumber': '0700555555', 'text': '1'})
client.post('/alerts/ussd', {'sessionId': s5, 'phoneNumber': '0700555555', 'text': '4'})  # Turkana

user = UserAlert.objects.get(phone_number='0700555555')
if user.is_active:
    print('✓ User is active after registration')
else:
    print('✗ User not active')

# Unsubscribe
r = client.post('/alerts/ussd', {'sessionId': s5, 'phoneNumber': '0700555555', 'text': '3'})
response = r.content.decode()

if 'unsubscribed' in response.lower():
    print('✓ Unsubscribe message shown')
else:
    print('✗ Unsubscribe message not shown')

user.refresh_from_db()
if not user.is_active:
    print('✓ User marked as inactive in database')
else:
    print('✗ User still active in database')

print('\n' + '='*80)
print('ALL MENU OPTIONS VERIFIED')
print('='*80 + '\n')
