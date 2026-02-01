#!/bin/bash
# Clear in-memory USSD sessions using the debug endpoint.
# Set USSD_DEBUG_SECRET in your environment or pass via --secret

NGROK_URL=${1:-http://localhost:8001}
SECRET=${2:-${USSD_DEBUG_SECRET}}

if [ -z "$SECRET" ]; then
  echo "USSD debug secret not provided. Set USSD_DEBUG_SECRET env or pass as second arg."
  exit 1
fi

echo "Clearing USSD sessions at $NGROK_URL/alerts/debug/clear_sessions"
curl -s -X POST "$NGROK_URL/alerts/debug/clear_sessions?secret=$SECRET" -w "\nHTTP_STATUS:%{http_code}\n" -o /dev/stdout
