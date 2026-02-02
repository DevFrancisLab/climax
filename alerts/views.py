from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserAlert, ClimateAlert
from .services.africastalking_service import AfricasTalkingService
from .services.ai_service import AIService
from .services.ussd_translations import (
    get_text,
    build_county_menu,
    get_pagination_info,
    COUNTIES,
    COUNTY_DISPLAY,
)
import os


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
    """Store user's language preference in session and database (if registered)."""
    # Update session
    if phone_number not in _ussd_sessions:
        _ussd_sessions[phone_number] = {}
    _ussd_sessions[phone_number]["language"] = language
    _ussd_sessions[phone_number]["language_selected"] = True
    _ussd_sessions[phone_number]["state"] = "main_menu"
    
    # Also update database if user is registered
    try:
        user = UserAlert.objects.get(phone_number=phone_number)
        user.language = language
        user.save(update_fields=['language'])
    except UserAlert.DoesNotExist:
        # User not yet registered, that's fine - they'll be created when they select a county
        pass


def get_session_state(phone_number: str) -> str:
    """Get current USSD session state.
    
    MULTILINGUAL FEATURE: Returns 'language_selection' as default state
    for new sessions, ensuring users select language before accessing menus.
    """
    return _ussd_sessions.get(phone_number, {}).get("state", "language_selection")


def set_session_state(phone_number: str, state: str):
    """Set current USSD session state."""
    if phone_number not in _ussd_sessions:
        _ussd_sessions[phone_number] = {}
    _ussd_sessions[phone_number]["state"] = state


def has_language_been_selected(phone_number: str) -> bool:
    """Check if user has already selected a language in this session.
    
    Priority: Session flag > Database registration
    This ensures that when a user chooses 99 to change language,
    the session flag takes precedence over database status.
    """
    # Check session flag FIRST - this allows users to reset language selection
    # even if they're registered in the database
    session_flag = _ussd_sessions.get(phone_number, {}).get("language_selected", None)
    if session_flag is not None:
        return session_flag
    
    # If user is registered in DB and no session flag, they've already selected
    try:
        UserAlert.objects.get(phone_number=phone_number)
        return True
    except UserAlert.DoesNotExist:
        pass
    
    # Default to False for new sessions
    return False


def get_session_county_page(phone_number: str) -> int:
    """Get current county pagination page from session."""
    return _ussd_sessions.get(phone_number, {}).get("county_page", 1)


def set_session_county_page(phone_number: str, page: int):
    """Set county pagination page in session."""
    if phone_number not in _ussd_sessions:
        _ussd_sessions[phone_number] = {}
    _ussd_sessions[phone_number]["county_page"] = page


def reset_session_county_page(phone_number: str):
    """Reset county pagination to page 1."""
    set_session_county_page(phone_number, 1)


