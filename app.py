import json
from flask import Flask, render_template, request
from dotenv import load_dotenv
from requests import Session
from twilio.rest import Client
import os
load_dotenv()

coinmarketcap_api_token = os.environ.get('COIN_MARKET_TOKEN')
app = Flask('__name__')

slug_dict = {
    'matic':['3890', 'polygon'],
    'btc':['1', 'bitcoin'],
    'eth':['1027', 'ethereum']
}
parameters = {
    'slug':''
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': coinmarketcap_api_token
}
session = Session()
session.headers.update(headers)


twilio_acc_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
notify_service_sid = os.environ.get('NOTIFY_SERVICE_SID')
mobile_number = os.environ.get('MOBILE_NO')
client = Client(twilio_acc_sid, twilio_auth_token)

# To get the Coinmarketcap data for particular crypto coin
def get_crypto_data(crypto):
    parameters['slug'] = slug_dict[crypto.lower()][1]
    print(parameters['slug'])
    url ='https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    try:
        id = slug_dict[crypto.lower()][0]
        response = session.get(url,params=parameters)
        data = json.loads(response.text)['data'][id]
        name=data['name']
        price = round(data['quote']['USD']['price'], 3)
        percent_change_24 = round(data['quote']['USD']['percent_change_24h'], 3)
        print(f"{name} : {price} : {round(percent_change_24, 2)}%")
        return [name, price, percent_change_24]
    except:
        print("Error")
    

# To send create and send message to the given mobile numberx
def send_message(mobile, crypto_data):
    try:
        print("reached here.....")
        message = client.messages.create(   
            from_=mobile_number,
            body=f"Now data for {crypto_data[0]} \nPrice : ${crypto_data[1]} \nPercent_change_24h : {crypto_data[2]}%",
            to=mobile
        )
        print(message.sid)
    except:
        print("Error while sending message")

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        mobile = request.form['mobile']
        crypto = request.form['crypto']
        crypto_data = get_crypto_data(crypto)
        send_message(mobile, crypto_data)
    return render_template('index.html')

@app.route("/test")
def test():
    return render_template('test.html')

if __name__ == "__main__":
    app.run()