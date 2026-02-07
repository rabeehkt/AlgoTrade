import logging
import datetime
from typing import List, Dict, Any, Optional
from config import CONFIG
from orb_strategy import OrbStrategy
from kiteconnect import KiteConnect

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("Backtest")

class BacktestKiteClient:
    """
    Mock Kite Client for Backtesting.
    Serves historical data from memory instead of making API calls.
    """
    def __init__(self, historical_data: List[Dict[str, Any]]):
        self.data = historical_data
        self.current_index = 0
        self.instrument_token_map = {} # Map symbol to token

    def set_current_index(self, index: int):
        self.current_index = index

    @property
    def current_candle(self):
        return self.data[self.current_index]

    def instruments(self, exchange: str):
        # Return a dummy list or the minimal needed
        # We can implement a simple lookup if needed
        return [{"tradingsymbol": CONFIG.trading_pair.split(":")[-1], "instrument_token": 256265}]

    def historical_data(self, instrument_token: int, from_date: datetime.datetime, to_date: datetime.datetime, interval: str, continuous: bool = False, oi: bool = False) -> List[Dict[str, Any]]:
        """
        Filter in-memory data for the requested range.
        """
        # In this simple backtest, we assume 'data' is 1-minute data for the whole day.
        # We verify if the requested range is within our data.
        
        filtered_data = []
        for candle in self.data:
            # Check if candle is within range [from_date, to_date)
            # Kite API 'to_date' behavior might need checking, usually inclusive?
            # Doing a simple check here.
            
            # Ensure candle['date'] is datetime (it comes as datetime from kiteconnect)
            c_date = candle['date']
            # Make sure timezones match if needed (Kite returns offset-aware)
            
            if from_date <= c_date <= to_date:
                filtered_data.append(candle)
                
        return filtered_data

    def quote(self, instrument_token: str):
        # Return current candle close as price
        price = self.current_candle['close']
        symbol = CONFIG.trading_pair
        return {symbol: {'last_price': price}}




# Global cache for instruments to avoid repeated calls in batch mode
INSTRUMENTS_CACHE = None

def get_instrument_token(kite, symbol):
    global INSTRUMENTS_CACHE
    if INSTRUMENTS_CACHE is None:
        try:
            print("Fetching instruments (once)...")
            INSTRUMENTS_CACHE = kite.instruments("NSE")
        except Exception as e:
            print(f"Error fetching instruments: {e}")
            return None

    symbol_only = symbol.split(":")[-1]
    for instr in INSTRUMENTS_CACHE:
        if instr['tradingsymbol'] == symbol_only:
            return instr['instrument_token']
    return None


