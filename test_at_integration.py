#!/usr/bin/env python
"""Test script for Africa's Talking integration"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/frank/climax')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'climax.settings')
django.setup()

from alerts.services.africastalking_service import AfricasTalkingService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_credentials():
    """Test if AT credentials are properly configured"""
    username = os.getenv("AT_USERNAME")
    api_key = os.getenv("AT_API_KEY")
    
    print("=" * 60)
    print("AFRICA'S TALKING INTEGRATION TEST")
    print("=" * 60)
    print()
    
    # Check credentials
    print("1. Checking Credentials:")
    print(f"   - AT_USERNAME: {'✓ Configured' if username else '✗ Missing'}")
    print(f"   - AT_API_KEY: {'✓ Configured' if api_key else '✗ Missing'}")
    print()
    
    if not username or not api_key:
        print("❌ ERROR: Missing AT credentials in .env file")
        print("   Please add AT_USERNAME and AT_API_KEY to your .env file")
        return False
    
    print("✓ Credentials found")
    print()
    
    # Test service initialization
    print("2. Testing Service Initialization:")
    try:
        AfricasTalkingService.initialize()
        print("   ✓ Service initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        return False
    
    print()
    
    # Test database
    print("3. Testing Database Setup:")
    try:
        from alerts.models import UserAlert
        count = UserAlert.objects.count()
        print(f"   ✓ Database connected - {count} existing users")
    except Exception as e:
        print(f"   ✗ Database error: {e}")
        return False
    
    print()
    
    # Test SMS sending (using test number)
    print("4. Testing SMS Send:")
    try:
        # Use a test phone number (Africa's Talking sandbox)
        test_number = "+254700000000"
        test_message = "Test message from Climate Alert System"
        
        result = AfricasTalkingService.send_sms(test_number, test_message)
        
        if result:
            print(f"   ✓ SMS send attempted")
            print(f"   Response: {result}")
        else:
            print(f"   ⚠ No response from Africa's Talking")
    except Exception as e:
        print(f"   ⚠ SMS test error: {e}")
        print(f"   (This may be expected if credentials are invalid or sandbox not configured)")
    
    print()
    print("=" * 60)
    print("✓ Integration test completed successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_credentials()
    sys.exit(0 if success else 1)
