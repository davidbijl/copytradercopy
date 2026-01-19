# Python copy-trading script to copy Futures positions between Kraken acounts.

# This code contains 2 sections. 
# Section 1 falls under the MTI License and Crypto Facilities copyright notice as stated in Section 1.
# Section 2 is released in the public domain using The Unlicense as stated in Section 2.

# SECTION 1

# Crypto Facilities Ltd REST API v3

# Copyright (c) 2018 Crypto Facilities

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# https://github.com/CryptoFacilities/REST-v3-Python/blob/master/cfRestApiV3Examples.py

import time
import base64
import hashlib
import hmac
import json
import urllib.request as urllib2
import urllib.parse as urllib
import ssl
import math

class cfApiMethods(object):
    def __init__(self, apiPath, apiPublicKey="", apiPrivateKey="", timeout=10, checkCertificate=True, useNonce=False):
        self.apiPath = apiPath
        self.apiPublicKey = apiPublicKey
        self.apiPrivateKey = apiPrivateKey
        self.timeout = timeout
        self.nonce = 0
        self.checkCertificate = checkCertificate
        self.useNonce = useNonce

    ##### public endpoints #####

    # returns all instruments with specifications
    def get_instruments(self):
        endpoint = "/derivatives/api/v3/instruments"
        return self.make_request("GET", endpoint)

    # returns market data for all instruments
    def get_tickers(self):
        endpoint = "/derivatives/api/v3/tickers"
        return self.make_request("GET", endpoint)

    # returns the entire order book of a futures
    def get_orderbook(self, symbol):
        endpoint = "/derivatives/api/v3/orderbook"
        postUrl = "symbol=%s" % symbol
        return self.make_request("GET", endpoint, postUrl=postUrl)

    # returns historical data for futures and indices
    def get_history(self, symbol, lastTime=""):
        endpoint = "/derivatives/api/v3/history"
        if lastTime != "":
            postUrl = "symbol=%s&lastTime=%s" % (symbol, lastTime)
        else:
            postUrl = "symbol=%s" % symbol
        return self.make_request("GET", endpoint, postUrl=postUrl)

    ##### private endpoints #####

    # returns key account information
    # Deprecated because it returns info about the Futures margin account
    # Use get_accounts instead
    def get_account(self):
        endpoint = "/derivatives/api/v3/account"
        return self.make_request("GET", endpoint)

    # returns key account information
    def get_accounts(self):
        endpoint = "/derivatives/api/v3/accounts"
        return self.make_request("GET", endpoint)

    # places an order
    def send_order(self, orderType, symbol, side, size, limitPrice, stopPrice=None, clientOrderId=None):
        endpoint = "/derivatives/api/v3/sendorder"
        postBody = "orderType=%s&symbol=%s&side=%s&size=%s&limitPrice=%s" % (
            orderType, symbol, side, size, limitPrice)

        if orderType == "stp" and stopPrice is not None:
            postBody += "&stopPrice=%s" % stopPrice

        if clientOrderId is not None:
            postBody += "&cliOrdId=%s" % clientOrderId

        return self.make_request("POST", endpoint, postBody=postBody)

    # places an order
    def send_order_1(self, order):
        endpoint = "/derivatives/api/v3/sendorder"
        postBody = urllib.urlencode(order)
        return self.make_request("POST", endpoint, postBody=postBody)

    # edit an order
    def edit_order(self, edit):
        endpoint = "/derivatives/api/v3/editorder"
        postBody = urllib.urlencode(edit)
        return self.make_request("POST", endpoint, postBody=postBody)

    # cancels an order
    def cancel_order(self, order_id=None, cli_ord_id=None):
        endpoint = "/derivatives/api/v3/cancelorder"

        if order_id is None:
            postBody = "cliOrdId=%s" % cli_ord_id
        else:
            postBody = "order_id=%s" % order_id

        return self.make_request("POST", endpoint, postBody=postBody)

    # cancel all orders
    def cancel_all_orders(self, symbol=None):
        endpoint = "/derivatives/api/v3/cancelallorders"
        if symbol is not None:
            postbody = "symbol=%s" % symbol
        else:
            postbody = ""

        return self.make_request("POST", endpoint, postBody=postbody)

    # cancel all orders after
    def cancel_all_orders_after(self, timeoutInSeconds=60):
        endpoint = "/derivatives/api/v3/cancelallordersafter"
        postbody = "timeout=%s" % timeoutInSeconds

        return self.make_request("POST", endpoint, postBody=postbody)

    # places or cancels orders in batch
    def send_batchorder(self, jsonElement):
        endpoint = "/derivatives/api/v3/batchorder"
        postBody = "json=%s" % jsonElement
        return self.make_request("POST", endpoint, postBody=postBody)

    # returns all open orders
    def get_openorders(self):
        endpoint = "/derivatives/api/v3/openorders"
        return self.make_request("GET", endpoint)

    # returns filled orders
    def get_fills(self, lastFillTime=""):
        endpoint = "/derivatives/api/v3/fills"
        if lastFillTime != "":
            postUrl = "lastFillTime=%s" % lastFillTime
        else:
            postUrl = ""
        return self.make_request("GET", endpoint, postUrl=postUrl)

    # returns all open positions
    def get_openpositions(self):
        endpoint = "/derivatives/api/v3/openpositions"
        return self.make_request("GET", endpoint)

    # sends an xbt withdrawal request
    def send_withdrawal(self, targetAddress, currency, amount):
        endpoint = "/derivatives/api/v3/withdrawal"
        postBody = "targetAddress=%s&currency=%s&amount=%s" % (
            targetAddress, currency, amount)
        return self.make_request("POST", endpoint, postBody=postBody)

    # returns xbt transfers
    def get_transfers(self, lastTransferTime=""):
        endpoint = "/derivatives/api/v3/transfers"
        if lastTransferTime != "":
            postUrl = "lastTransferTime=%s" % lastTransferTime
        else:
            postUrl = ""
        return self.make_request("GET", endpoint, postUrl=postUrl)

    # returns all notifications
    def get_notifications(self):
        endpoint = "/derivatives/api/v3/notifications"
        return self.make_request("GET", endpoint)

    # makes an internal transfer
    def transfer(self, fromAccount, toAccount, unit, amount):
        endpoint = "/derivatives/api/v3/transfer"
        postBody = "fromAccount=%s&toAccount=%s&unit=%s&amount=%s" % (
            fromAccount, toAccount, unit, amount)
        return self.make_request("POST", endpoint, postBody=postBody)

    # accountlog csv
    def get_accountlog(self):
        endpoint = "/api/history/v2/accountlogcsv"
        return self.make_request("GET", endpoint)

    def _get_partial_historical_elements(self, elementType, **params):
        endpoint = "/api/history/v2/%s" % elementType

        params = {k: v for k, v in params.items() if v is not None}
        postUrl = urllib.urlencode(params)

        return self.make_request_raw("GET", endpoint, postUrl)

    def _get_historical_elements(self, elementType, since=None, before=None, sort=None, limit=1000):
        elements = []

        continuationToken = None

        while True:
            res = self._get_partial_historical_elements(elementType, since = since, before = before, sort = sort, continuationToken = continuationToken)
            body = json.loads(res.read().decode('utf-8'))
            elements = elements + body['elements']

            if res.headers['is-truncated'] is None or res.headers['is-truncated'] == "false":
                continuationToken = None
                break
            else:
                continuationToken = res.headers['next-continuation-token']

            if len(elements) >= limit:
                elements = elements[:limit]
                break

        return elements

    def get_orders(self, since=None, before=None, sort=None, limit=1000):
        """
        Retrieves orders of your account. With default parameters it gets the 1000 newest orders.

        :param since: Timestamp in milliseconds. Retrieves orders starting at this time rather than the newest/latest.
        :param before: Timestamp in milliseconds. Retrieves orders before this time.
        :param sort: String "asc" or "desc". The sorting of orders.
        :param limit: Amount of orders to be retrieved.
        :return: List of orders
        """

        return self._get_historical_elements('orders', since, before, sort, limit)

    def get_executions(self, since=None, before=None, sort=None, limit=1000):
        """
        Retrieves executions of your account. With default parameters it gets the 1000 newest executions.

        :param since: Timestamp in milliseconds. Retrieves executions starting at this time rather than the newest/latest.
        :param before: Timestamp in milliseconds. Retrieves executions before this time.
        :param sort: String "asc" or "desc". The sorting of executions.
        :param limit: Amount of executions to be retrieved.
        :return: List of executions
        """

        return self._get_historical_elements('executions', since, before, sort, limit)

    def get_market_price(self, symbol, since=None, before=None, sort=None, limit=1000):
        """
        Retrieves prices of given symbol. With default parameters it gets the 1000 newest prices.

        :param symbol: Name of a symbol. For example "PI_XBTUSD".
        :param since: Timestamp in milliseconds. Retrieves prices starting at this time rather than the newest/latest.
        :param before: Timestamp in milliseconds. Retrieves prices before this time.
        :param sort: String "asc" or "desc". The sorting of prices.
        :param limit: Amount of prices to be retrieved.
        :return: List of prices
        """

        return self._get_historical_elements('market/' + symbol + '/price', since, before, sort, limit)

    def get_market_orders(self, symbol, since=None, before=None, sort=None, limit=1000):
        """
        Retrieves orders of given symbol. With default parameters it gets the 1000 newest orders.

        :param symbol: Name of a symbol. For example "PI_XBTUSD".
        :param since: Timestamp in milliseconds. Retrieves orders starting at this time rather than the newest/latest.
        :param before: Timestamp in milliseconds. Retrieves orders before this time.
        :param sort: String "asc" or "desc". The sorting of orders.
        :param limit: Amount of orders to be retrieved.
        :return: List of orders
        """

        return self._get_historical_elements('market/' + symbol + '/orders', since, before, sort, limit)

    def get_market_executions(self, symbol, since=None, before=None, sort=None, limit=1000):
        """
        Retrieves executions of given symbol. With default parameters it gets the 1000 newest executions.

        :param symbol: Name of a symbol. For example "PI_XBTUSD".
        :param since: Timestamp in milliseconds. Retrieves executions starting at this time rather than the newest/latest.
        :param before: Timestamp in milliseconds. Retrieves executions before this time.
        :param sort: String "asc" or "desc". The sorting of executions.
        :param limit: Amount of executions to be retrieved.
        :return: List of executions
        """

        return self._get_historical_elements('market/' + symbol + '/executions', since, before, sort, limit)

    # signs a message
    def sign_message(self, endpoint, postData, nonce=""):
        if endpoint.startswith('/derivatives'):
            endpoint = endpoint[len('/derivatives'):]

        # step 1: concatenate postData, nonce + endpoint
        message = postData + nonce + endpoint

        # step 2: hash the result of step 1 with SHA256
        sha256_hash = hashlib.sha256()
        sha256_hash.update(message.encode('utf8'))
        hash_digest = sha256_hash.digest()

        # step 3: base64 decode apiPrivateKey
        secretDecoded = base64.b64decode(self.apiPrivateKey)

        # step 4: use result of step 3 to has the result of step 2 with HMAC-SHA512
        hmac_digest = hmac.new(secretDecoded, hash_digest,
                               hashlib.sha512).digest()

        # step 5: base64 encode the result of step 4 and return
        return base64.b64encode(hmac_digest)

    # creates a unique nonce
    def get_nonce(self):
        # https://en.wikipedia.org/wiki/Modulo_operation
        self.nonce = (self.nonce + 1) & 8191
        return str(int(time.time() * 1000)) + str(self.nonce).zfill(4)

    # sends an HTTP request
    def make_request_raw(self, requestType, endpoint, postUrl="", postBody=""):
        # create authentication headers
        postData = postUrl + postBody

        if self.useNonce:
            nonce = self.get_nonce()
            signature = self.sign_message(endpoint, postData, nonce=nonce)
            authentHeaders = {"APIKey": self.apiPublicKey,
                              "Nonce": nonce, "Authent": signature}
        else:
            signature = self.sign_message(endpoint, postData)
            authentHeaders = {
                "APIKey": self.apiPublicKey, "Authent": signature}

        authentHeaders["User-Agent"] = "cf-api-python/1.0"

        # create request
        if postUrl != "":
            url = self.apiPath + endpoint + "?" + postUrl
        else:
            url = self.apiPath + endpoint

        request = urllib2.Request(url, str.encode(postBody), authentHeaders)
        request.get_method = lambda: requestType

        # read response
        if self.checkCertificate:
            response = urllib2.urlopen(request, timeout=self.timeout)
        else:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            response = urllib2.urlopen(
                request, context=ctx, timeout=self.timeout)

        # return
        return response

    # sends an HTTP request and read response body
    def make_request(self, requestType, endpoint, postUrl="", postBody=""):
        return self.make_request_raw(requestType, endpoint, postUrl, postBody).read().decode("utf-8")

