from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time
import config

class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = {}
        self.orderId = None
        self.done = False
        self.nextId = None

    def error(self, reqId, errorCode, errorString):
        print(f'Error {errorCode}: {errorString}')

    def nextValidId(self, orderId):
        self.nextId = orderId
        self.done = True

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice,
                   permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print(f'Order {orderId} status: {status}')

    def openOrder(self, orderId, contract, order, orderState):
        print(f'Order opened: {orderId}')

    def execDetails(self, reqId, contract, execution):
        print(f'Order executed: {execution.orderId}')

def getContract(symbol):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    return contract

def getOrder(action, qty):
    order = Order()
    order.action = action
    order.totalQuantity = qty
    order.orderType = 'MKT'
    return order

def connectIbkr():
    app = TradeApp()
    app.connect(config.ibkrHost, config.ibkrPort, config.ibkrClientId)

    apiThread = threading.Thread(target=app.run, daemon=True)
    apiThread.start()

    timeout = 5
    startTime = time.time()
    while not app.done and time.time() - startTime < timeout:
        time.sleep(0.1)

    if not app.done:
        print("Connection timeout")
        return None

    return app

def execTrade(app, sym, action, qty):
    if not app or not app.nextId:
        print("No valid connection")
        return False

    try:
        contract = getContract(sym)
        order = getOrder(action, qty)
        
        app.placeOrder(app.nextId, contract, order)
        app.nextId += 1
        
        print(f"Order placed: {action} {qty} {sym}")
        return True
    except Exception as e:
        print(f"Trade error: {e}")
        return False

def executeTradesIbkr(trades):
    app = connectIbkr()
    if not app:
        return False

    success = True
    for trade in trades:
        if not execTrade(app, trade['symbol'], trade['action'], trade['quantity']):
            success = False

    app.disconnect()
    return success

ibkr_app = None
api_thread = None

def connectIbkr():
    global ibkr_app, api_thread
    if ibkr_app and ibkr_app.isConnected():
        print("Already connected to IBKR.")
        return ibkr_app

    ibkr_app = TradeApp()
    ibkr_app.connect(config.ibkrHost, config.ibkrPort, clientId=config.ibkrClientId)

    api_thread = threading.Thread(target=ibkr_app.run, daemon=True)
    api_thread.start()

    print("Waiting for connection...")
    if ibkr_app.done:
        if ibkr_app.isConnected():
            print("Successfully connected to IBKR.")

            ibkr_app.reqIds(-1)
            time.sleep(1)
            return ibkr_app
        else:
            print("Event set, but not connected. Check TWS/Gateway.")
            disconnectIbkr()
            return None
    else:
        print("Connection timed out. Ensure TWS/Gateway is running or API is enabled.")
        ibkr_app.disconnect()
        return None

def disconnectIbkr():
    global ibkr_app, api_thread
    if ibkr_app and ibkr_app.isConnected():
        print("Disconnecting from IBKR...")
        ibkr_app.disconnect()
        if api_thread and api_thread.is_alive():
            api_thread.join(timeout=5)
        print("Disconnected.")
    ibkr_app = None
    api_thread = None

def executeTradesIbkr(tradesToMake):
    if not tradesToMake:
        print("No trades to execute.")
        return

    app = connectIbkr()
    if not app or not app.isConnected():
        print("Cannot execute trades: not connected.")
        return

    print("\nExecuting trades with IBKR:")
    executedOrderIds = []
    for trade in tradesToMake:
        if trade['action'].upper() in ['BUY', 'SELL'] and trade['quantity'] > 0:
            print(f"Attempting to {trade['action']} {trade['quantity']} of {trade['symbol']}")
            orderId = app.placeOrder(app.nextId, getContract(trade['symbol']), 
                                   getOrder(trade['action'], trade['quantity']))
            app.nextId += 1
            if orderId:
                executedOrderIds.append(orderId)
            time.sleep(1)
        elif trade['action'].upper() == 'HOLD':
            print(f"Holding {trade['symbol']}.")
        else:
            print(f"Skipping invalid trade action for {trade['symbol']}: {trade['action']}")

    print("Waiting a few seconds for order statuses...")
    time.sleep(10)
    print("Order Statuses Received:")
    for oid, statusInfo in app.order_statuses.items():
        print(f"Order ID {oid}: {statusInfo}")

    disconnectIbkr()
    return executedOrderIds