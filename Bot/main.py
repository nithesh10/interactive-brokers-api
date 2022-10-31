
import random
from ib_insync import *
import pandas as pd
import time
import creds
import threading
import multiprocessing  
util.startLoop()  # uncomment this line when in a notebook
import asyncio





ib = IB()
contract = Forex('EURUSD')
contract = Crypto(symbol='ETH', exchange='PAXOS', currency='USD')
#contract=Stock(symbol='AAPL')  
class TrailOrder(Order):

    def __init__(self, action: str, totalQuantity: float, trailStopPrice: float,
                 **kwargs):
        Order.__init__(
            self, orderType='TRAIL', action=action,
            totalQuantity=totalQuantity, trailStopPrice=trailStopPrice, **kwargs)

def login():
    #random_id = random.randint(0, 9999)
    random_id=0
    ibs=ib.connect('127.0.0.1', creds.port, clientId=random_id)
    return ibs
def isconnected(ib):
    if(ib.isConnected()):
        print("connected")
        ibs=ib
    else:
        print("logging in again")
        ibs=login()
    return ibs
def get_historic_data(contract):
    bars = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='1 D',
        barSizeSetting='1 min', whatToShow='MIDPOINT', useRTH=True)

    # convert to pandas dataframe:
    df = util.df(bars)
    print(df)
    return df
def Myround(x, base=5):
    return base * round(x/base)
def myround(x, prec=2, base=.05):
    return round(base * round(float(x)/base),prec)
def get_bid_ask(contract):
    while True:
        trig="wait"
        data = ib.reqTickers(contract)
        print(data)
        ask=data[0].askSize
        bid=data[0].bidSize
        ltp=data[0].marketPrice()
        min_Tick=data[0].minTick
        
        print('ask_quantity: ',ask)
        print('bid_quantity: ',bid)
        print('market_price: ',ltp)
        print('close_price: ', data[0].close)
        print('last_price: ', data[0].last)
        print('min_tick', min_Tick)

        diff=bid-ask
        bid_diff=(bid-ask)*100/bid
        ask_diff=(ask-bid)*100/ask
        print(bid_diff,ask_diff)
        if(bid_diff >=creds.bid_ask_perc):
            trig="buy"
            print("buy triggered")
            return(ask,bid,ltp,trig,min_Tick)
        elif(ask_diff >=creds.bid_ask_perc):
            trig="sell"
            print("sell triggered")
            return(ask,bid,ltp,trig,min_Tick)
        else:
            trig="wait"


def place_limit_order(ib,contract,trig,ltp,bid,ask,min_Tick,tr_stp):
    global lmt_ord
    global stp_ord
    global stp_trd_buy
    global stp_trd_sell
    ib=isconnected(ib)
    ib.qualifyContracts(contract)
    quantity=int(creds.amt_per_trade/ltp)
    d=((creds.limit_perc/100)*ltp)

    if(trig=="buy"):
        order = LimitOrder('BUY',quantity, myround(ltp+d,4,min_Tick))
        print(f"order sent to exchange \n ltp:- {ltp} buy limit order {myround(ltp+d,4,min_Tick)}")
        
    elif(trig=="sell"):
        order = LimitOrder('SELL',quantity, myround(ltp-d,4,min_Tick))
        print(f"order sent to exchange \n ltp:- {ltp} sell limit order {myround(ltp-d,4,min_Tick)}")
    trade = ib.placeOrder(contract, order)

    while not trade.isDone():
        ib.sleep(1)
    print("trade placed successfully")
    lmt_ord.append(order)
    if(tr_stp!=0):
        print("placing stoploss")
        s=((creds.sl_perc/100)*ltp)
        if(trig=="buy"):
            order = TrailOrder(action='SELL',totalQuantity=quantity,trailStopPrice=myround(ltp-s,4,min_Tick),trailingPercent=creds.trailing_perc)
            trades = ib.placeOrder(contract, order)
            stp_trd_buy.append(trades)
        elif(trig=="sell"):
            order = TrailOrder(action='BUY',totalQuantity=quantity,trailStopPrice=myround(ltp+s,4,min_Tick),trailingPercent=creds.trailing_perc)
            trades = ib.placeOrder(contract, order)
            stp_trd_sell.append(trades)
        stp_ord.append(order)
        
    if(tr_stp==0):
        ib.cancelOrder(stp_ord[-1])


ib=login()
qq=0 
pos=0
dir=0
lmt_ord=[]
stp_ord=[]
stp_trd_buy=[]
stp_trd_sell=[]
while True:
    ib=isconnected(ib)
    t=0
    pos=0
    while t<=creds.timer:
        tr_stp=1
        ask,bid,ltp,trig,min_Tick=get_bid_ask(contract)
        for tra in stp_trd_buy:
            if(tra.isDone()):
                qq-=1
        for tra in stp_trd_sell:
            if(tra.isDone()):
                qq+=1
                
        if((pos!=-1 and trig=="sell" and qq>-creds.overall_trades) or (pos!=1 and trig=="buy" and qq<creds.overall_trades)):
            if((dir==1 and trig=="sell") or (dir==-1 and trig=="buy")):
                tr_stp=0
            place_limit_order(ib,contract,trig,ltp,bid,ask,min_Tick,tr_stp)
            if(trig=="buy"):
                qq+=1
                if( tr_stp!=0 ):
                    pos=1
                    dir=1
            elif(trig=="sell"):
                qq-=1
                if(tr_stp!=0):
                    pos=-1
                    dir=-1
            if(qq==0):
                dir=0
                pos=0
            print("pos")
            p=ib.positions()
            print(p)
        t+=1
        time.sleep(1)