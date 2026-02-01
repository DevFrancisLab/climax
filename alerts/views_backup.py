from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserAlert, ClimateAlert
from .services.africastalking_service import AfricasTalkingService
from .services.ai_service import AIService
from .services.ussd_translations import (
    get_text,
    build_county_menu,
    COUNTIES,
    COUNTY_DISPLAY,
)


# Simple in-memory session storage for language preference and navigation state
# In production, use Redis or database
_ussd_sessions = {}


def get_user_language(phone_number: str) -> str:
    """Get user's language preference from session or database."""
    # Check in-memory session first
    if phone_number in _ussd_sessions:
        return _ussd_sessions[phone_number].get("language", "en")
    
    # Check database if user is registered
    try:
        user = UserAlert.objects.get(phone_number=phone_number)
        return user.language
    except UserAlert.DoesNotExist:
        return "en"


def set_user_language(phone_number: str, language: str):
    """Store user's language preference in session."""
    if phone_number not in _ussd_sessions:
        _ussd_sessions[phone_number] = {}
    _ussd_sessions[phone_number]["language"] = language
    _ussd_sessions[phone_number]["language_selected"] = True
    _ussd_sessions[phone_number]["state"] = "main_menu"  # Track current state


def get_session_state(phone_number: str) -> str:
    """Get current USSD session state."""
    return _ussd_sessions.get(phone_number, {}).get("state", "main_menu")


def set_session_state(phone_number: str, state: str):
    """Set current USSD session state."""
    if phone_number not in _ussd_sessions:
        _ussd_sessions[phone_number] = {}
    _ussd_sessions[phone_number]["state"] = state


def has_language_been_selected(phone_number: str) -> bool:
    """Check if user has already selected a language in this session."""
    # If user is registered in DB, they've already selected
    try:
        UserAlert.objects.get(phone_number=phone_number)
        return True
    except UserAlert.DoesNotExist:
        pass
    
    # Check if language was explicitly selected in this session
    return _ussd_sessions.get(phone_number, {}).get("language_selected", False)


@csrf_exempt
def ussd_callback(request):
    """Handle USSD callback from Africa's Talking with language support."""
    session_id = request.POST.get("sessionId")
    phone_number = request.POST.get("phoneNumber")
    text = request.POST.get("text", "")

    response = ""
    
    # Determine current language
    language = get_user_language(phone_number)
    language_selected = has_language_been_selected(phone_number)

    # LANGUAGE SELECTION SCREEN (first interaction - empty text)
    if text == "":
        response = f"CON {get_text(language, 'language_selection')}"

    # SET LANGUAGE - Option 1: English (only if not yet selected)
    elif text == "1" and not language_selected:
        set_user_language(phone_number, "en")
        language = "en"
        response = f"CON {get_text(language, 'main_menu')}"

    # SET LANGUAGE - Option 2: Swahili (only if not yet selected)
    elif text == "2" and not language_selected:
        set_user_language(phone_number, "sw")
        language = "sw"
        response = f"CON {get_text(language, 'main_menu')}"

    # MAIN MENU - Register (option 1)
    elif text == "1" and language_selected:
        language = get_user_language(phone_number)
        response = f"CON {build_county_menu(language)}"

    # MAIN MENU - Check Risk Status (option 2)
    elif text == "2" and language_selected:
        language = get_user_language(phone_number)
        try:
            user = UserAlert.objects.get(phone_number=phone_number)
            # Fetch latest approved alert for user's county
            alert = ClimateAlert.objects.filter(
                county=user.county, approved=True
            ).order_by("-created_at").first()
            if alert:
                title = get_text(language, "risk_status_title", county=user.get_county_display())
                back_text = get_text(language, "back_to_menu")
                response = f"CON {title}\n{alert.message}\n{back_text}"
            else:
                no_alerts = get_text(language, "no_alerts", county=user.get_county_display())
                response = f"END {no_alerts}"
        except UserAlert.DoesNotExist:
            register_first = get_text(language, "register_first")
            response = f"END {register_first}"

    # MAIN MENU - Unsubscribe (option 3)
    elif text == "3" and language_selected:
        language = get_user_language(phone_number)
        try:
            UserAlert.objects.filter(phone_number=phone_number).update(is_active=False)
            unsubscribed_text = get_text(language, "unsubscribed")
            response = f"END {unsubscribed_text}"
        except Exception as e:
            error_text = get_text(language, "unsubscribe_error")
            response = f"END {error_text}"
            print(f"Unsubscribe error: {e}")

    # REGISTER -> COUNTY SELECTION (format: 1*{county_code})
    elif text.startswith("1*") and language_selected:
        parts = text.split("*")
        if len(parts) >= 2:
            county_code = parts[1]
            if county_code in COUNTIES:
                county = COUNTIES[county_code]
                counties_display = COUNTY_DISPLAY.get(language, COUNTY_DISPLAY["en"])
                county_display = counties_display[county_code]

                try:
                    user_alert, created = UserAlert.objects.update_or_create(
                        phone_number=phone_number,
                        defaults={
                            "county": county,
                            "language": language,
                            "is_active": True,
                        },
                    )
                    # Send confirmation SMS
                    msg = get_text(language, "registration_confirmation", county=county_display)
                    AfricasTalkingService.send_sms(phone_number, msg)
                    success_text = get_text(language, "registration_success", county=county_display)
                    response = f"END {success_text}"
                except Exception as e:
                    error_text = get_text(language, "registration_error")
                    response = f"END {error_text}"
                    print(f"Registration error for {phone_number}: {e}")
            else:
                error_text = get_text(language, "invalid_county")
                response = f"END {error_text}"
        else:
            # Show county menu again
            response = f"CON {build_county_menu(language)}"
    
    # REGISTER -> COUNTY CODE SELECTION (direct county code 1-8, after main menu register)
    elif text in COUNTIES and language_selected:
        # User is selecting from county menu directly
        county_code = text
        county = COUNTIES[county_code]
        counties_display = COUNTY_DISPLAY.get(language, COUNTY_DISPLAY["en"])
        county_display = counties_display[county_code]
        
        try:
            user_alert, created = UserAlert.objects.update_or_create(
                phone_number=phone_number,
                defaults={
                    "county": county,
                    "language": language,
                    "is_active": True,
                },
            )
            # Send confirmation SMS
            msg = get_text(language, "registration_confirmation", county=county_display)
            AfricasTalkingService.send_sms(phone_number, msg)
            success_text = get_text(language, "registration_success", county=county_display)
            response = f"END {success_text}"
        except Exception as e:
            error_text = get_text(language, "registration_error")
            response = f"END {error_text}"
            print(f"Registration error for {phone_number}: {e}")

    # BACK TO MAIN MENU (from risk status screen)
    elif text == "2*1" and language_selected:
        language = get_user_language(phone_number)
        response = f"CON {get_text(language, 'main_menu')}"

    else:
        # Fallback: show main menu or language selection
        if language_selected:
            response = f"CON {get_text(language, 'main_menu')}"
        else:
            response = f"CON {get_text(language, 'language_selection')}"

    return HttpResponse(response, content_type="text/plain")
