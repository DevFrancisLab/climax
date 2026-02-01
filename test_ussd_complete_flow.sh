#!/bin/bash
# Proper USSD session test that simulates Africa's Talking behavior
# This script maintains sessionId across requests to test state persistence

BASE_URL="https://055f33e82726.ngrok-free.app/ussd"
SESSION_ID="$(uuidgen)"
PHONE="254700088999"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          USSD COMPLETE FLOW TEST (Proper Session)            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Session ID: $SESSION_ID"
echo "Phone: $PHONE"
echo ""

# Step 1: Initial request (language selection)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Language Selection (text='')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESP=$(curl -s -X POST "$BASE_URL" \
  -d "sessionId=$SESSION_ID" \
  -d "phoneNumber=$PHONE" \
  -d "text=" \
  -H "Content-Type: application/x-www-form-urlencoded")
echo "Response:"
echo "$RESP"
echo ""

# Step 2: Select English
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Select English (text='1')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESP=$(curl -s -X POST "$BASE_URL" \
  -d "sessionId=$SESSION_ID" \
  -d "phoneNumber=$PHONE" \
  -d "text=1" \
  -H "Content-Type: application/x-www-form-urlencoded")
echo "Response:"
echo "$RESP"
echo ""

# Step 3: Select Register (text=1 from main menu)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Select Register Option (text='1')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESP=$(curl -s -X POST "$BASE_URL" \
  -d "sessionId=$SESSION_ID" \
  -d "phoneNumber=$PHONE" \
  -d "text=1" \
  -H "Content-Type: application/x-www-form-urlencoded")
echo "Response:"
echo "$RESP"
echo ""

if [[ "$RESP" == *"Select County"* ]] || [[ "$RESP" == *"Busia"* ]]; then
  echo "✅ PASS: County menu is appearing!"
else
  echo "❌ FAIL: County menu NOT found!"
  echo "Debug: Response was: $RESP"
fi
echo ""

# Step 4: Select a county (e.g., Kisumu = 2)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Select County Kisumu (text='2')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESP=$(curl -s -X POST "$BASE_URL" \
  -d "sessionId=$SESSION_ID" \
  -d "phoneNumber=$PHONE" \
  -d "text=2" \
  -H "Content-Type: application/x-www-form-urlencoded")
echo "Response:"
echo "$RESP"
echo ""

if [[ "$RESP" == END* ]] && [[ "$RESP" == *"registered"* ]]; then
  echo "✅ PASS: User successfully registered!"
else
  echo "❌ FAIL: Registration unsuccessful!"
fi
echo ""

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                      TEST COMPLETE                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
