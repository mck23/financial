#!/usr/bin/env python


# Code to Collect PUT Options over a Defined Range of Strike Prices 
# Write this as a JSON structure to a File Corresponding to the Ticker 
# Utilizes TDAmeritade's API Service 
# Please reference https://developer.tdameritrade.com/content/getting-started
   
import requests
import json
from decimal import Decimal
import datetime
import json 
import os.path
from decouple import config


# Define Datastructure 
# Insight will be a dictionary of json objects with the following structure
insight = {}
insight['instruments'] = []

def list_append(list, date, time, datetime, symbol, type, price, strike_price="", opt_date=""):
     list.append({
          'date': date,
          'time': time,
	  'datetime': datetime,
	  'symbol': symbol,
          'type': type,
	  'price': price,
	  'strike_price': strike_price,
	  'opt_date': opt_date
      })



# Request the Ticker Symbol and Trading Range of Interest

ticker  = str(input ('Enter ticker symbol: '))
low  = int(input ('Enter lowest option price: '))
high = int(input ('Enter highest option price: '))

# Check if datafile exists, open it and first repopulate the list  

filename='./'+ticker.lower()+'.txt'
if(os.path.isfile(filename)):
     with open(filename) as json_file:
          insight = json.load(json_file)

# Regenerate the Access Token

url = "https://api.tdameritrade.com/v1/oauth2/token"

# Pull the Refresh Token from .env 
refresh_token = config('refresh_token',default='')
client_id = config('client_id',default='')

d = {'grant_type': 'refresh_token','refresh_token': refresh_token,'client_id': client_id,}
new_auth = requests.post(url, data=d)


# Convert the access token structure to JSON 
json_new_auth=new_auth.json()
#print (new_auth)
new_auth_token = json_new_auth['access_token']

# Discover the Security's Financial Data at the time of execution 

for current in range(low, high+1, 5) : 

    url = "https://api.tdameritrade.com/v1/marketdata/chains?symbol="+ticker+"&contractType=PUT&&includeQuotes=TRUE&range=SBK&fromDate=2020-09-01&toDate=2022-12-31&expMonth=ALL&optionType=ALL&strike="+str(current)
    
    headers = {
        'Authorization': "Bearer " + new_auth_token, 
        'cache-control': "no-cache",
        }
    
    # Pull the Options Date at the Given Strike 
    jtob = requests.request("GET", url, headers=headers)

    #Debug  
    #print(jtob.text)
    #print ('----------------------------')
    #print ('----------------------------')
    #print ('----------------------------')
   
    # Convert to JSON Data
    blocklist = json.loads(jtob.text)
   
    # Datetime Values 
    now = datetime.datetime.now().strftime("%Y-%b-%d %H:%M")
    query_date=str(datetime.datetime.now().date())
    query_time=datetime.datetime.now().time().strftime("%H:%M:%S")
 
    # Capture the Fundamentals about the Option
    fundamental = blocklist['symbol']
    last_trade = blocklist['underlying']['last'] 
    list_append(insight['instruments'],query_date, query_time, now, fundamental, "stock", last_trade)
    
    # For each Block in Blocklist, Write each Option Price of Interest  
    
    for date in blocklist['putExpDateMap']:
         trunc_date=date.split(":")[0]
         for strike in blocklist['putExpDateMap'][date]:
              for value in blocklist['putExpDateMap'][date][strike]:
                   list_append(insight['instruments'],query_date, query_time, now, fundamental, "option", value['last'],strike,trunc_date)

with open(filename, 'w') as outfile:
    json.dump(insight, outfile)
    
