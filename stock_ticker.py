#!/usr/bin/python
import os
import re
import pytz
import paho.mqtt.client as mqtt
from bs4 import BeautifulSoup
import json
import requests
import json
from datetime import datetime
mqtthost = os.environ['MQTTHOST']
mqttport = int(os.environ['MQTTPORT'])
mqttuser = os.environ['MQTTUSER']
mqttpass = os.environ['MQTTPASS']
mqtttopic = os.environ['MQTTTOPIC']
stocksymbol = os.environ['STOCKSYMBOL']

#def on_connect(client, userdata, flags, rc):
def on_disconnect(client,userdata,rc):
    client.connected_flag=False
    client.disconnect_flag=True
    client.connect(str(mqtthost).rstrip(), str(mqttport).rstrip(), 60)
    print("disconnected")
def on_connect(client,userdata,rc):
    client.connected_flag=True
    client.disconnect_flag=False
    print("re-connected")
client = mqtt.Client()
client.username_pw_set(str(mqttuser).rstrip(),str(mqttpass).rstrip())
client.on_connect=on_connect
client.on_disconnect=on_disconnect
client.connected_flag=False
client.disconnect_flag=False
client.connect(mqtthost, mqttport, 60)
last_price=0
eastern = pytz.timezone('US/Eastern')
while True:
  stockurl="https://finance.yahoo.com/quote/"+stocksymbol
  page = requests.get(stockurl).content
  soup = BeautifulSoup(page, "html.parser")
  pattern = re.compile("root.App")
  #print(pattern)
  script = soup.find("script",text=pattern)
  #data=soup.find('script',{'type':'application/json'})
  if script:
    script_contents = script.string
    jsvar,_,jsvalue = script_contents.partition('root.App.main = ')
    left_strip=jsvalue.rsplit(';\n}',1)[0]
    data=json.loads(left_strip)
    #print("GME PRICE: " +data['context']['dispatcher']['stores']['StreamDataStore']['quoteData']['GME']['postMarketPrice']['fmt'])
    #price=data['context']['dispatcher']['stores']['StreamDataStore']['quoteData']['GME']['regularMarketPrice']['fmt']
    try:
      day=datetime.now(tz=eastern).weekday()
      now = datetime.now(tz=eastern)
      seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
      print(day)
      print(seconds_since_midnight)
      #price=data['context']['dispatcher']['stores']['QuoteSummaryStore']['price']['postMarketPrice']['fmt']
    except:
      print("couldn't get time")
      price=''
    try:
      if day < 5:
          if (seconds_since_midnight > 25200) and (seconds_since_midnight < 34200):
            price = data['context']['dispatcher']['stores']['QuoteSummaryStore']['price']['preMarketPrice']['fmt']
          if (seconds_since_midnight > 0) and (seconds_since_midnight < 25200):
            price = data['context']['dispatcher']['stores']['QuoteSummaryStore']['price']['preMarketPrice']['fmt']
          if (seconds_since_midnight > 34200) and (seconds_since_midnight <57600):
            price=data['context']['dispatcher']['stores']['StreamDataStore']['quoteData'][stocksymbol]['regularMarketPrice']['fmt']
          if (seconds_since_midnight > 57600) and (seconds_since_midnight < 86400):
           price= data['context']['dispatcher']['stores']['QuoteSummaryStore']['price']['postMarketPrice']['fmt']
      if day >=5:
        price= data['context']['dispatcher']['stores']['QuoteSummaryStore']['price']['postMarketPrice']['fmt']
      if last_price > price:
          client.publish(mqtttopic,"DOWN")
      #elif float(last_price) < float(price): 
      elif last_price < price:
          client.publish(mqtttopic,"UP")
      elif last_price == price:
          client.publish(mqtttopic,"EVEN")
      last_price=price
    except:
        print("just keep swimming")
        exit()

client.loop_forever()
