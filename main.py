import kiteconnect

# Initialize Kite Connect
kite = kiteconnect.KiteConnect(api_key="your_api_key")

# Function to place a MIS market order

def place_mis_order(symbol, quantity):
    try:
        # Place a market order
        order_id = kite.place_order(
            tradingsymbol=symbol,
            exchange=kiteconst.EXCHANGE_NSE,
            transaction_type=kiteconst.TRANSACTION_TYPE_BUY,
            quantity=quantity,
            order_type=kiteconst.ORDER_TYPE_MARKET,
            product=kiteconst.PRODUCT_MIS
        )
        print(f"Order placed successfully. Order ID: {order_id}")
        return order_id
    except Exception as e:
        print(f"Error placing order: {e}")

# Function to calculate P&L

def calculate_pnl(entry_price, exit_price, quantity):
    return (exit_price - entry_price) * quantity

# Example usage
if __name__ == '__main__':
    order_id = place_mis_order("INFY", 1)  # Place a market order for 1 share of INFY
    # Example P&L calculation
    entry_price = 1500  # Entry price of the stock
    exit_price = 1550   # Exit price of the stock
    pnl = calculate_pnl(entry_price, exit_price, 1)
    print(f"Profit/Loss: {pnl}")
