import os
from flask import Flask, request, abort, render_template, redirect
import requests
from flask_bootstrap import Bootstrap

app = Flask(__name__, static_folder='static')
bootstrap = Bootstrap(app)

import json
import shelve
import uuid

class LinePay(object):

    DEFAULT_ENDPOINT = 'https://sandbox-api-pay.line.me/'
    VERSION = 'v2'

    def __init__(self, channel_id, channel_secret, redirect_url):
        self.channel_id = channel_id
        self.channel_secret = channel_secret
        self.redirect_url = redirect_url

    def reserve(self, product_name, amount, currency, order_id, **kwargs):
        url = '{}{}{}'.format(self.DEFAULT_ENDPOINT, self.VERSION, '/payments/request')
        data = {**
                {
                    'productName':product_name,
                    'amount':amount,
                    'currency':currency,
                    'confirmUrl':'https://{}{}'.format(request.environ['HTTP_HOST'], self.redirect_url),
                    'orderId':order_id,
                },
                **kwargs}
        headers = {'Content-Type': 'application/json',
                   'X-LINE-ChannelId':self.channel_id,
                   'X-LINE-ChannelSecret':self.channel_secret}
        response = requests.post(url, headers=headers, data=json.dumps(data).encode("utf-8"))

        if int(json.loads(response.text)['returnCode']) == 0:
            with shelve.open('store') as store:
                # just for prototyping
                store[str(json.loads(response.text)['info']['transactionId'])] = {'productName': product_name, 'amount': amount, 'currency': currency}
            return json.loads(response.text)

        else:
            abort(400, json.loads(response.text)['returnCode'] + ' : ' + json.loads(response.text)['returnMessage'])

    def confirm(self, transaction_id):
        transaction_info = {}
        with shelve.open('store') as store:
            transaction_info = store[transaction_id]

        if len(transaction_info) == 0:
            abort(400, 'reservation of this transaction id is not exists')

        url = '{}{}{}'.format(self.DEFAULT_ENDPOINT, self.VERSION, '/{}/confirm'.format(transaction_id))
        data = {
                'amount':transaction_info['amount'],
                'currency':transaction_info['currency'],
                }
        headers = {'Content-Type': 'application/json',
                   'X-LINE-ChannelId':self.channel_id,
                   'X-LINE-ChannelSecret':self.channel_secret}
        response = requests.post(url, headers=headers, data=json.dumps(data).encode("utf-8"))
        return transaction_info

# get it in https://pay.line.me/jp/developers/techsupport/sandbox/creation?locale=ja_JP
chennel_id = '1587958668'
channel_secret = '520e556b5afa9823bc4461a2a12c945c'
callback_url = '/callback'

"""
# get these at https://pay.line.me/center/notice/list after creating sandbox sandbox
chennel_id = YOUR_LINE_PAY_CHANNEL_ID
channel_secret = YOUR_LINE_PAY_CHANNEL_SECRET
callback_url = '/callback'
"""
pay = LinePay(chennel_id, channel_secret, callback_url)

@app.route("/")
def render_index():
    return render_template('index.html')

@app.route("/reserve")
def redirect_to_pay():
    data = {"product_name": "LINE Pay Demo product",
            'amount':'100',
            'currency':'JPY',
            'order_id':uuid.uuid4().hex,
            # optional values can be set. see https://pay.line.me/file/guidebook/technicallinking/LINE_Pay_Integration_Guide_for_Merchant-v1.1.2-JP.pdf
            'productImageUrl':'https://{}{}'.format(request.environ['HTTP_HOST'], '/static/item_image.png')
            }
    transaction_info = pay.reserve(**data)
    return redirect(transaction_info['info']['paymentUrl']['web'])

@app.route("/callback")
def callback_from_pay():
    transaction_info = pay.confirm(request.args.get('transactionId'))
    return render_template('purchased.html', **transaction_info)

app.errorhandler(400)
def handler_error_400(error):
    return error

if __name__ == '__main__':
    app.debug = True;
    app.run(host='0.0.0.0')
