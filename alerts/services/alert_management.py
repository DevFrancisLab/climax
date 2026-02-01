"""Alert management and orchestration service."""

from .data_service import DataService
from .ai_service import AIService
from alerts.models import ClimateAlert


def create_ai_alerts_for_county(county: str) -> list[ClimateAlert]:
    """
    Create AI-generated climate alerts for a specific county.
    
    This function orchestrates the workflow:
    1. Fetch county risks from DataService
    2. Generate AI-powered alert text for each risk using AIService
    3. Create ClimateAlert records with suggested messages (not yet approved)
    
    Args:
        county: County name (e.g., 'nairobi', 'kisumu')
        
    Returns:
        List of created ClimateAlert objects (unapproved)
    """
    county_risks = DataService.get_county_risks(county)
    alerts = []
    
    for risk in county_risks:
        # Generate AI-powered alert text
        ai_text = AIService.generate_alert_from_json(
            county=county,
            risk_type=risk["risk_type"],
            risk_level=risk["risk_level"],
            forecast=risk["forecast"]
        )
        
        # Create the alert record with suggested message
        alert = ClimateAlert.objects.create(
            county=county,
            risk_type=risk["risk_type"],
            risk_level=risk["risk_level"],
            message="",  # Will be set after approval
            suggested_message=ai_text,
            approved=False
        )
        alerts.append(alert)
    
    return alerts