def run_backtest(target_date: str) -> Dict[str, Any]:
    """
    Run backtest for a specific date across all configured stocks.
    target_date: Format 'YYYY-MM-DD'
    Returns: Dictionary with 'pnl', 'trades', 'status'
    """
    print(f"--- Backtest for {target_date} ---")
    
    if not CONFIG.api_key or not CONFIG.access_token:
        print("ERROR: Credentials missing in config.py")
        return {'status': 'error', 'pnl': 0, 'trades': 0}

    # 1. Initialize Real Kite Client to fetch data
    real_kite = KiteConnect(api_key=CONFIG.api_key)
    real_kite.set_access_token(CONFIG.access_token)
    
    # 2. Fetch Data for ALL Stocks
    # Store in a dict: stock_data[symbol] = [candles...]
    stock_data = {}
    
    # Resolve tokens
    # print("Resolving Instrument Tokens...")
    token_map = {} # symbol -> token
    
    for symbol in CONFIG.nifty_50_symbols:
        token = get_instrument_token(real_kite, symbol)
        if token:
            token_map[symbol] = token
        else:
            print(f"Could not resolve token for {symbol}")
         
    # print(f"Resolved {len(token_map)} / {len(CONFIG.nifty_50_symbols)} stocks.")
    
    # Fetch History
    # print("Fetching historical data for all stocks...")
    from_date = f"{target_date} 09:15:00"
    to_date = f"{target_date} 15:30:00"
    
    import time
    
    for symbol, token in token_map.items():
        try:
            data = real_kite.historical_data(token, from_date, to_date, "minute")
            if data:
                stock_data[symbol] = data
            # Rate limit protection: Sleep a bit
            time.sleep(0.2) 
        except Exception as e:
            print(f"Failed to fetch data for {symbol}: {e}")
            time.sleep(1) # Sleep longer on error
            
    if not stock_data:
        print("No data found for any stock.")
        return {'status': 'no_data', 'pnl': 0, 'trades': 0}
        
    print(f"Data fetched for {len(stock_data)} stocks.")

    # 3. Synchronized Simulation Loop
    # We need to iterate Minute by Minute.
    # Convert all data to a timeline: timestamp -> {symbol: candle}
    timeline = {}
    for symbol, candles in stock_data.items():
        for candle in candles:
            ts = candle['date']
            if ts not in timeline:
                timeline[ts] = {}
            timeline[ts][symbol] = candle
            
    sorted_timestamps = sorted(timeline.keys())
    
    # Simulation State
    stock_states = {} # symbol -> {orb_high, orb_low, orb_locked, orb_candles, position, entry_price, sl, target}
    for symbol in stock_data.keys():
        stock_states[symbol] = {
            'orb_high': None, 'orb_low': None, 'orb_locked': False, 'orb_candles': [],
            'position': None, 'entry_price': 0, 'sl': 0, 'target': 0
        }
    
    trades = []
    daily_pnl = 0
    trades_taken_today = 0
    max_trades = CONFIG.max_trades_per_day
    
    orb_window_minutes = CONFIG.orb_time_frame
    
    print(f"\n--- Simulation Start (Max Trades: {max_trades}) ---")
    
    for current_time in sorted_timestamps:
        minute_data = timeline[current_time]
        
        # 1. Update ORB State for all stocks
        for symbol, candle in minute_data.items():
            state = stock_states[symbol]
            if not state['orb_locked']:
                state['orb_candles'].append(candle)
                if len(state['orb_candles']) == orb_window_minutes:
                     high = max(c['high'] for c in state['orb_candles'])
                     low = min(c['low'] for c in state['orb_candles'])
                     state['orb_high'] = high
                     state['orb_low'] = low
                     state['orb_locked'] = True
                     # print(f"[{current_time}] {symbol} ORB LOCKED: {high} - {low}")

        # 2. Check Signals & Manage Trades
        potential_signals = [] # Tuple: (strength, symbol, signal, price, sl, target)
        
        # Cutoff Check (Optional per request, usually 11:30 AM?)
        # if current_time.hour > 11 or (current_time.hour == 11 and current_time.minute >= 30):
        #    pass # Logic to skip new entries could go here
        
        for symbol, candle in minute_data.items():
            state = stock_states[symbol]
            current_price = candle['close']
            current_high = candle['high']
            current_low = candle['low']
            
            # Manage Existing Position
            if state['position']:
                exit_reason = None
                exit_price = 0
                
                if state['position'] == "BUY":
                    if current_low <= state['sl']:
                        exit_reason = "STOP LOSS HIT"
                        exit_price = state['sl']
                    elif current_high >= state['target']:
                        exit_reason = "TARGET HIT"
                        exit_price = state['target']
                elif state['position'] == "SELL":
                    if current_high >= state['sl']:
                        exit_reason = "STOP LOSS HIT"
                        exit_price = state['sl']
                    elif current_low <= state['target']:
                        exit_reason = "TARGET HIT"
                        exit_price = state['target']
                        
                # EOD Exit
                if not exit_reason and current_time.hour == 15 and current_time.minute >= 25:
                     exit_reason = "EOD EXIT"
                     exit_price = current_price

                if exit_reason:
                     pnl = (exit_price - state['entry_price']) if state['position'] == "BUY" else (state['entry_price'] - exit_price)
                     daily_pnl += pnl
                     print(f"[{current_time}] {symbol} EXIT: {exit_reason} ({state['position']}) @ {exit_price} | PnL: {pnl:.2f}")
                     trades.append({
                        'symbol': symbol, 'type': 'EXIT', 'side': state['position'], 
                        'price': exit_price, 'time': current_time, 'pnl': pnl, 'reason': exit_reason
                     })
                     state['position'] = "EXITED" # Mark as exited so no re-entry
            
            # Check New Entry (Only if no position and limit not reached)
            elif state['orb_locked'] and state['position'] is None and trades_taken_today < max_trades:
                 # Check Breakout
                 signal = None
                 sl = 0
                 target = 0
                 
                 if current_price > state['orb_high']:
                     signal = "BUY"
                     sl = state['orb_low']
                     risk = current_price - sl
                     target = current_price + (risk * 1.5)
                     
                 elif current_price < state['orb_low']:
                     signal = "SELL"
                     sl = state['orb_high']
                     risk = sl - current_price
                     target = current_price - (risk * 1.5)
                     
                 if signal:
                     # Calculate Strength
                     # abs(current_price - ORB_level) / (ORB_high - ORB_low)
                     orb_range = state['orb_high'] - state['orb_low']
                     if orb_range == 0: orb_range = 0.05 # Prevent div by zero
                     level = state['orb_high'] if signal == "BUY" else state['orb_low']
                     
                     # Use the same logic as OrbStrategy (inlined here for backtest simplicity without full object overhead)
                     # strength = OrbStrategy.calculate_signal_strength(..., current_price, signal) 
                     # Refactoring backtest to use the exact class method would require instantiating OrbStrategy for each stock.
                     # For now, we keep the logic identical:
                     strength = abs(current_price - level) / orb_range
                     
                     potential_signals.append({
                         'strength': strength,
                         'symbol': symbol,
                         'signal': signal,
                         'price': current_price,
                         'sl': sl,
                         'target': target
                     })

        # 3. Process Signals (Ranking)
        if potential_signals:
            # Sort by strength descending
            potential_signals.sort(key=lambda x: x['strength'], reverse=True)
            
            # Print Candidate Summary
            if trades_taken_today < max_trades:
                print(f"\n--- CANDIDATES at {current_time} (Top 3 by Strength) ---")
                for i, sig in enumerate(potential_signals[:3]):
                    orb_h = stock_states[sig['symbol']]['orb_high']
                    orb_l = stock_states[sig['symbol']]['orb_low']
                    rng = orb_h - orb_l if orb_h and orb_l else 0
                    print(f"  {i+1}. {sig['symbol']} [{sig['signal']}] | Score: {sig['strength']:.4f} | Range: {rng:.2f} | Price: {sig['price']}")
            
            # Take top N
            slots_available = max_trades - trades_taken_today
            entries = potential_signals[:slots_available]
            
            for entry in entries:
                symbol = entry['symbol']
                state = stock_states[symbol]
                
                # Double check if we still have slots (loop safety)
                if trades_taken_today >= max_trades: break
                
                state['position'] = entry['signal']
                state['entry_price'] = entry['price']
                state['sl'] = entry['sl']
                state['target'] = entry['target']
                
                trades_taken_today += 1
                
                print(f">>> EXECUTING TRADE: {symbol} selected. Reason: Highest Strength ({entry['strength']:.4f}) among candidates.")
                trades.append({
                    'symbol': symbol, 'type': 'ENTRY', 'side': entry['signal'],
                    'price': entry['price'], 'time': current_time,
                    'sl': entry['sl'], 'target': entry['target']
                })

    print(f"Total PnL: {daily_pnl:.2f}, Trades: {len(trades) // 2}\n")
    return {'status': 'success', 'pnl': daily_pnl, 'trades': len(trades) // 2}


def run_batch_backtest(days_lookback: int):
    """
    Run backtest for the last N days.
    """
    print(f"Starting Batch Backtest for last {days_lookback} days...")
    
    total_pnl = 0
    total_trades = 0
    winning_days = 0
    losing_days = 0
    
    today = datetime.datetime.now().date()
    
    # Iterate backwards
    days_processed = 0
    current_offset = 0
    
    while days_processed < days_lookback and current_offset < (days_lookback * 4): # Safety break increased
        # Calculate date
        target_date_obj = today - datetime.timedelta(days=current_offset)
        target_date_str = target_date_obj.strftime("%Y-%m-%d")
        
        # Skip weekends - simplistic check (0=Mon, 6=Sun)
        if target_date_obj.weekday() >= 5:
            current_offset += 1
            continue
            
        result = run_backtest(target_date_str)
        
        if result['status'] == 'success':
            total_pnl += result['pnl']
            total_trades += result['trades']
            if result['pnl'] > 0:
                winning_days += 1
            elif result['pnl'] < 0:
                losing_days += 1
            
            # Count this day as processed because we got valid data (market was active)
            days_processed += 1
                
        elif result['status'] == 'no_data':
             pass # Just skip, might be holiday
        
        current_offset += 1
        
    print("="*40)
    print(f"Batch Backtest Summary ({days_lookback} active days)")
    print("="*40)
    print(f"Total PnL      : {total_pnl:.2f}")
    print(f"Total Trades   : {total_trades}")
    print(f"Winning Days   : {winning_days}")
    print(f"Losing Days    : {losing_days}")
    print("="*40)


if __name__ == "__main__":
    import sys
    
    arg = "2024-01-01"
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    else:
        # Default usage info
        print("Usage:")
        print("  python backtest.py YYYY-MM-DD   (Single day)")
        print("  python backtest.py <Number>     (Last N days, e.g. 20)")
        arg = input("Enter date or number of days: ").strip()
        
    # Check if arg is a number (Batch mode) or date (Single mode)
    try:
        days = int(arg)
        # It's a number, run batch
        run_batch_backtest(days)
    except ValueError:
        # It's a date string
        run_backtest(arg)
