from flask import Flask, request
from twilio.rest import Client
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from twilio.http.http_client import TwilioHttpClient
import os
from ast import literal_eval
import json
import requests
import uuid
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import SyncGrant
from config_json import (TWILIO_ACCOUNT_SID, 
                        TWILIO_AUTH_TOKEN, 
                        TWILIO_API_KEY_PUSH_SID, 
                        TWILIO_API_KEY_PUSH_SECRET,
                        TWILIO_SYNC_SERVICE)


app = Flask(__name__)
CORS(app)
api = Api(app)

# Twilio Sync
@app.route('/token', methods=['POST'])
def token():
    token = AccessToken(TWILIO_ACCOUNT_SID,
                        TWILIO_API_KEY_PUSH_SID,
                        TWILIO_API_KEY_PUSH_SECRET,
                        grants=[SyncGrant(TWILIO_SYNC_SERVICE)],
                        identity=uuid.uuid4().hex)
    return {'token': token.to_jwt().decode()}



body_request = reqparse.RequestParser()
body_request.add_argument('secret', type=str)
body_request.add_argument('event', type=str)
body_request.add_argument('event_id', type=str)
body_request.add_argument('restaurant_id', type=str)
body_request.add_argument('restaurant_name', type=str)
body_request.add_argument('restaurant_address', type=str)
body_request.add_argument('order_type', type=str)
body_request.add_argument('data', type=str)

# proxy_client = TwilioHttpClient(proxy={'http': os.environ['http_proxy'], 'https': os.environ['https_proxy']})
# client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,http_client=proxy_client)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_SMS(client, current_message, restaurant_phone, customer_phone):
    try: 
        message = client.messages.create(
                    body=current_message, 
                    from_=restaurant_phone,
                    to=customer_phone)

        status = 'success'
    except: 
        status = 'fail'
        
    return status

def push_to_front(info_needed):
    sync_service = client.sync.services(TWILIO_SYNC_SERVICE)
    todo_list = sync_service.sync_lists('msgList')
    todo_list.sync_list_items.create(info_needed)

class Webhook(Resource):
    def post(self):
        data = body_request.parse_args()
        data = {key:data[key] for key in data if data[key] is not None}
        details = literal_eval(data['data'])
        customer = details.get('order').get('customer')

        # gather data from rest api
        resp = requests.get("http://127.0.0.1:5000/restaurant/b9a2d2a0-7b09-4d32-8078-2621db1d2ffa")
        r = resp.json()
        users_ids = [u['user_id'] for u in r['users']]
        order_type = data.get('order_type')

        # send sms to the restaurant to the customer
        if order_type:
            if order_type == 'Pickup':
                status = send_SMS(client, r['pickup_message'], r['restaurant_phone'], '+5522997934061') #customer.get('phone'))
            else:
                status = send_SMS(client, r['delivery_message'], r['restaurant_phone'], '+5522997934061') #customer.get('phone'))
        
        if 'order_new' in data.get('event'):
            info_needed = {
                'order_type': data.get('order_type'),
                'name': customer.get('name'),
                'email': customer.get('email'),
                'sent_to': customer.get('phone'), 
                'sent_from': r['restaurant_phone'],
                'date_sent': details.get('order').get('created'),
                'log': status,
                'restaurant_name': data.get('restaurant_name'),
                'restaurant_id': r['restaurant_id'],
                'users_ids': users_ids
            }
            #send data to front end
            push_to_front(info_needed)

        return {'data': data}

api.add_resource(Webhook, '/webhook')        

if __name__ == '__main__':
    app.run(port=4242)


