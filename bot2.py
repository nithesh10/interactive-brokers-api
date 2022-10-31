from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum


class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    #def tickPrice(self, reqId, tickType, price, attrib):
        #print("Tick Price. Ticker Id:", reqId, "tickType:", TickTypeEnum.to_str(tickType), "Price:", price, end=' ')
    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 1 and reqId == 2:
            print('The current ask price is: ', price)

    def tickSize(self, reqId, tickType, size):
        print("Tick Size. Ticker Id:", reqId, "tickType:", TickTypeEnum.to_str(tickType), "Size:", size)
        #if tickType == 2 and reqId == 1:
        #   print('The current ask price is: ', price)

def main():
    app = TestApp()

    app.connect("127.0.0.1", 7496, 0)

    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    contract.primaryExchange = "NASDAQ"


    try:
        app.reqMarketDataType(1)  # switch to delayed-frozen data if live is not available
        
        marketData=app.reqMktData(1, contract, "", False, False, [])
        

        
    except Exception:
        marketData=0
    
        
    else:
        s=app.reqMarketDataType(4)  # switch to delayed-frozen data if live is not available
        marketData=app.reqMktData(1, contract, "", False, False, [])
        
        
    
    finally:
        print (marketData)



    app.run()


if __name__ == "__main__":
    main()