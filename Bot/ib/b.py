import asyncio
import datetime
import time
import concurrent.futures as cf
import multiprocessing as mp
import creds
from ib_insync import *


def bigCalculation():
    i=0
    while i<20:
        print("doig cal")
        time.sleep(1)
        i+=1
    

def onPendingTickers():
    print('.')


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    mp.set_start_method('spawn')
    executor = cf.ProcessPoolExecutor(1)
    ib = IB().connect('127.0.0.1', 7496, clientId=21)
    
    
    # a minute later...
    time2 = datetime.time(0, 12, 20)
    ib.waitUntil(time2)
    for c in [Forex(s) for s in ('USDJPY', 'USDCHF')]:
        ib.reqMktData(c)
        IB.sleep(2)
        
    
    all_groups= asyncio.gather( bigCalculation(), onPendingTickers())
    results = loop.run_until_complete(all_groups)
    
    loop.close()
    print(results)
"""
import asyncio

import ib_insync as ibi
import creds
import time

class App:

    async def run(self):
        self.ib = ibi.IB()
        with await self.ib.connectAsync('127.0.0.1', creds.port, clientId=1):
            contracts = [
                ibi.Stock(symbol, 'SMART', 'USD')
                for symbol in ['AAPL', 'TSLA', 'AMD', 'INTC']]
            for contract in contracts:
                self.ib.reqMktData(contract)

            async for tickers in self.ib.pendingTickersEvent:
                for ticker in tickers:
                    print(ticker)

    def stop(self):
        self.ib.disconnect()


app = App()
try:
    asyncio.run(app.run())
    while True:
        print("ru 1")
        time.sleep(1)
    
except (KeyboardInterrupt, SystemExit):
    app.stop()
"""