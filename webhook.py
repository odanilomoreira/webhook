import requests
import json

# webhook_url = "https://webhook.site/7863369b-f555-4ba7-b764-6c451cd1b010"
webhook_url = "http://127.0.0.1:4242/webhook"

data = {
    'order': 'shoes',
    'price': 59.99
}

r = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
print(r)