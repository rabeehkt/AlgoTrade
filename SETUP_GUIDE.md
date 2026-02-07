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

Run the main script to get the login URL:

```bash
python main.py
```

This will print a login URL. Open it in your browser and complete the Kite login.

After login, you'll be redirected with a `request_token` in the URL.

### 5. Set Session Token

In `main.py`, uncomment and update:

```python
request_token = "your_request_token_from_redirect"
api_secret = "your_api_secret"
set_kite_session(kite, request_token, api_secret)
```

Then run again:

```bash
python main.py
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