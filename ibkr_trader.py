from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time
import config

class IBKRTraderApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextOrderId = None
        self.connected_event = threading.Event()
        self.order_status_event = threading.Event() # Wait for order status
        self.order_statuses = {} # Store order statuses

    def error(self, reqId, errorCode, errorString, advancedOrderReject=""):
        super().error(reqId, errorCode, errorString, advancedOrderReject)
        # Common errors:
        if errorCode not in [2104, 2106, 2158]: # Ignore informational messages
             print(f"IBKR Error. ID: {reqId}, Code: {errorCode}, Msg: {errorString}, Advanced: {advancedOrderReject or ''}")
        if errorCode in [502, 504, 1100]:
            self.connected_event.clear() # Signal disconnection

    def connectionClosed(self):
        super().connectionClosed()
        print("IBKR Connection Closed.")
        self.connected_event.clear()

    def connectAck(self):
        super().connectAck()
        print("IBKR Connected.")
        self.connected_event.set()

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextOrderId = orderId
        print(f"Next valid Order ID: {orderId}")
        # If not connected yet, may be the first signal of successful partial connection.
        if not self.connected_event.is_set(): 
             print("Received NextValidId, assuming connection is progressing.")
             

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId,
                    parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId,
                            parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        print(f"OrderStatus. Id: {orderId}, Status: {status}, Filled: {filled}, "
              f"Remaining: {remaining}, AvgFillPrice: {avgFillPrice}")
        self.order_statuses[orderId] = {
            "status": status, "filled": filled, "remaining": remaining, "avgFillPrice": avgFillPrice
        }
        if status in ["Filled", "Cancelled", "ApiCancelled", "Inactive"]:
            self.order_status_event.set() # Signal that a final status is reached for this order

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        print(f"OpenOrder. PermID: {order.permId}, ClientID: {order.clientId}, OrderID: {orderId}, "
              f"Account: {order.account}, Symbol: {contract.symbol}, SecType: {contract.secType}, "
              f"Exchange: {contract.exchange}, Action: {order.action}, OrderType: {order.orderType}, "
              f"TotalQty: {order.totalQuantity}, Status: {orderState.status}")
        self.order_statuses[orderId] = {"status": orderState.status}


    def _create_contract(self, symbol, sec_type='STK', exchange='SMART', currency='USD'):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = sec_type
        contract.exchange = exchange
        contract.currency = currency
        # Specify primaryExchange, EXAMPLE, NASDAQ, ARCA, NYSE
        if sec_type == 'STK':
            contract.primaryExchange = "NASDAQ" # Or other 
        return contract

    def _create_market_order(self, action, quantity):
        order = Order()
        order.action = action # "BUY" or "SELL"
        order.orderType = "MKT" # Market Order
        order.totalQuantity = quantity
        order.transmit = True # Transmit order immediately
        return order

    def place_trade(self, symbol, action, quantity):
        if self.nextOrderId is None:
            print("Error: nextOrderId not set. Cannot place trade.")
            # Requesting next valid ID often helps if it's None 
            self.reqIds(-1) # Request next valid ID
            time.sleep(1) 
            if self.nextOrderId is None:
                 print("Still no valid order ID. Check connection and TWS/Gateway.")
                 return None

        contract = self._create_contract(symbol)
        order = self._create_market_order(action.upper(), quantity) # Ensure action is uppercase

        current_order_id = self.nextOrderId
        print(f"Placing {action} order for {quantity} of {symbol} with ID {current_order_id}...")
        self.placeOrder(current_order_id, contract, order)
        self.nextOrderId += 1 # Increment the next order

        # Wait for order status update
        self.order_status_event.clear()
        if self.order_status_event.wait(timeout=30): # Wait up to 30 seconds before timing out
            print(f"Order {current_order_id} reached a terminal status or timeout.")
        else:
            print(f"Timeout waiting for order status for {current_order_id}.")
        return current_order_id


# Global app instance for simplicity in this program 
ibkr_app = None
api_thread = None

