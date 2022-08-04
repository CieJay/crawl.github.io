#!/usr/bin/env python
# coding: utf-8

# In[3]:


from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import html5lib
import re
from datetime import timedelta
from openpyxl import Workbook


#-------------------------------------------------------------------------------
url = 'https://www.twse.com.tw/zh/brokerService/brokerServiceAudit'
html = requests.get(url)
sp = BeautifulSoup(html.text,'html5lib')

td = sp.find_all('td')
total_brokerage_code=[]
for i in td:
    total_brokerage_code.append(i.text)

brokerage_code = []
for i in range(0,410,6):  # 券商代號
    brokerage_code.append(total_brokerage_code[i])

brokerage_name=[]
for i in range(1,415,6):
    brokerage_name.append(total_brokerage_code[i])


#-------------------------------------------------------------------------------

start_time = pd.to_datetime('2022-07-04')
total_time = []
for i in range(2): #天數
    total_time.append((start_time + timedelta(days=i)).strftime('%Y-%m-%d'))
#-------------------------------------------------------------------------------

date_run=0
empty = pd.DataFrame(np.zeros([0,8]))
empty.rename(columns={0:'日期',1:'券商代號',2:'券商',3:'股票代號',4:'股票',5:'買進張數',6:'賣出張數',7:'差額'},inplace=True)

def get(date,code):
    df = pd.DataFrame(np.zeros([100,8]))
    df.rename(columns={0:'日期',1:'券商代號',2:'券商',3:'股票代號',4:'股票',5:'買進張數',6:'賣出張數',7:'差額'},inplace=True)
    url = f'http://newjust.masterlink.com.tw/z/zg/zgb/zgb0.djhtm?a={code}&b={code}&c=E&e={date}&f={date}'
    html = requests.get(url)
    sp = BeautifulSoup(html.text,'html5lib')

    td = sp.find_all('td',class_='t3n1')
    buy_sell_data = []
    for i in td:
        buy_sell_data.append(re.sub('[,]','',i.text))
        buy_sell_data = list(map(int,buy_sell_data))
        
    name = sp.find_all('td',class_='t4t1')
    corp = []
    corp_code = []
    for i in name:
        corp_code.append(re.sub('\D','',i.text)) # 股票代碼
        corp.append(re.sub(u'([^\u4e00-\u9fa5])','',i.text)) # 股票名稱

    buy_sell = 0
    corp_run = 0
    try:
        for i in range(len(df)*2):
            df.iloc[i,0] = total_time[date_run]
            df.iloc[i,1] = brokerage_code[code_run]
            df.iloc[i,2] = brokerage_name[code_run]
            df.iloc[i,3] = corp_code[corp_run][1:5]  # 股票代碼
            df.iloc[i,4] = corp[corp_run] # 股票名稱
            corp_run += 1
            for j in range(5,8):
                df.iloc[i,j] = buy_sell_data[buy_sell]
                buy_sell += 1
    except:
        pass
    df =(df.T.loc[:,(df!=0).any(axis=1)]).T
    return(df)
    
for date in total_time:
    print(date)
    code_run = 0
    for code in brokerage_code:
        empty = pd.concat([empty,get(date,code)])
        print(code)
        code_run += 1
    date_run += 1
    
empty.to_csv('data.csv')

