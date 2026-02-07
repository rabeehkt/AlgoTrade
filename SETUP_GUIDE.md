# AlgoTrade - Kite Connect MIS Market Order Integration

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Kite Connect credentials:

```
KITE_API_KEY=your_api_key
KITE_API_SECRET=your_api_secret
KITE_USER_ID=your_user_id
```

### 3. Get Your Credentials

1. Visit [Kite Console](https://console.kite.trade/)
2. Create an app (if not already done)
3. Get your:
   - API Key
   - API Secret
   - User ID

### 4. Authenticate

Generate your session using the official Kite Connect flow:

1. Build a `KiteConnect` client with your API key.
2. Open `kite.login_url()` in a browser and complete login.
3. Exchange the returned `request_token` for an `access_token`.
4. Pass the `access_token` into `build_kite_client(...)` from `main.py`.

### 5. Place an Order

Use the high-level helper in `main.py` or `KiteOrderManager` directly:

```python
from main import build_kite_client, place_mis_order

kite = build_kite_client(api_key="your_api_key", access_token="your_access_token")
order_id, avg_price = place_mis_order(kite, symbol="INFY", quantity=1, side="BUY")
print(order_id, avg_price)
```

## Usage Examples

### Simple Function Usage

```python
from kiteconnect import KiteConnect
from kite_orders import place_mis_market_order

# Setup kite connection
kite = KiteConnect(api_key="your_key")
# ... authenticate ...

# Place order
order_id, avg_price = place_mis_market_order(
    kite=kite,
    symbol='INFY',
    quantity=1,
    side='BUY'
)

print(f"Order placed: {order_id}")
print(f"Average price: ₹{avg_price:.2f}")
```

### Advanced Manager Usage

```python
from kite_orders import KiteOrderManager

manager = KiteOrderManager(kite)

# Place order
result = manager.place_mis_market_order(
    symbol='RELIANCE',
    quantity=2,
    side='BUY',
    tag='my_strategy'
)

# Get order details
order_details = manager._get_order_details(result['order_id'])
print(order_details)

# Get all orders
all_orders = manager.get_all_orders()

# Cancel order
manager.cancel_order(result['order_id'])
```

## File Structure

```
AlgoTrade/
├── kite_orders.py          # Order management module
├── main.py                 # Main entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Your local credentials (git ignored)
└── SETUP_GUIDE.md          # This file
```

## Key Features

✅ Place MIS market orders  
✅ Get order_id and average_price  
✅ Full order tracking  
✅ Error handling and logging  
✅ Secure credential management  
✅ Extensible for strategies  

## Testing

Run the example:

```bash
python main.py
```

## Troubleshooting

### "The requested resource was not found"
- Check your API key is correct
- Ensure your Kite app is created in Console

### "Invalid request token"
- Get a fresh request_token from the login URL
- Ensure the token hasn't expired (valid for 2 minutes)

### "Access denied"
- Verify your Kite account is active
- Check that you have trading permissions enabled

## Next Steps

1. ✅ Set up credentials
2. ✅ Test the basic example
3. 🔄 Build your trading strategy using `KiteOrderManager`
4. 📊 Add position tracking
5. 📈 Implement risk management

## Resources

- [Kite Connect Docs](https://kite.trade/docs/connect/v3/)
- [PyKiteConnect GitHub](https://github.com/zerodhatech/pykiteconnect)
- [Zerodha API Support](https://support.zerodha.com/)