def connect_ibkr():
    global ibkr_app, api_thread
    if ibkr_app and ibkr_app.isConnected():
        print("Already connected to IBKR.")
        return ibkr_app

    ibkr_app = IBKRTraderApp()
    ibkr_app.connect(config.IBKR_HOST, config.IBKR_PORT, clientId=config.IBKR_CLIENT_ID)

    # Start the EClient processing loop 
    api_thread = threading.Thread(target=ibkr_app.run, daemon=True)
    api_thread.start()

    # Wait for connection to be made
    print("Waiting for IBKR connection...")
    if ibkr_app.connected_event.wait(timeout=10): # Wait up to 10 seconds before timing out
        if ibkr_app.isConnected():
            print("Successfully connected to IBKR.")

            ibkr_app.reqIds(-1)
            time.sleep(1) # Give a second for nextValidId to arrive
            return ibkr_app
        else:
            print("Connection event set, but not connected. Check TWS/Gateway and logs.")
            disconnect_ibkr()
            return None
    else:
        print("IBKR connection timed out. Ensure TWS/Gateway is running and API is enabled.")
        ibkr_app.disconnect() # Clean up
        return None


def disconnect_ibkr():
    global ibkr_app, api_thread
    if ibkr_app and ibkr_app.isConnected():
        print("Disconnecting from IBKR...")
        ibkr_app.disconnect()
        if api_thread and api_thread.is_alive():
            api_thread.join(timeout=5) # Wait for thread to finish
        print("Disconnected.")
    ibkr_app = None
    api_thread = None


def execute_trades_ibkr(trades_to_make):

    # Connects to IBKR and executes the list of trades.
    if not trades_to_make:
        print("No trades to execute.")
        return

    app = connect_ibkr()
    if not app or not app.isConnected():
        print("Cannot execute trades: IBKR not connected.")
        return

    print("\nExecuting trades via IBKR:")
    executed_order_ids = []
    for trade in trades_to_make:
        if trade['action'].upper() in ['BUY', 'SELL'] and trade['quantity'] > 0:
            print(f"Attempting to {trade['action']} {trade['quantity']} of {trade['symbol']}")
            order_id = app.place_trade(trade['symbol'], trade['action'], trade['quantity'])
            if order_id:
                executed_order_ids.append(order_id)
            time.sleep(1) # Small delay between orders, as recommended by IKBR
        elif trade['action'].upper() == 'HOLD':
            print(f"Holding {trade['symbol']}.")
        else:
            print(f"Skipping invalid trade action for {trade['symbol']}: {trade['action']}")

    # Keep connection alive to receive order statuses, then disconnect
    print("Waiting a few seconds for final order statuses...")
    time.sleep(10) # Wait for order status messages
    print("IBKR Order Statuses Received:")
    for oid, status_info in app.order_statuses.items():
        print(f"Order ID {oid}: {status_info}")

    disconnect_ibkr()
    return executed_order_ids


if __name__ == '__main__':
    # Example usage for testing
    # Ensure you are connected to a PAPER TRADING account for testing.
    print("Starting IBKR trader module test...")

    # Create some dummy trades for testing
    sample_trades = [
        {'action': 'BUY', 'symbol': 'AAPL', 'quantity': 1, 'reason': 'Test buy'}, # Use a low quantity for paper testing
        # {'action': 'SELL', 'symbol': 'MSFT', 'quantity': 1, 'reason': 'Test sell'} # Example sell
    ]
    # Before running, ensure:
    # 1. TWS or Gateway is running.
    # 2. API settings are enabled (e.g., "Enable ActiveX and Socket Clients").
    # 3. Correct host/port/clientId in config.py (use paper trading port).

    user_confirmation = input("This will attempt to connect to IBKR and place trades. Are you sure? (yes/no): ")
    if user_confirmation.lower() == 'yes':
        print("Proceeding with IBKR trade execution test...")
        executed_ids = execute_trades_ibkr(sample_trades)
        if executed_ids:
            print(f"Executed Order IDs: {executed_ids}")
        else:
            print("No orders were processed or executed.")
    else:
        print("IBKR trade execution test cancelled by user.")

    # Make sure to disconnect if script ends abruptly or in an interactive session
    if ibkr_app and ibkr_app.isConnected():
        disconnect_ibkr()