#!/bin/bash

# Test script to verify county selection happens before registration
# This reproduces the issue: "I selected Register for alerts but got registered for Busia without selecting it"

BASE_URL="http://localhost:8000/alerts/ussd"
SESSION_ID=$(uuidgen)
PHONE="254700$(date +%s | tail -c 6)"  # Generate unique phone number

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     TESTING REGISTRATION FLOW - COUNTY SELECTION REQUIRED      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Testing with:"
echo "  Session ID: $SESSION_ID"
echo "  Phone Number: $PHONE"
echo ""

# Step 1: Initiate session (empty text)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[Step 1] Initiate session (text='')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESPONSE1=$(curl -s -X POST "$BASE_URL" \
  -d "sessionId=$SESSION_ID" \
  -d "phoneNumber=$PHONE" \
  -d "text=")
echo "$RESPONSE1"
echo ""

# Verify we get language selection
if [[ "$RESPONSE1" == *"Select Language"* ]] || [[ "$RESPONSE1" == *"Chagua Lugha"* ]]; then
    echo "✅ PASS: Language selection menu displayed"
else
    echo "❌ FAIL: Expected language selection menu"
    echo "Got: $RESPONSE1"
fi
echo ""

# Step 2: Select English (text=1)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[Step 2] Select English (text='1')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESPONSE2=$(curl -s -X POST "$BASE_URL" \
  -d "sessionId=$SESSION_ID" \
  -d "phoneNumber=$PHONE" \
  -d "text=1")
echo "$RESPONSE2"
echo ""

# Verify we get main menu
if [[ "$RESPONSE2" == *"Climate Alert System"* ]] || [[ "$RESPONSE2" == *"Register for alerts"* ]]; then
    echo "✅ PASS: Main menu displayed in English"
else
    echo "❌ FAIL: Expected English main menu"
    echo "Got: $RESPONSE2"
fi
echo ""

# Step 3: Select "Register for alerts" (text=1 again)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[Step 3] Select 'Register for alerts' (text='1')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESPONSE3=$(curl -s -X POST "$BASE_URL" \
  -d "sessionId=$SESSION_ID" \
  -d "phoneNumber=$PHONE" \
  -d "text=1")
echo "$RESPONSE3"
echo ""

# THE CRITICAL CHECK: We should get county menu, NOT registration confirmation
if [[ "$RESPONSE3" == *"Select County"* ]]; then
    echo "✅ PASS: County selection menu displayed (not registered yet!)"
elif [[ "$RESPONSE3" == *"registered"* ]]; then
    echo "❌ FAIL: User was registered WITHOUT selecting county!"
    echo "This is the bug that was reported."
    exit 1
else
    echo "⚠️  WARNING: Unexpected response"
    echo "Got: $RESPONSE3"
fi
echo ""

# Step 4: Now select a county (Kisumu = option 2)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[Step 4] Select county 2 (Kisumu) (text='2')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESPONSE4=$(curl -s -X POST "$BASE_URL" \
  -d "sessionId=$SESSION_ID" \
  -d "phoneNumber=$PHONE" \
  -d "text=2")
echo "$RESPONSE4"
echo ""

# Verify registration success
if [[ "$RESPONSE4" == *"registered"* ]] && [[ "$RESPONSE4" == *"Kisumu"* ]]; then
    echo "✅ PASS: User successfully registered for Kisumu"
elif [[ "$RESPONSE4" == *"Busia"* ]]; then
    echo "❌ FAIL: User registered for Busia instead of Kisumu!"
    exit 1
else
    echo "⚠️  WARNING: Unexpected registration response"
    echo "Got: $RESPONSE4"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                     ALL TESTS PASSED ✅                        ║"
echo "║   County selection is required before registration is saved    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
