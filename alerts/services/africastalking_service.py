import africastalking
import os


africastalking.initialize(
    username=os.getenv("AT_USERNAME"),
    api_key=os.getenv("AT_API_KEY")
)



class AfricasTalkingService:
    @staticmethod
    def send_sms(phone_number, message):
        try:
            africastalking.SMS.send(message=message, recipients=[phone_number])
            print(f"SMS sent to {phone_number}: {message}")
        except Exception as e:
            print(f"Error sending SMS to {phone_number}: {e}")
