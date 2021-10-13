#!/usr/bin/env python

# A simple trading bot with a strategy to profit from small percentage variations  
# The target securitys are those with relatively static high / low bands
# The bot does not determine the target security.  This can be determined from standard quantative analysis tools.   
# This Utilizes TDAmeritade's API Service 
# Please reference https://developer.tdameritrade.com/content/simple-auth-local-apps

import requests
import json
from decimal import Decimal
#from datetime import datetime, time, date
from datetime import datetime
import json 
import os.path
import time
from numpy import random
import math 
from decouple import config

# Define varibles and defaults
fixed_delay = 27 
random_max = 27
start_hour = 5
start_minute = 0
end_hour = 14
end_minute = 0
start_time = int(start_hour)*60 + int(start_minute)
end_time = int(end_hour)*60 + int(end_minute)
current_time =  datetime.now().hour*60 +datetime.now().minute
owned = False

if start_time <= current_time and end_time >= current_time:
    print('True in the time window')


# Pull the Refresh Token from .env
refresh_token = config('refresh_token',default='')
client_id = config('client_id',default='') 



ticker  = str(input ('Enter ticker symbol: '))
print (ticker)

entry_max  = str(input ('Enter maximum purchase price: '))
entry_price=float(entry_max)
print (entry_price)
#Market value none owned until we verify some is
market_value=0

# safe initializations 
average_price=100.00
last_price = 0.00


while (True):


    current_time =  datetime.now().hour*60 +datetime.now().minute

    if start_time <= current_time and end_time >= current_time:
        print('True in the time window')
    else:
        print('Not in the time window')

    # Delay at least a bit 
    time.sleep(fixed_delay)
    random_delay=random.randint(0,random_max)
    time.sleep(random_delay)
    print('random delay' + str(random_delay))

    # Obtain the new token because it expires often

    url = "https://api.tdameritrade.com/v1/oauth2/token"



    d = {'grant_type': 'refresh_token','refresh_token': refresh_token,'client_id': client_id,}
    new_auth = requests.post(url, data=d)

    json_new_auth=new_auth.json()
    print ( "Here comes the JSON access token")
    #print (new_auth)
    
    new_auth_token = json_new_auth['access_token']
    print (new_auth_token)
 
 # Discover owned positions      
     
    account_number = config('account_number',default='')

    url = "https://api.tdameritrade.com/v1/accounts/"+account_number+"?fields=positions"
    
    headers = {
            'Authorization': "Bearer " + new_auth_token, 
            'cache-control': "no-cache",
    }
 
    discovered_positions = requests.request("GET", url, headers=headers)
    json_discovered=json.loads(discovered_positions.text) 
    
    print ('Discovered positions')
    #print(discovered_positions)
    #print(json_discovered)
    #print(json_discovered['securitiesAccount'])
    #print("-----------------------")
    #print(json_discovered['securitiesAccount']['positions']) 
       
   
    for position in json_discovered['securitiesAccount']['positions']:
       
        #print(position['instrument']['symbol'])
        #print(position['averagePrice'])
        #print(position['longQuantity']) 
        #print(position['currentDayCost']) 
        if  (position['instrument']['symbol']== ticker): 
            print( ticker + ' exists')
            print(position['instrument']['symbol'])
            average_price = position['averagePrice']
            print('average price ' + str(average_price))
            number_shares = position['longQuantity']
            print('number of shares ' + str(number_shares))
            #print('current day cost ' + str(position['currentDayCost']))
            market_value=position['marketValue']
            print('marketValue '+str(market_value))
            owned_price = market_value/number_shares
            print('calculated cost per share '+ str(owned_price))
            owned = True
        else:
            print('Do not do anything')  


# Check if it is time to sell or buy  
    print('Check based on ownership ')
    time.sleep(fixed_delay)
    random_delay=random.randint(fixed_delay)
    time.sleep(random_delay)
    print('random delay' + str(random_delay))

    if (not owned):
        url="https://api.tdameritrade.com/v1/marketdata/"+ticker+"/quotes"        

        headers = {
               'Authorization': "Bearer " + new_auth_token, 
               'cache-control': "no-cache",
        }

    
    # Check current market price 
        market_price = requests.request("GET", url, headers=headers)
        current_price =json.loads(market_price.text)
        print(current_price) 
        last_price = current_price[ticker]['lastPrice']
        print('the last price was ' + str(last_price))
        buy_price = min(last_price - .01,entry_price)
        shares_to_buy = max(100,math.floor(int(market_value/(buy_price))))
        print('number of shares to buy ' + str(shares_to_buy))
        
# Buy shares        
        
        url = "https://api.tdameritrade.com/v1/accounts/"+account_number+"/orders"
    
    #    url = "https://api.tdameritrade.com/v1/accounts/150466852/orders"

        headers = {
               'Authorization': "Bearer " + new_auth_token, 
               'Content-Type': 'application/json'
        }


        buy_dictionary = {
            "orderType": "LIMIT",
            "session": "NORMAL",
            "duration": "FILL_OR_KILL",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                 {
                    "instruction": "Buy",
                    "quantity": shares_to_buy,
                    "instrument": {
                         "symbol": ticker,
                         "assetType": "EQUITY"
                    }
                } 
            ],
            "price":buy_price 
         } 
        payload = json.dumps(buy_dictionary)
        print(payload)
        buy_response = requests.request("POST", url, headers=headers, data=payload)
        if (buy_response.status_code == 200 or buy_response.status_code == 201):
            owned = True
            print('buy response ' + str(buy_response.status_code))
        #print(json.loads(buy_response.text))

# Check if it's time to sell  
    elif ( last_price  > 1.015*average_price ):

        print('it is time to sell')
        # we only reach this if we own the shares
        shares_to_sell =  int(number_shares)
        print('shares to sell' + shares_to_sell)
        sell_price = last_price

        url = "https://api.tdameritrade.com/v1/accounts/150466852/orders"
        headers = {
               'Authorization': "Bearer " + new_auth_token, 
               'Content-Type': 'application/json'
        }


        sell_dictionary = {
            "orderType": "LIMIT",
            "session": "NORMAL",
            "duration": "FILL_OR_KILL",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                 {
                    "instruction": "Sell",
                    "quantity": shares_to_sell,
                    "instrument": {
                         "symbol": ticker,
                         "assetType": "EQUITY"
                    }
                } 
            ],
            "price": sell_price 
         } 
        payload = json.dumps(sell_dictionary)
        print(payload)
        sell_response = requests.request("POST", url, headers=headers, data=payload)
        print('sell response ' + str(sell_response.status_code))
        print(sell_response.text)
        if (sell_response.status_code == 200 or sell_response.status_code == 201):
            # owned = False
            owned = False
            print('sell response ' + str(sell_response.status_code))
            print('setting ownership to False')

