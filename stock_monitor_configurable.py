import yfinance as yf
import schedule
import time
from datetime import datetime
import json
import os

class StockMonitor:
    def __init__(self):
        self.config_file = "stock_config.json"
        self.stocks_to_monitor = {}
        self.previous_prices = {}
        self.monitoring_interval = 1
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.stocks_to_monitor = config.get('stocks', {})
                    self.monitoring_interval = config.get('interval_minutes', 1)
            except:
                self.setup_config()
        else:
            self.setup_config()
    
    def save_config(self):
        """Save configuration to file"""
        config = {
            'stocks': self.stocks_to_monitor,
            'interval_minutes': self.monitoring_interval
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def setup_config(self):
        """Interactive setup for stock monitoring configuration"""
        print("=== Stock Monitoring Setup ===")
        print("Let's configure your stock monitoring preferences")
        
        # Get monitoring interval
        while True:
            try:
                interval = int(input("\nEnter monitoring interval in minutes (1-60): "))
                if 1 <= interval <= 60:
                    self.monitoring_interval = interval
                    break
                else:
                    print("Please enter a value between 1 and 60")
            except ValueError:
                print("Please enter a valid number")
        
        # Get stocks to monitor
        print("\nEnter the stock symbols you want to monitor (e.g., AAPL, MSFT, BANKNIFTY.NS, RELIANCE.NS)")
        print("Type 'done' when finished")
        
        while True:
            symbol = input("\nEnter stock symbol (or 'done' to finish): ").strip().upper()
            if symbol == 'DONE':
                if not self.stocks_to_monitor:
                    print("You need to add at least one stock symbol!")
                    continue
                break
            
            if symbol:
                # Validate symbol by trying to fetch price
                try:
                    test_price = self.get_stock_price(symbol)
                    if test_price is not None:
                        print(f"✓ Valid symbol: {symbol} - Current price: ${test_price:.2f}")
                        
                        # Get buy threshold
                        while True:
                            try:
                                buy_thresh = float(input(f"Enter BUY alert threshold for {symbol} (current: ${test_price:.2f}): "))
                                break
                            except ValueError:
                                print("Please enter a valid number")
                        
                        # Get sell threshold
                        while True:
                            try:
                                sell_thresh = float(input(f"Enter SELL alert threshold for {symbol} (current: ${test_price:.2f}): "))
                                if sell_thresh > buy_thresh:
                                    break
                                else:
                                    print("Sell threshold should be higher than buy threshold")
                            except ValueError:
                                print("Please enter a valid number")
                        
                        self.stocks_to_monitor[symbol] = {
                            'buy_threshold': buy_thresh,
                            'sell_threshold': sell_thresh
                        }
                        print(f"✓ {symbol} added to monitoring list")
                    else:
                        print(f"✗ Could not fetch price for {symbol}. Please check the symbol format.")
                        print("For Indian stocks, use .NS suffix (e.g., RELIANCE.NS, BANKNIFTY.NS)")
                except Exception as e:
                    print(f"✗ Error validating {symbol}: {e}")
        
        self.save_config()
        print("\nConfiguration saved successfully!")
    
    def get_stock_price(self, symbol):
        """Fetch current stock price using yfinance"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period='1d', interval='1m')
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def check_alerts(self, symbol, current_price):
        """Check if price crosses any alert thresholds"""
        alerts = []
        thresholds = self.stocks_to_monitor[symbol]
        
        # Check if price crossed buy threshold
        if current_price <= thresholds['buy_threshold']:
            alerts.append(f"BUY ALERT: {symbol} at ${current_price:.2f} (below buy threshold ${thresholds['buy_threshold']})")
        
        # Check if price crossed sell threshold
        if current_price >= thresholds['sell_threshold']:
            alerts.append(f"SELL ALERT: {symbol} at ${current_price:.2f} (above sell threshold ${thresholds['sell_threshold']})")
        
        # Check for significant price movement
        if symbol in self.previous_prices:
            prev_price = self.previous_prices[symbol]
            if prev_price != 0:  # Avoid division by zero
                change_percent = ((current_price - prev_price) / prev_price) * 100
                if abs(change_percent) >= 2.0:  # Alert on 2%+ movement
                    direction = "UP" if change_percent > 0 else "DOWN"
                    alerts.append(f"MOVEMENT ALERT: {symbol} moved {direction} {abs(change_percent):.2f}% to ${current_price:.2f}")
        
        self.previous_prices[symbol] = current_price
        return alerts
    
    def monitor_stocks(self):
        """Main monitoring function that runs periodically"""
        print(f"\n=== Stock Market Monitoring - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        
        all_alerts = []
        for symbol in self.stocks_to_monitor:
            price = self.get_stock_price(symbol)
            if price is not None:
                print(f"{symbol}: ${price:.2f}")
                alerts = self.check_alerts(symbol, price)
                all_alerts.extend(alerts)
            else:
                print(f"{symbol}: Unable to fetch price")
        
        # Display alerts if any
        if all_alerts:
            print("\n🚨 ALERTS:")
            for alert in all_alerts:
                print(f"   {alert}")
        else:
            print("\nNo alerts triggered")
    
    def start_monitoring(self):
        """Start the monitoring scheduler"""
        print("Starting Real-Time Stock Market Monitor...")
        print(f"Monitoring: {', '.join(self.stocks_to_monitor.keys())}")
        print(f"Check interval: {self.monitoring_interval} minute(s)")
        print("Press Ctrl+C to stop monitoring\n")
        
        # Run immediately once
        self.monitor_stocks()
        
        # Schedule periodic monitoring
        schedule.every(self.monitoring_interval).minutes.do(self.monitor_stocks)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")

def main():
    # Create and start the stock monitor
    monitor = StockMonitor()
    
    # Show current configuration
    print("\nCurrent Configuration:")
    print(f"Monitoring Interval: {monitor.monitoring_interval} minutes")
    print("Stocks being monitored:")
    for symbol, thresholds in monitor.stocks_to_monitor.items():
        print(f"  {symbol}: Buy @ ${thresholds['buy_threshold']}, Sell @ ${thresholds['sell_threshold']}")
    
    # Ask if user wants to reconfigure
    reconfigure = input("\nDo you want to reconfigure? (y/n): ").lower().strip()
    if reconfigure == 'y':
        monitor.setup_config()
    
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
