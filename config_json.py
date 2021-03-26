import json

with open('credentials.json') as json_file:
    config = json.load(json_file)
    TWILIO_ACCOUNT_SID = config.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = config.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = config.get('TWILIO_PHONE_NUMBER')
    TWILIO_API_KEY = config.get('TWILIO_API_KEY')
    TWILIO_SYNC_SERVICE = config.get('TWILIO_SYNC_SERVICE')
    TWILIO_API_KEY_PUSH_SECRET = config.get('TWILIO_API_KEY_PUSH_SECRET')
    TWILIO_API_KEY_PUSH_SID = config.get('TWILIO_API_KEY_PUSH_SID')

