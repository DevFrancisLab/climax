# Multilingual USSD Climate Alert System

## Overview
The CLIMAX climate alert system now supports multilingual USSD interface with English and Swahili (Kiswahili) support. Users select their language at the start of the USSD flow, and all subsequent menus are rendered in their chosen language.

## Features Implemented

### ✅ Language Selection
- Initial screen presents language options: English or Kiswahili
- Language preference is stored in session and database
- Selection persists across sessions for registered users

### ✅ Dynamic Menu Rendering
All menus are translated and rendered based on user's language choice:
- **Language Selection Menu**: "Select Language / Chagua Lugha"
- **Main Menu**: Shows register, check risk status, unsubscribe options
- **County Selection Menu**: All 8 Kenyan counties with language-appropriate text
- **Success/Error Messages**: Contextual feedback in selected language

### ✅ State Management
4-state USSD state machine:
- `language_selection`: Initial screen
- `main_menu`: After language selected
- `county_selection`: During registration process
- `risk_status`: When viewing alert details

### ✅ Session Persistence
- In-memory session dictionary stores language and state per phone number
- Database persistence for registered users
- Language preference survives across USSD sessions

## USSD Flow Diagram

```
Start (text="")
    ↓
Language Selection
├─ text="1" → English
└─ text="2" → Swahili
    ↓
Main Menu (Language-specific)
├─ text="1" → Register for alerts
├─ text="2" → Check risk status
└─ text="3" → Unsubscribe
    ↓
[If Register] County Selection (Language-specific)
    ├─ text="1" → Busia
    ├─ text="2" → Kisumu
    ├─ text="3" → Garissa
    ├─ text="4" → Turkana
    ├─ text="5" → Marsabit
    ├─ text="6" → Makueni
    ├─ text="7" → Nairobi
    └─ text="8" → Kilifi
        ↓
    Registration Success (END)
```

## Code Architecture

### New Module: `alerts/services/ussd_translations.py`
- `TRANSLATIONS`: Centralized translation dictionary
- `get_text(language, key, **kwargs)`: Retrieve translated text with variable substitution
- `build_county_menu(language)`: Generate county selection menu in specified language
- `COUNTIES`: County code mapping
- `COUNTY_DISPLAY`: Language-specific county display names

### Updated: `alerts/views.py`
- In-memory session storage: `_ussd_sessions` dictionary
- Session management functions:
  - `get_user_language(phone_number)`: Retrieve language from session or database
  - `set_user_language(phone_number, language)`: Store language preference
  - `get_session_state(phone_number)`: Get current USSD navigation state
  - `set_session_state(phone_number, state)`: Update navigation state
  - `has_language_been_selected(phone_number)`: Check if language was chosen
- Updated `ussd_callback()`: State-aware menu rendering with language support

### Updated: `alerts/models.py`
- New field in `UserAlert`: `language` (CharField with choices: 'en'/'sw')
- Default language: 'en' (English)

## Translations

### English Menus
```
Select Language:
1. English
2. Kiswahili

Climate Alert System
1. Register for alerts
2. Check risk status
3. Unsubscribe

Select County:
1. Busia
2. Kisumu
... [etc]
```

### Swahili Menus
```
Chagua Lugha:
1. English
2. Kiswahili

Mfumo wa Onyo wa Tabia Nchi
1. Jisajili kwa onyo
2. Angalia hali ya hatari
3. Sitisha

Chagua Kaunti:
1. Busia
2. Kisumu
... [etc]
```

## Test Coverage

13 unit tests covering:
- ✅ SMS sending integration
- ✅ Language selection (English and Swahili)
- ✅ County selection menu display
- ✅ User registration (both languages)
- ✅ Risk status checking
- ✅ Unsubscribe functionality
- ✅ Model validation

**Status**: All 13 tests passing ✓

## Session Storage

### Current Implementation
In-memory Python dictionary:
```python
_ussd_sessions = {
    'phone_number': {
        'language': 'en' or 'sw',
        'language_selected': True/False,
        'state': 'language_selection' | 'main_menu' | 'county_selection' | 'risk_status'
    }
}
```

### Production Recommendation
Replace with Redis for distributed systems:
```python
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)
```

## API Response Format

All responses follow Africa's Talking USSD standard:
- **CON** prefix: Continue the USSD session
- **END** prefix: Terminate the USSD session

Example:
```
CON Climate Alert System
1. Register for alerts
2. Check risk status
3. Unsubscribe
```

## Database Changes

Migration: `0004_useralert_language`
- Adds `language` field to `UserAlert` model
- Default value: 'en' (English)
- Choices: [('en', 'English'), ('sw', 'Swahili')]

## Configuration

No additional configuration required. The system:
- Auto-detects new vs. returning users
- Defaults to English for new users
- Retrieves stored language for registered users
- Maintains session state for seamless multi-step flows

## How It Works

1. **New User Calls USSD Code**
   ```
   User: *130*1#
   System: Shows language selection (default English text)
   ```

2. **User Selects Language**
   ```
   User: 2 (Swahili)
   System: Switches all menus to Swahili, shows main menu
   ```

3. **User Completes Registration**
   ```
   User: 1 (Register) → 7 (Nairobi)
   System: Stores county, language in database, sends SMS confirmation in Swahili
   ```

4. **User Returns (Language Persists)**
   ```
   User: *130*1#
   System: Retrieves stored language (Swahili), shows main menu in Swahili
   ```

## Extending with New Languages

To add a new language (e.g., French):

1. Update `LANGUAGE_CHOICES` in `models.py`:
   ```python
   LANGUAGE_CHOICES = [
       ("en", "English"),
       ("sw", "Swahili"),
       ("fr", "French"),
   ]
   ```

2. Add translations to `ussd_translations.py`:
   ```python
   TRANSLATIONS = {
       'en': { ... },
       'sw': { ... },
       'fr': {
           'language_selection': 'Sélectionner la langue:\n1. English\n2. Kiswahili',
           'main_menu': '...',
           ...
       }
   }
   ```

3. Run migration:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

## Testing

Run all tests:
```bash
python manage.py test alerts
```

Test specific functionality:
```bash
python manage.py test alerts.tests.USSDCallbackTests.test_ussd_language_swahili
```

## Future Enhancements

- [ ] Store sessions in Redis for scalability
- [ ] Add SMS-based language switching (text "LANG=sw")
- [ ] Support for additional languages
- [ ] Admin interface for managing translations
- [ ] Analytics on language preferences by region
- [ ] A/B testing for menu layout optimization

---

**Last Updated**: January 2026
**Status**: Production Ready ✓