# SECTION 2

# This is free and unencumbered software released into the public domain.
# 
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
# 
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import datetime
import os  # to access "variables" stored in the pipedream context

# standard settings
# you could use "api.cryptofacilities.com" if your IP is whitelisted (Settings -> API Keys -> IP Whitelist)
#apiPath = "https://www.cryptofacilities.com"
apiPath = "https://futures.kraken.com"
timeout = 20
checkCertificate = True  # when using the test environment, this must be set to "False"
useNonce = False  # nonce is optional

# check whether all keys are present
required_env = [
    "SOURCE_KRAKEN_FUTURES_KEY",
    "SOURCE_KRAKEN_FUTURES_SECRET",
    "YOUR_KRAKEN_FUTURES_KEY",
    "YOUR_KRAKEN_FUTURES_SECRET",
]
missing = [k for k in required_env if k not in os.environ]
if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

# removed "cfApi." before these methods:
cfPublic = cfApiMethods(apiPath, timeout=timeout, checkCertificate=checkCertificate)
cfSource = cfApiMethods(apiPath, timeout=timeout, apiPublicKey=os.environ["SOURCE_KRAKEN_FUTURES_KEY"], apiPrivateKey=os.environ["SOURCE_KRAKEN_FUTURES_SECRET"], checkCertificate=checkCertificate, useNonce=useNonce)
cfYour = cfApiMethods(apiPath, timeout=timeout, apiPublicKey=os.environ["YOUR_KRAKEN_FUTURES_KEY"], apiPrivateKey=os.environ["YOUR_KRAKEN_FUTURES_SECRET"], checkCertificate=checkCertificate, useNonce=useNonce)

