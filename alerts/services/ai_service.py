import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class AIService:
    @staticmethod
    def generate_alert_from_json(county: str, risk_type: str, risk_level: str, forecast: str) -> str:
        """Generates a concise, SMS-ready alert using Gemini Flash.
        
        Args:
            county: County name
            risk_type: Type of risk (e.g., flood, drought)
            risk_level: Risk level (low, medium, high)
            forecast: Weather/climate forecast description
            
        Returns:
            SMS-ready alert text (under 160 characters)
        """
        if not GEMINI_API_KEY:
            # Fallback if API key not configured
            return f"⚠️ {risk_type.upper()} ALERT – {county.title()} | {risk_level.upper()}: {forecast}"
        
        prompt = (
            f"Write a concise, clear SMS alert for {county.title()} county.\n"
            f"Risk type: {risk_type}\n"
            f"Risk level: {risk_level}\n"
            f"Forecast: {forecast}\n"
            f"Make it actionable and short (under 160 characters)."
        )
        
        try:
            # Using Gemini 2.5 Flash Lite API to generate text
            model = genai.GenerativeModel("gemini-2.5-flash-lite")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini Flash error: {e}")
            # Fallback to simple text if AI fails
            return f"⚠️ {risk_type.upper()} ALERT – {county.title()} | {risk_level.upper()}: {forecast}"

    @staticmethod
    def summarize(text: str) -> str:
        """Return a summary of text (fallback placeholder)."""
        if not text:
            return ""
        return text[:160] + ("..." if len(text) > 160 else "")

    @staticmethod
    def classify_risk(message: str) -> str:
        """Naive risk classification: low/medium/high."""
        if not message:
            return "low"
        m = message.lower()
        if "severe" in m or "high" in m or "danger" in m:
            return "high"
        if "moderate" in m or "medium" in m or "watch" in m:
            return "medium"
        return "low"