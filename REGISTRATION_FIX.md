# Registration Flow - Bug Fix Summary

## Issue Reported
When testing in Africa's Talking USSD Simulator, selecting "1. Register for alerts" immediately registered the user for Busia (county code 1) without showing the county selection menu first.

**User complaint:** "I selected 1. Register for alerts, I told 'You are registered for Busia alerts. You will receive SMS updates' and I did not select it"

## Root Cause
The issue was **session state persistence in memory**. Here's what was happening:

### Before the Fix
1. Session state was stored with a default of `"main_menu"` when retrieving a non-existent session
2. This meant if a user went through registration and the session wasn't properly cleared, their state would remain in `"county_selection"`
3. When they called back later (or in subsequent tests), the code would:
   - Get `current_state = "county_selection"` (from previous session)
   - Receive `text = "1"` (thinking they're selecting "Register for alerts")
   - Match the county selection logic: `elif text in COUNTIES and current_state == "county_selection"`
   - Immediately register them for Busia (county code "1") without showing the menu

### The Fix (Two Changes)

**1. Changed default session state from "main_menu" to "language_selection"**
```python
# BEFORE:
def get_session_state(phone_number: str) -> str:
    return _ussd_sessions.get(phone_number, {}).get("state", "main_menu")

# AFTER:
def get_session_state(phone_number: str) -> str:
    return _ussd_sessions.get(phone_number, {}).get("state", "language_selection")
```

This ensures new sessions start in language selection mode, not main menu mode.

**2. Clear session state after successful registration**
```python
# After user registers successfully:
if phone_number in _ussd_sessions:
    _ussd_sessions[phone_number].clear()  # Completely clear the session
```

This prevents old session state from persisting to future interactions.

**3. Properly initialize state on empty text (new session start)**
```python
if text == "":
    # Always show the appropriate starting menu
    if language_selected:
        set_session_state(phone_number, "main_menu")
        response = f"CON {get_text(language, 'main_menu')}"
    else:
        set_session_state(phone_number, "language_selection")
        response = f"CON {get_text(language, 'language_selection')}"
```

This ensures that:
- New users always start with language selection
- Returning users (already registered) skip to main menu
- The state is explicitly set based on registration status

## Verification
All tests pass, including new test case `test_registration_flow.sh`:

```
Step 1: Empty text → Language selection menu ✅
Step 2: Select "1" (English) → Main menu ✅
Step 3: Select "1" (Register) → County selection menu ✅
Step 4: Select "2" (Kisumu) → Registration confirmation ✅
```

## How to Test
Run the test script:
```bash
./test_registration_flow.sh
```

Or use Africa's Talking USSD Simulator:
1. Navigate to Dashboard → USSD → Simulator
2. Dial the short code
3. When prompted, select language
4. Select "Register for alerts"
5. Verify county selection menu appears
6. Select your county
7. Verify registration confirmation

## State Transitions (Correct Flow)
```
New User Flow:
language_selection → (select 1 or 2) → main_menu → (select 1) → county_selection → (select 1-8) → END (registered)

Returning User Flow:
main_menu → (select 1) → main_menu (already registered, shows menu again)
main_menu → (select 2) → risk_status → (select 1) → main_menu
main_menu → (select 3) → END (unsubscribed)
```

## What Changed
- ✅ Session state no longer persists incorrectly after registration
- ✅ County selection menu is now required before registration
- ✅ New users always see language selection first
- ✅ State machine now properly resets between complete USSD flows