# get general info about assets
instruments = json.loads(cfPublic.get_instruments())['instruments']
#print( [ i for i in instruments if i['symbol'] == 'PF_XBTUSD' ], '\n')

# get futures portfolio value ratio (including unrealized PnL)
source_portfolio_value = json.loads(cfSource.get_accounts())['accounts']['flex']['portfolioValue']
your_portfolio = json.loads(cfYour.get_accounts())
#print(your_portfolio,'\n')  
your_portfolio_value = your_portfolio['accounts']['flex']['portfolioValue']
print('your_portfolio_value:', your_portfolio_value, 'USD\n')

if your_portfolio_value <= 100:  # stop if your account is almost empty (which would cause strategy to behave irregularly)
    raise ValueError('Your account has < 100 USD value, causing strategy to become irregular or unreliable.')

# get current futures positions
source_positions = json.loads(cfSource.get_openpositions())['openPositions']
your_positions = json.loads(cfYour.get_openpositions())['openPositions']
#print( source_positions )

# get current prices (if script runs quickly, assume prices are still roughly the same)
tickers = json.loads(cfPublic.get_tickers())['tickers']

# adjust your portfolio to resemble source portfolio.
if source_portfolio_value <= 500:  # avoid division by zero, and also stop if source account is almost empty (which would cause strategy to behave irregularly)
    raise ValueError('The SOURCE account has < 500 USD value, causing strategy to become irregular or unreliable.')    
