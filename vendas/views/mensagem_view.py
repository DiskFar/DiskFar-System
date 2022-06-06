import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

def envia_mensagem_whatsapp(numero, mensagem):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
                            from_=os.environ.get('TWILIO_FROM_WHATSAPP'),
                            body=mensagem,
                            to=f'whatsapp:+55{numero}'
        )
        return f'WhatsApp enviado com sucesso, para o número: {numero}'
    except TwilioRestException as error:
        return error
    
def envia_mensagem_sms(numero, mensagem):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
                            messaging_service_sid=os.environ.get('TWILIO_MESSAGING_SERVICE_SID'),
                            body=mensagem,
                            to=f'+55{numero}'
        )
        return f'SMS enviado com sucesso, para o número: {numero}'
    except TwilioRestException as error:
        return error