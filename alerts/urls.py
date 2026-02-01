from django.urls import path
from .views import ussd_callback, clear_ussd_sessions

urlpatterns = [
    path("ussd", ussd_callback),
    path("debug/clear_sessions", clear_ussd_sessions),
]