else:
    pfratio = your_portfolio_value / source_portfolio_value
  
    # close all open orders
    result = json.loads(cfYour.cancel_all_orders())
    if len(result['cancelStatus']['cancelledOrders']) > 0:
        print('cancel_all_orders:\n', result['result'], 'cancelled', len(result['cancelStatus']['cancelledOrders']), 'orders.\n' )
    
    # close any of your positions that no longer appear in source positions list
    for your_pos in your_positions: 
        s = your_pos['symbol']
        if len( [ p for p in source_positions if p['symbol'] == s ] ) == 0:    # if corresponding source position not found
            # send limit order to close it
            contractValueTradePrecision = [ i['contractValueTradePrecision'] for i in instruments if i['symbol'] == s ][0]
            position_adjustment = round( -1 * your_pos['size'], contractValueTradePrecision )  # avoid "sendStatus":{"status":"invalidSize"} issue    
            if abs( position_adjustment ) > 0:
                markPrice = [ t['markPrice'] for t in tickers if t['symbol'] == s ][0]
                # price must have correct precision (different from contractValueTradePrecision) avoid "sendStatus":{"status":"invalidPrice"} issue
                tickSize = [ i['tickSize'] for i in instruments if i['symbol'] == s ][0]
                if position_adjustment > 0:
                    limitPrice = math.ceil( markPrice / tickSize ) * tickSize
                else:
                    limitPrice = math.floor( markPrice / tickSize ) * tickSize
                limit_order = { 
                  "orderType": "lmt"      # simple Limit order, don't mess with post-only
                  , "symbol": s
                  , "side": ( 'buy' if position_adjustment > 0 else 'sell' )
                  , "size": abs( position_adjustment )
                  , "limitPrice": limitPrice
                  , "reduceOnly": "true"
                }
                result = cfYour.send_order_1(limit_order)
                print("closing position:\n", limit_order, '\n', result)
      #print('\n')
  
    # adjust your positions to those of the source
    for source_pos in source_positions: 
        s = source_pos['symbol']
        #print( s )
        desired_position = pfratio * source_pos['size'] * ( 1 if source_pos['side'] == 'long' else -1 )
        # find corresponding position in your account
        current_position = [ p for p in your_positions if p['symbol'] == s ]
        current_position = current_position[0]['size'] if len( current_position ) == 1 else 0   # put zero if not found
        #print( 'desired_position:', desired_position, 'current_position:', current_position )
        # send limit order
        contractValueTradePrecision = [ i['contractValueTradePrecision'] for i in instruments if i['symbol'] == s ][0]
        #print( 'contractValueTradePrecision', contractValueTradePrecision, 'decimals' )
        position_adjustment = round( desired_position - current_position, contractValueTradePrecision )  # avoid "sendStatus":{"status":"invalidSize"} issue
        #print( 'position_adjustment', position_adjustment )
        if abs( position_adjustment ) > 0:
            markPrice = [ t['markPrice'] for t in tickers if t['symbol'] == s ][0]
            # price must have correct precision (different from contractValueTradePrecision) avoid "sendStatus":{"status":"invalidPrice"} issue
            tickSize = [ i['tickSize'] for i in instruments if i['symbol'] == s ][0]
            if position_adjustment > 0:
                limitPrice = math.ceil( markPrice / tickSize ) * tickSize
            else:
                limitPrice = math.floor( markPrice / tickSize ) * tickSize
            limit_order = { 
              "orderType": "lmt" # simple Limit order, don't mess with post-only
              , "symbol": s
              , "side": ( 'buy' if position_adjustment > 0 else 'sell' )
              , "size": abs( position_adjustment )
              , "limitPrice": limitPrice
            }
            result = cfYour.send_order_1(limit_order)
            print("sent order:\n", limit_order, '\n', result)
        #print('\n')

