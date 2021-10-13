#!/usr/bin/env python

# Display the leverage of put options over time parameterized by expiration date  
# Utilize a given symbols put JSON data as written by pullputs.py 

import matplotlib.pyplot as plt 
import matplotlib.ticker as ticker
import requests
import json
from decimal import Decimal
import datetime
import json 
import os.path
import numpy as np

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


#Collect the ticker symbol of interest and fractional decline

ticker  = str(input ('Enter ticker symbol: '))

factor  = float(input ('Enter factor : '))

# Set flag to only find first stock entry
stocknotfound=1


#Check if datafile exists, open it and first repopulate the list  

testcounter=0
filename='./'+ticker.lower()+'.txt'

if(os.path.isfile(filename)):
     with open(filename) as json_file:
          insight = json.load(json_file)


# Initialize the Options Arrays

# Yearish 2021 

     x_nov_19=[]
     y_nov_19=[]

     x_dec_17=[]
     y_dec_17=[]

# Yearish 2022 

     x_jan_21=[]
     y_jan_21=[]

     x_mar_18=[]
     y_mar_18=[]

     x_apr_14=[]
     y_apr_14=[]

     for entry in insight['instruments']:

          if (entry['type']=="stock" and bool(stocknotfound)): 

               stockprice=float(entry['price'])
               stocknotfound=0
       
          if (entry['type']=="option" and  entry['price']!=0.0):

               #new_date_string = str(entry['date']+' '+entry['time'][:-3][:-3])
               #new_date = datetime.datetime.strptime(new_date_string,"%Y-%m-%d %H:%M")

               if (entry['opt_date']=="2021-11-19"):  
                    x_nov_19.append(int(float(entry['strike_price'])))
                    y_nov_19.append((float(entry['strike_price'])-float(entry['price'])-float(factor*stockprice))/float(entry['price']))

               if (entry['opt_date']=="2021-12-17"):  
                    x_dec_17.append(int(float(entry['strike_price'])))
                    y_dec_17.append((float(entry['strike_price'])-float(entry['price'])-float(factor*stockprice))/float(entry['price']))

               if (entry['opt_date']=="2022-01-21"):  
                    x_jan_21.append(int(float(entry['strike_price'])))
                    y_jan_21.append((float(entry['strike_price'])-float(entry['price'])-float(factor*stockprice))/float(entry['price']))

               if (entry['opt_date']=="2022-03-21"):  
                    x_mar_18.append(int(float(entry['strike_price'])))
                    y_mar_18.append((float(entry['strike_price'])-float(entry['price'])-float(factor*stockprice))/float(entry['price']))

               if (entry['opt_date']=="2022-04-14"):  
                    x_apr_14.append(int(float(entry['strike_price'])))
                    y_apr_14.append((float(entry['strike_price'])-float(entry['price'])-float(factor*stockprice))/float(entry['price']))

# Plot the Stock Arrays
     
     plt.plot(x_nov_19, y_nov_19, color='orange', linestyle='solid',linewidth =1, marker='o', markerfacecolor='orange', markersize=5,label='Nov 19 2021') 
     plt.plot(x_dec_17, y_dec_17, color='red', linestyle='dashed',linewidth =1, marker='+', markerfacecolor='red', markersize=5,label='Dec 17 2021') 
     plt.plot(x_jan_21, y_jan_21, color='green', linestyle='solid',linewidth =1, marker='', markerfacecolor='green', markersize=5,label ='Jan 21 2022') 
     plt.plot(x_mar_18, y_mar_18, color='blue', linestyle='dashed',linewidth =1, marker='^', markerfacecolor='blue', markersize=5,label ='Mar 18 2022') 
     plt.plot(x_apr_14, y_apr_14, color='black', linestyle='dotted',linewidth =1, marker='', markerfacecolor='black', markersize=5,label='Apr 14 2022') 


plt.xticks(rotation='vertical')  
# naming the x axis 
plt.xlabel('strike price ') 
# naming the y axis 
plt.ylabel('leverage') 
  
# giving a title to my graph 
plt.title('Option Explorations !') 

# need a legend
plt.legend(loc='upper right',bbox_to_anchor=(1.3, 1.1))  
# function to show the plot 
plt.show() 
