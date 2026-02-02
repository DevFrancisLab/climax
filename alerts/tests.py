from django.test import TestCase, Client
from django.urls import reverse
from alerts.models import UserAlert
from alerts.services.africastalking_service import AfricasTalkingService
from alerts.views import _ussd_sessions
from unittest.mock import patch, MagicMock


class AfricasTalkingServiceTests(TestCase):
    """Test Africa's Talking service integration"""
    def test_send_sms(self):
        """Test sending SMS uses africastalking.SMS.send with expected args"""
        with patch('alerts.services.africastalking_service.africastalking.SMS') as mock_sms:
            mock_sms.send.return_value = {'SMSMessageData': {'Message': 'Sent'}}

            AfricasTalkingService.send_sms('+254700000000', 'Test message')

            mock_sms.send.assert_called_once_with(message='Test message', recipients=['+254700000000'])

    def test_send_sms_handles_exception(self):
        """Ensure send_sms doesn't raise if africastalking throws"""
        with patch('alerts.services.africastalking_service.africastalking.SMS') as mock_sms:
            mock_sms.send.side_effect = Exception('boom')
            # should not raise
            AfricasTalkingService.send_sms('+254700000000', 'Test message')



class USSDCallbackTests(TestCase):
    """Test USSD callback functionality"""

    def setUp(self):
        self.client = Client()
        self.ussd_url = '/alerts/ussd'
        # Clear sessions before each test
        _ussd_sessions.clear()

    def test_ussd_language_selection(self):
        """Test language selection at start of flow"""
        response = self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000000',
            'text': ''
        })
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Select Language', content)
        self.assertIn('1. English', content)
        self.assertIn('2. Kiswahili', content)

    def test_ussd_language_english(self):
        """Test selecting English language"""
        response = self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000000',
            'text': '1'
        })
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Climate Alert System', content)
        self.assertIn('Register for alerts', content)
        
        # Verify session language is English (either explicitly set or default)
        lang = _ussd_sessions.get('0700000000', {}).get('language', 'en')
        self.assertEqual(lang, 'en')

    def test_ussd_language_swahili(self):
        """Test selecting Swahili language"""
        response = self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000001',
            'text': '2'
        })
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Tahadhari ya Hali ya Hewa', content)  # Swahili for Climate Alert System
        self.assertIn('Jisajili', content)  # Swahili for Register
        
        # Verify session language was set
        self.assertEqual(_ussd_sessions.get('0700000001', {}).get('language'), 'sw')

    def test_ussd_county_selection_menu(self):
        """Test county selection menu is shown"""
        # Dial (shows language selection)
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000000',
            'text': ''
        })
        
        # Select English (option 1)
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000000',
            'text': '1'
        })
        
        # Select register (option 1 from main menu)
        response = self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000000',
            'text': '1'
        })
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Select County', content)
        self.assertIn('Busia', content)
        # With pagination (5 counties per page), Kilifi is on page 2
        # Check for pagination option instead
        self.assertIn('More counties', content)

    @patch('alerts.views.AfricasTalkingService.send_sms')
    def test_ussd_register_user(self, mock_send_sms):
        """Test user registration for alerts"""
        mock_send_sms.return_value = {'success': True}
        
        # Dial (shows language selection)
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000000',
            'text': ''
        })
        
        # Select English (option 1)
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000000',
            'text': '1'
        })
        
        # Select register (option 1 from main menu) - shows county selection
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000000',
            'text': '1'
        })
        
        # Register for Busia (option 1)
        response = self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000000',
            'text': '1'  # Select Busia
        })
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('registered', content.lower())
        
        # Verify user was saved
        user = UserAlert.objects.filter(phone_number='0700000000').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.county, 'busia')
        self.assertTrue(user.is_active)
        self.assertEqual(user.language, 'en')

    @patch('alerts.views.AfricasTalkingService.send_sms')
    def test_ussd_register_user_swahili(self, mock_send_sms):
        """Test user registration in Kiswahili"""
        mock_send_sms.return_value = {'success': True}
        
        # Dial (shows language selection)
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000003',
            'text': ''
        })
        
        # Select Kiswahili (option 2)
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000003',
            'text': '2'
        })
        
        # Select register (option 1 from main menu)
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000003',
            'text': '1'
        })
        
        # Register for Nairobi (option 7)
        response = self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000003',
            'text': '7'  # Nairobi
        })
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Check for Kiswahili registration confirmation text
        self.assertIn('umejisajili', content.lower())
        
        # Verify user was saved
        user = UserAlert.objects.filter(phone_number='0700000003').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.county, 'nairobi')
        self.assertEqual(user.language, 'sw')

    @patch('alerts.views.AfricasTalkingService.send_sms')
    def test_ussd_unsubscribe(self, mock_send_sms):
        """Test user unsubscribe"""
        # First create and register a user
        # Dial (language selection)
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000001',
            'text': ''
        })
        # Select English
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000001',
            'text': '1'
        })
        # Select register
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000001',
            'text': '1'
        })
        # Select county
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000001',
            'text': '7'  # Nairobi
        })
        
        # Now unsubscribe (option 3 from main menu)
        response = self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000001',
            'text': '3'
        })
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('unsubscribed', content.lower())
        
        # Verify user is marked inactive
        user = UserAlert.objects.get(phone_number='0700000001')
        self.assertFalse(user.is_active)

    def test_ussd_risk_status_not_registered(self):
        """Test risk status when user not registered"""
        # Dial (language selection)
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000002',
            'text': ''
        })
        
        # Select English
        self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000002',
            'text': '1'
        })
        
        # Check risk status when not registered (option 2 from main menu)
        response = self.client.post(self.ussd_url, {
            'sessionId': 'test123',
            'phoneNumber': '0700000002',
            'text': '2'
        })
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('register', content.lower())


class UserAlertModelTests(TestCase):
    """Test UserAlert model"""

    def test_create_user_alert(self):
        """Test creating a user alert"""
        alert = UserAlert.objects.create(
            phone_number='+254700000000',
            county='nairobi',
            language='en',
            is_active=True
        )
        
        self.assertEqual(alert.phone_number, '+254700000000')
        self.assertEqual(alert.county, 'nairobi')
        self.assertEqual(alert.language, 'en')
        self.assertTrue(alert.is_active)

    def test_unique_phone_number(self):
        """Test that phone numbers are unique"""
        UserAlert.objects.create(
            phone_number='+254700000000',
            county='nairobi'
        )
        
        # Trying to create duplicate should fail
        with self.assertRaises(Exception):
            UserAlert.objects.create(
                phone_number='+254700000000',
                county='kisumu'
            )

    def test_county_choices(self):
        """Test county choice validation"""
        alert = UserAlert.objects.create(
            phone_number='+254700000000',
            county='nairobi'
        )
        
        # Verify the display helper works
        self.assertEqual(alert.get_county_display(), 'Nairobi')
