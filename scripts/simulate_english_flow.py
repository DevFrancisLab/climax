import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'climax.settings')
import django
django.setup()
from django.test import Client

client = Client()
SESSION='simulate-english-001'
PHONE='0700999000'

print('\n[Step 1] initial (empty text)')
r = client.post('/alerts/ussd', {'sessionId':SESSION, 'phoneNumber':PHONE, 'text': ''})
print(r.content.decode())

print('\n[Step 2] select language = English (1)')
r = client.post('/alerts/ussd', {'sessionId':SESSION, 'phoneNumber':PHONE, 'text': '1'})
print(r.content.decode())

print('\n[Step 3] select Register (1)')
r = client.post('/alerts/ussd', {'sessionId':SESSION, 'phoneNumber':PHONE, 'text': '1'})
print(r.content.decode())

print('\n[Step 4] select county 2 (Kisumu)')
r = client.post('/alerts/ussd', {'sessionId':SESSION, 'phoneNumber':PHONE, 'text': '2'})
print(r.content.decode())
