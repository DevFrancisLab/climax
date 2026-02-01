"""USSD translations and menu builders for multilingual support"""

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
    }
}


def get_text(language, key, **kwargs):
    """Get translated text for a given key and language.
    
    Args:
        language: 'en' or 'sw'
        key: Translation key
        **kwargs: Format parameters (e.g., county='Nairobi')
    
    Returns:
        Translated and formatted text
    """
    text = TRANSLATIONS.get(language, TRANSLATIONS['en']).get(key, '')
    return text.format(**kwargs) if kwargs else text


def build_county_menu(language):
    """Build county selection menu in specified language.
    
    Args:
        language: 'en' or 'sw'
    
    Returns:
        Formatted county menu string
    """
    menu = get_text(language, 'county_selection')
    county_display = COUNTY_DISPLAY.get(language, COUNTY_DISPLAY['en'])
    
    for key, val in county_display.items():
        menu += f"{key}. {val}\n"
    
    return menu.rstrip('\n')
