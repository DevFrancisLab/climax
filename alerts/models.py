from django.db import models


RISK_LEVELS = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]

LANGUAGE_CHOICES = [
    ("en", "English"),
    ("sw", "Swahili"),
]


class UserAlert(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    county = models.CharField(max_length=50)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="en")
    is_active = models.BooleanField(default=True)
    last_alert_sent = models.DateTimeField(null=True, blank=True)

    def get_county_display(self):
        return self.county.title()


class ClimateAlert(models.Model):
    county = models.CharField(max_length=50)
    risk_type = models.CharField(max_length=50)  # e.g., flood, drought
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS)
    message = models.TextField()
    suggested_message = models.TextField(null=True, blank=True)  # AI-generated message
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