@csrf_exempt
def ussd_callback(request):
    """Handle USSD callback from Africa's Talking with language support.
    
    PRODUCTION HARDENING:
    - Global try/except ensures endpoint never crashes
    - All code paths guarantee valid CON/END response
    - State-based language selection fixes deep menu navigation
    - Language selection triggered by state, not step_count
    """
    try:
        session_id = request.POST.get("sessionId")
        phone_number = request.POST.get("phoneNumber")
        text = request.POST.get("text", "")

        response = ""
        
        # Parse the USSD navigation steps (Africa's Talking concatenates with *)
        steps = text.split("*") if text else []
        step_count = len(steps)
        current_step = steps[-1] if steps else ""  # The latest step selected
        
        # Determine current language and state
        language = get_user_language(phone_number)
        language_selected = has_language_been_selected(phone_number)
        current_state = get_session_state(phone_number)
        
        # Debug logging for troubleshooting live callbacks
        try:
            debug_info = {
                "sessionId": session_id,
                "phoneNumber": phone_number,
                "text": text,
                "steps": steps,
                "step_count": step_count,
                "current_step": current_step,
                "language": language,
                "language_selected": language_selected,
                "current_state": current_state,
            }
            print(f"USSD DEBUG: {debug_info}")
        except Exception:
            # Keep handler robust; never fail due to logging
            pass
        
        # NEW SESSION (empty text) - initialize state based on language selection
        if text == "":
            # Always show the appropriate starting menu
            if language_selected:
                # User has selected language before - show main menu
                set_session_state(phone_number, "main_menu")
                response = f"CON {get_text(language, 'main_menu')}"
            else:
                # New session or user needs to select language
                # MULTILINGUAL FEATURE: Show language selection screen
                set_session_state(phone_number, "language_selection")
                response = f"CON {get_text(language, 'language_selection')}"
        
        # STATE-BASED: LANGUAGE SELECTION
        # Trigger when in language_selection state, regardless of step_count
        # This fixes the bug where deep menu navigation (e.g., 1*99*2) breaks selection
        elif current_state == "language_selection" and current_step in ["1", "2"]:
            if current_step == "1":
                # SELECT ENGLISH
                set_user_language(phone_number, "en")
                reset_session_county_page(phone_number)
                response = f"CON {get_text('en', 'main_menu')}"
            elif current_step == "2":
                # SELECT KISWAHILI
                set_user_language(phone_number, "sw")
                reset_session_county_page(phone_number)
                response = f"CON {get_text('sw', 'main_menu')}"
        
        # NAVIGATION CONTROL: 99 - Change language (Back to language selection)
        elif current_step == "99" and language_selected:
            set_session_state(phone_number, "language_selection")
            reset_session_county_page(phone_number)
            # Clear language selection to force user to choose again
            if phone_number in _ussd_sessions:
                _ussd_sessions[phone_number]["language_selected"] = False
            response = f"CON {get_text('en', 'language_selection')}"
        
        # NAVIGATION CONTROL: 00 - Go to Main Menu (English and Swahili)
        elif language in ["en", "sw"] and current_step == "00" and language_selected:
            set_session_state(phone_number, "main_menu")
            reset_session_county_page(phone_number)
            response = f"CON {get_text(language, 'main_menu')}"
        
        # NAVIGATION CONTROL: 98 - Next page (English and Swahili county menu pagination)
        elif language in ["en", "sw"] and current_step == "98" and current_state == "county_selection":
            current_page = get_session_county_page(phone_number)
            pagination = get_pagination_info(current_page, counties_per_page=5)
            
            # Move to next page if available
            if current_page < pagination['total_pages']:
                next_page = current_page + 1
                set_session_county_page(phone_number, next_page)
                response = f"CON {build_county_menu(language, page=next_page, counties_per_page=5)}"
            else:
                # Already on last page
                response = f"CON {build_county_menu(language, page=current_page, counties_per_page=5)}"
        
        # NAVIGATION CONTROL: 0 - Back (English and Swahili)
        elif language in ["en", "sw"] and current_step == "0" and language_selected:
            # Go back based on current state
            if current_state == "county_selection":
                # From county selection → check if on paginated page
                current_page = get_session_county_page(phone_number)
                if current_page > 1:
                    # Go back to previous county page
                    prev_page = current_page - 1
                    set_session_county_page(phone_number, prev_page)
                    response = f"CON {build_county_menu(language, page=prev_page, counties_per_page=5)}"
                else:
                    # On page 1, go back to main menu
                    set_session_state(phone_number, "main_menu")
                    reset_session_county_page(phone_number)
                    response = f"CON {get_text(language, 'main_menu')}"
            elif current_state == "risk_status":
                # From risk status → back to main menu
                set_session_state(phone_number, "main_menu")
                reset_session_county_page(phone_number)
                response = f"CON {get_text(language, 'main_menu')}"
            else:
                # From main menu or other states, go to language selection
                set_session_state(phone_number, "language_selection")
                reset_session_county_page(phone_number)
                response = f"CON {get_text(language, 'language_selection')}"
        
        # STATE-BASED ROUTING: County selection takes priority over main menu routing
        elif current_state == "county_selection" and current_step in COUNTIES:
            # User is selecting a county
            county_code = current_step
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
                # Keep language preference but reset state to main_menu for next interaction
                if phone_number in _ussd_sessions:
                    _ussd_sessions[phone_number]["state"] = "main_menu"
                response = f"END {success_text}"
            except Exception as e:
                error_text = get_text(language, "registration_error")
                response = f"END {error_text}"
                print(f"Registration error for {phone_number}: {e}")
        
        # STATE-BASED ROUTING: Risk status back option
        elif current_state == "risk_status" and current_step == "1":
            set_session_state(phone_number, "main_menu")
            response = f"CON {get_text(language, 'main_menu')}"
        
        # STEP 2+: HANDLE CONCATENATED STEPS (format: {language}*{step1}*{step2}*...)
        elif step_count >= 2:
            # User's language is set from step 0 (language selection), now handle subsequent menu choices
            menu_choice = steps[1] if len(steps) > 1 else ""
            
            if menu_choice == "1":
                # Register option (step 1)
                if step_count == 2:
                    # Just selected register, show county menu
                    set_session_state(phone_number, "county_selection")
                    county_page = get_session_county_page(phone_number)
                    response = f"CON {build_county_menu(language, page=county_page, counties_per_page=5)}"
                elif step_count == 3:
                    # Selected county (step 2)
                    county_code = steps[2]
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
                            # Keep language preference but reset state to main_menu for next interaction
                            if phone_number in _ussd_sessions:
                                _ussd_sessions[phone_number]["state"] = "main_menu"
                            response = f"END {success_text}"
                        except Exception as e:
                            error_text = get_text(language, "registration_error")
                            response = f"END {error_text}"
                            print(f"Registration error for {phone_number}: {e}")
                    else:
                        error_text = get_text(language, "invalid_county")
                        response = f"END {error_text}"
            
            elif menu_choice == "2":
                # Check risk status
                if step_count == 2:
                    # Show risk status
                    try:
                        user = UserAlert.objects.get(phone_number=phone_number)
                        language = user.language
                        alert = ClimateAlert.objects.filter(
                            county=user.county, approved=True
                        ).order_by("-created_at").first()
                        if alert:
                            title = get_text(language, "risk_status_title", county=user.get_county_display())
                            back_text = get_text(language, "back_to_menu")
                            set_session_state(phone_number, "risk_status")
                            response = f"CON {title}\n{alert.message}\n{back_text}"
                        else:
                            no_alerts = get_text(language, "no_alerts", county=user.get_county_display())
                            response = f"END {no_alerts}"
                    except UserAlert.DoesNotExist:
                        register_first = get_text(language, "register_first")
                        response = f"END {register_first}"
                elif step_count == 3 and steps[2] == "1":
                    # Back to menu from risk status
                    set_session_state(phone_number, "main_menu")
                    response = f"CON {get_text(language, 'main_menu')}"
            
            elif menu_choice == "3":
                # Unsubscribe
                try:
                    UserAlert.objects.filter(phone_number=phone_number).update(is_active=False)
                    unsubscribed_text = get_text(language, "unsubscribed")
                    response = f"END {unsubscribed_text}"
                except Exception as e:
                    error_text = get_text(language, "unsubscribe_error")
                    response = f"END {error_text}"
                    print(f"Unsubscribe error: {e}")
            else:
                # Invalid menu choice at step 2+, show main menu
                set_session_state(phone_number, "main_menu")
                response = f"CON {get_text(language, 'main_menu')}"
        
        # STATE-BASED ROUTING: Main menu and other single-step requests
        elif language_selected and step_count == 1:
            # User has language selected, route based on current step
            if current_step == "1":
                # Register option - show county menu
                set_session_state(phone_number, "county_selection")
                county_page = get_session_county_page(phone_number)
                response = f"CON {build_county_menu(language, page=county_page, counties_per_page=5)}"
            elif current_step == "2":
                # Check risk status
                try:
                    user = UserAlert.objects.get(phone_number=phone_number)
                    language = user.language
                    alert = ClimateAlert.objects.filter(
                        county=user.county, approved=True
                    ).order_by("-created_at").first()
                    if alert:
                        title = get_text(language, "risk_status_title", county=user.get_county_display())
                        back_text = get_text(language, "back_to_menu")
                        set_session_state(phone_number, "risk_status")
                        response = f"CON {title}\n{alert.message}\n{back_text}"
                    else:
                        no_alerts = get_text(language, "no_alerts", county=user.get_county_display())
                        response = f"END {no_alerts}"
                except UserAlert.DoesNotExist:
                    register_first = get_text(language, "register_first")
                    response = f"END {register_first}"
            elif current_step == "3":
                # Unsubscribe
                try:
                    UserAlert.objects.filter(phone_number=phone_number).update(is_active=False)
                    unsubscribed_text = get_text(language, "unsubscribed")
                    response = f"END {unsubscribed_text}"
                except Exception as e:
                    error_text = get_text(language, "unsubscribe_error")
                    response = f"END {error_text}"
                    print(f"Unsubscribe error: {e}")
            else:
                # Invalid option - show main menu
                response = f"CON {get_text(language, 'main_menu')}"

        else:
            # Fallback: show appropriate menu based on state
            if current_state == "language_selection":
                response = f"CON {get_text(language, 'language_selection')}"
            else:
                # Default: show main menu with language selected
                set_session_state(phone_number, "main_menu")
                response = f"CON {get_text(language, 'main_menu')}"

        # FINAL SAFETY CHECK: Ensure response is never None or empty
        if not response:
            response = f"CON {get_text(language, 'main_menu')}"

        return HttpResponse(response, content_type="text/plain; charset=utf-8")
    
    except Exception as e:
        # Global exception handler: production NEVER crashes
        # Always return valid USSD response
        print(f"USSD HANDLER EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        
        # Return safe fallback response in English
        fallback = "CON Climate Alert System\n1. Register for alerts\n2. Check risk status\n3. Unsubscribe"
        return HttpResponse(fallback, content_type="text/plain; charset=utf-8")


@csrf_exempt
def clear_ussd_sessions(request):
    """Clears the in-memory USSD session store. Protected by environment secret.

    Use by setting `USSD_DEBUG_SECRET` in the server environment and
    sending the secret in the `X-USSD-SECRET` header or `?secret=` query param.
    """
    secret = os.getenv("USSD_DEBUG_SECRET")
    provided = request.META.get("HTTP_X_USSD_SECRET") or request.GET.get("secret")
    if not secret or provided != secret:
        return JsonResponse({"error": "unauthorized"}, status=401)

    count = len(_ussd_sessions)
    _ussd_sessions.clear()
    print(f"USSD DEBUG: cleared {count} sessions via API")
    return JsonResponse({"status": "cleared", "sessions_cleared": count})
