from django.urls import include, path

urlpatterns = [
    path("ussd", include("alerts.urls")),
]
