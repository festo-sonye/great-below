import requests
import json
from django.conf import settings
from datetime import datetime
from base64 import b64encode


class MpesaClient:
    """M-PESA Daraja API Client"""
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.phone = settings.MPESA_PHONE
        self.env = settings.MPESA_ENV
        self.callback_url = settings.MPESA_CALLBACK_URL
        
        if self.env == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
    
    def get_access_token(self):
        """Get access token from Daraja API"""
        url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        
        try:
            response = requests.get(
                url,
                auth=(self.consumer_key, self.consumer_secret),
                timeout=5
            )
            response.raise_for_status()
            return response.json()['access_token']
        except requests.exceptions.HTTPError as e:
            print(f"Daraja OAuth Error: Status {e.response.status_code}")
            print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
            return None
    
    def initiate_stk_push(self, phone_number, amount, order_code, account_reference='Great Below'):
        """Initiate STK push (Lipa na M-Pesa Online)"""
        access_token = self.get_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to get access token. Check your Consumer Key and Secret.'}
        
        # Format phone number
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif not phone_number.startswith('254'):
            phone_number = '254' + phone_number
        
        # Validate phone number format
        if len(phone_number) != 12 or not phone_number.startswith('254'):
            return {'success': False, 'error': f'Invalid phone number format: {phone_number}. Must be 254XXXXXXXXX'}
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password
        password_string = f'{self.shortcode}{self.passkey}{timestamp}'
        password = b64encode(password_string.encode()).decode()
        
        url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Amount must be an integer (in cents or whole Ksh)
        try:
            amount_int = int(float(amount))
        except:
            return {'success': False, 'error': f'Invalid amount format: {amount}'}
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount_int,
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': 'https://example.com/mpesa-callback/',  # Using dummy URL for sandbox testing
            'AccountReference': f'{account_reference}_{order_code}',
            'TransactionDesc': f'Payment for order {order_code}'
        }
        
        # Log the request for debugging
        print(f"M-PESA Request: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('ResponseCode') == '0':
                return {
                    'success': True,
                    'checkout_request_id': result.get('CheckoutRequestID'),
                    'customer_message': result.get('CustomerMessage'),
                    'request_id': result.get('RequestID')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('errorMessage', result.get('ResponseDescription', 'Unknown error')),
                    'response_code': result.get('ResponseCode')
                }
        except requests.exceptions.HTTPError as e:
            # Capture response body for debugging
            try:
                error_data = e.response.json()
                error_msg = error_data.get('errorMessage', error_data.get('error_description', str(e)))
            except:
                error_msg = e.response.text if hasattr(e, 'response') else str(e)
            print(f"M-PESA HTTP Error: {error_msg}")
            return {'success': False, 'error': f'HTTP Error: {error_msg}'}
        except Exception as e:
            print(f"M-PESA Exception: {str(e)}")
            return {'success': False, 'error': f'Request failed: {str(e)}'}
    
    def check_transaction_status(self, checkout_request_id):
        """Check STK push transaction status"""
        access_token = self.get_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to get access token'}
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f'{self.shortcode}{self.passkey}{timestamp}'
        password = b64encode(password_string.encode()).decode()
        
        url = f'{self.base_url}/mpesa/stkpushquery/v1/query'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'success': False, 'error': f'Request failed: {str(e)}'}
