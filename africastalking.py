# Local shim for africastalking to make tests and local runs deterministic.
# This is a lightweight stub only for local/testing environments.

def initialize(username=None, api_key=None):
    # no-op for tests
    return None

class SMS:
    @staticmethod
    def send(message=None, recipients=None):
        # Simple stub: pretend to send and return a success structure
        if not recipients:
            raise Exception("No recipients provided")
        return {"SMSMessageData": {"Message": "Sent", "Recipients": recipients, "Message": message}}

# Expose other services as no-op placeholders if needed
class Voice:
    @staticmethod
    def call(*args, **kwargs):
        return None
