"""USSD translations and menu builders for multilingual support"""

# IMPROVEMENT 1: Counties dictionary with ordered numeric keys
# This ensures numeric order is maintained and easy to extend
COUNTIES = {
    '1': 'busia',
    '2': 'kisumu',
    '3': 'garissa',
    '4': 'turkana',
    '5': 'marsabit',
    '6': 'makueni',
    '7': 'nairobi',
    '8': 'kilifi',
}

COUNTY_DISPLAY = {
    'en': {
        '1': 'Busia',
        '2': 'Kisumu',
        '3': 'Garissa',
        '4': 'Turkana',
        '5': 'Marsabit',
        '6': 'Makueni',
        '7': 'Nairobi',
        '8': 'Kilifi',
    },
    'sw': {
        '1': 'Busia',
        '2': 'Kisumu',
        '3': 'Garissa',
        '4': 'Turkana',
        '5': 'Marsabit',
        '6': 'Makueni',
        '7': 'Nairobi',
        '8': 'Kilifi',
    }
}

TRANSLATIONS = {
    'en': {
        'language_selection': 'Select Language:\n1. English\n2. Kiswahili',
        'main_menu': 'Climate Alert System\n1. Register for alerts\n2. Check risk status\n3. Unsubscribe',
        'county_selection': 'Select County:\n',
        'registration_success': 'You are registered for {county} alerts.\nYou will receive SMS updates.',
        'registration_confirmation': 'Welcome to Climate Alert System. You are registered for {county} alerts.',
        'registration_error': 'Error registering. Please try again later.',
        'invalid_county': 'Invalid county selection. Please try again.',
        'no_alerts': 'No current alerts for {county}.',
        'risk_status_title': 'Latest alert for {county}:\n',
        'back_to_menu': '\n1. Back to menu',
        'register_first': 'Please register first for alerts.',
        'unsubscribed': 'You have been unsubscribed from alerts.',
        'unsubscribe_error': 'Error unsubscribing. Please try again.',
        'already_registered': 'You are already registered for alerts. Dial again to access the main menu.',
        # IMPROVEMENT 3: Added missing translation keys for better USSD flow handling
        'invalid_option': 'Invalid option. Please try again.',
        'session_timeout': 'Session expired. Please dial again.',
        'back': '1. Back',
    },
    'sw': {
        'language_selection': 'Chagua Lugha:\n1. English\n2. Kiswahili',
        'main_menu': 'Mfumo wa Onyo wa Tabia Nchi\n1. Jisajili kwa onyo\n2. Angalia hali ya hatari\n3. Sitisha',
        'county_selection': 'Chagua Kaunti:\n',
        'registration_success': 'Umejisajili kwa onyo za {county}.\nUtapokea ujumbe wa SMS.',
        'registration_confirmation': 'Karibu katika Mfumo wa Onyo wa Tabia Nchi. Umejisajili kwa onyo za {county}.',
        'registration_error': 'Hitilafu katika kusajili. Tafadhali jaribu tena baadaye.',
        'invalid_county': 'Chaguo la kaunti si sahihi. Tafadhali jaribu tena.',
        'no_alerts': 'Hakuna onyo la sasa kwa {county}.',
        'risk_status_title': 'Onyo la mwisho kwa {county}:\n',
        'back_to_menu': '\n1. Rudi katika menyu',
        'register_first': 'Tafadhali jisajili kwanza kwa onyo.',
        'unsubscribed': 'Umesitisha kupokea onyo.',
        'unsubscribe_error': 'Hitilafu katika kusitisha. Tafadhali jaribu tena.',
        'already_registered': 'Umejisajili tayari kwa onyo. Piga upya uone menyu ya kawaida.',
        # IMPROVEMENT 3: Added missing translation keys for better USSD flow handling
        'invalid_option': 'Chaguo si sahihi. Tafadhali jaribu tena.',
        'session_timeout': 'Kikao kimeacha. Tafadhali piga upya.',
        'back': '1. Rudi',
    }
}


def get_text(language, key, **kwargs):
    """Get translated text for a given key and language.
    
    IMPROVEMENT 3: Enhanced function to safely handle missing formatting keys.
    If a formatting placeholder is missing from kwargs, it will be left as-is
    instead of crashing the application.
    
    Args:
        language: 'en' or 'sw'
        key: Translation key
        **kwargs: Format parameters (e.g., county='Nairobi')
    
    Returns:
        Translated and formatted text. If language not found, defaults to English.
        If formatting key is missing, placeholder is preserved in output.
    """
    # Get text from language or fall back to English
    text = TRANSLATIONS.get(language, TRANSLATIONS['en']).get(key, '')
    
    # Safely format text with missing key protection
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError as e:
            # Log the missing key but don't crash
            print(f"WARNING: Missing format key {e} for translation key '{key}' in language '{language}'")
            # Return text with placeholders intact
            return text
    
    return text


def build_county_menu(language):
    """Build county selection menu in specified language.
    
    IMPROVEMENT 1: Ensures counties are always displayed in numeric order
    by sorting keys as integers instead of strings.
    
    IMPROVEMENT 2: Easy to extend for new languages - just add language
    key to COUNTY_DISPLAY dictionary.
    
    Args:
        language: 'en' or 'sw'
    
    Returns:
        Formatted county menu string with counties in numeric order
    """
    menu = get_text(language, 'county_selection')
    county_display = COUNTY_DISPLAY.get(language, COUNTY_DISPLAY['en'])
    
    # IMPROVEMENT 1: Sort counties by numeric key to ensure consistent order
    for key in sorted(county_display.keys(), key=int):
        val = county_display[key]
        menu += f"{key}. {val}\n"
    
    return menu.rstrip('\n')
