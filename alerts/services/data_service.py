"""Data service for fetching county-specific climate and risk data."""


class DataService:
    """Service for retrieving climate and risk data for counties."""

    @staticmethod
    def get_county_risks(county: str) -> list[dict]:
        """
        Fetch risk data for a given county.
        
        Args:
            county: County name (e.g., 'nairobi', 'kisumu')
            
        Returns:
            List of risk dictionaries with keys: risk_type, risk_level, forecast
            
        Example:
            [
                {
                    "risk_type": "flood",
                    "risk_level": "high",
                    "forecast": "Heavy rains expected next 3 days"
                },
                {
                    "risk_type": "drought",
                    "risk_level": "low",
                    "forecast": "Normal rainfall pattern"
                }
            ]
        """
        # TODO: Replace with actual data source (API, database, external service)
        # For now, return example data based on county
        county_lower = county.lower()
        
        # Mock data: different risks for different counties
        risk_data = {
            "nairobi": [
                {
                    "risk_type": "flood",
                    "risk_level": "medium",
                    "forecast": "Isolated thunderstorms expected in the afternoon"
                }
            ],
            "kisumu": [
                {
                    "risk_type": "flood",
                    "risk_level": "high",
                    "forecast": "Heavy rainfall expected for next 5 days. Lake levels rising."
                }
            ],
            "turkana": [
                {
                    "risk_type": "drought",
                    "risk_level": "high",
                    "forecast": "Below-normal rainfall. Pasture and water scarcity likely."
                }
            ],
            "makueni": [
                {
                    "risk_type": "drought",
                    "risk_level": "medium",
                    "forecast": "Dry conditions continuing. Water rationing advised."
                }
            ],
            "busia": [
                {
                    "risk_type": "flood",
                    "risk_level": "high",
                    "forecast": "River levels rising due to upstream rainfall."
                }
            ],
            "garissa": [
                {
                    "risk_type": "drought",
                    "risk_level": "high",
                    "forecast": "Severe drought conditions. Livestock losses expected."
                }
            ],
            "kilifi": [
                {
                    "risk_type": "flood",
                    "risk_level": "medium",
                    "forecast": "Coastal flooding risk with high tides and swells."
                }
            ],
            "marsabit": [
                {
                    "risk_type": "drought",
                    "risk_level": "high",
                    "forecast": "Prolonged dry spell. Emergency water support needed."
                }
            ],
        }
        
        return risk_data.get(county_lower, [])
