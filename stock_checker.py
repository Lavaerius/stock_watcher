#!/usr/bin/python
import re
import paho.mqtt.client as mqtt
from bs4 import BeautifulSoup
import json
import requests
import json
from datetime import datetime
#def on_connect(client, userdata, flags, rc):

last_price=0
while True:
  page = requests.get("https://finance.yahoo.com/quote/GME").content
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
      day=datetime.now().weekday()
      now = datetime.now()
      seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
      #price=data['context']['dispatcher']['stores']['QuoteSummaryStore']['price']['postMarketPrice']['fmt']
    except:
      print("couldn't get time")
      price=''
    try:
      if day < 5:
          if (seconds_since_midnight > 25200) and (seconds_since_midnight < 34200):
            price = data['context']['dispatcher']['stores']['QuoteSummaryStore']['price']['preMarketPrice']['fmt']
            print("premarkt: "+ price)
          if (seconds_since_midnight > 34200) and (seconds_since_midnight <57600):
            price=data['context']['dispatcher']['stores']['StreamDataStore']['quoteData']['GME']['regularMarketPrice']['fmt']
            print("markt: "+ price)
          if (seconds_since_midnight > 57600) and (seconds_since_midnight < 72000):
           price= data['context']['dispatcher']['stores']['QuoteSummaryStore']['price']['postMarketPrice']['fmt']
           print("postmarkt: "+ price)
      if day >=5:
        price= data['context']['dispatcher']['stores']['QuoteSummaryStore']['price']['postMarketPrice']['fmt']
    except:
        print("just keep swimming")

