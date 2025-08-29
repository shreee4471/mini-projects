import yfinance as yf
import schedule
import time
from datetime import datetime
import json
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import plyer.platforms.win.notification
from plyer import notification

class StockMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Stock Monitor")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        self.config_file = "stock_config.json"
        self.stocks_to_monitor = {}
        self.previous_prices = {}
        self.monitoring_interval = 1
        self.monitoring_active = False
        self.monitor_thread = None
        
        self.load_config()
        self.create_widgets()
        self.update_display()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.stocks_to_monitor = config.get('stocks', {})
                    self.monitoring_interval = config.get('interval_minutes', 1)
            except:
                self.stocks_to_monitor = {}
    
    def save_config(self):
        """Save configuration to file"""
        config = {
            'stocks': self.stocks_to_monitor,
            'interval_minutes': self.monitoring_interval
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Interval setting
        ttk.Label(config_frame, text="Monitoring Interval (minutes):").grid(row=0, column=0, sticky=tk.W)
        self.interval_var = tk.StringVar(value=str(self.monitoring_interval))
        interval_spin = ttk.Spinbox(config_frame, from_=1, to=60, textvariable=self.interval_var, width=5)
        interval_spin.grid(row=0, column=1, padx=5)
        
        # Stock management section
        stock_frame = ttk.LabelFrame(main_frame, text="Stock Management", padding="10")
        stock_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(stock_frame, text="Stock Symbol:").grid(row=0, column=0, sticky=tk.W)
        self.symbol_var = tk.StringVar()
        symbol_entry = ttk.Entry(stock_frame, textvariable=self.symbol_var, width=15)
        symbol_entry.grid(row=0, column=1, padx=5)
        
        # Label to show current price and arrow
        self.price_label = ttk.Label(stock_frame, text="", width=20)
        self.price_label.grid(row=0, column=7, padx=10)
        
        # Bind event to update price when symbol changes
        symbol_entry.bind("<FocusOut>", self.update_price_display)
        symbol_entry.bind("<Return>", self.update_price_display)
        
        ttk.Label(stock_frame, text="Buy Threshold:").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.buy_var = tk.StringVar()
        ttk.Entry(stock_frame, textvariable=self.buy_var, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(stock_frame, text="Sell Threshold:").grid(row=0, column=4, sticky=tk.W, padx=(20,0))
        self.sell_var = tk.StringVar()
        ttk.Entry(stock_frame, textvariable=self.sell_var, width=10).grid(row=0, column=5, padx=5)
        
        ttk.Button(stock_frame, text="Add Stock", command=self.add_stock).grid(row=0, column=6, padx=10)
        
        # Stocks list
        self.stock_tree = ttk.Treeview(main_frame, columns=('symbol', 'buy', 'sell'), show='headings', height=8)
        self.stock_tree.heading('symbol', text='Symbol')
        self.stock_tree.heading('buy', text='Buy Threshold')
        self.stock_tree.heading('sell', text='Sell Threshold')
        self.stock_tree.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Remove button
        ttk.Button(main_frame, text="Remove Selected", command=self.remove_stock).grid(row=3, column=0, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Save Configuration", command=self.save_config).pack(side=tk.LEFT, padx=5)
        
        # Output console
        output_frame = ttk.LabelFrame(main_frame, text="Monitoring Output", padding="10")
        output_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
    
    def add_stock(self):
        """Add a new stock to monitor"""
        symbol = self.symbol_var.get().strip().upper()
        buy_thresh = self.buy_var.get()
        sell_thresh = self.sell_var.get()
        
        if not symbol or not buy_thresh or not sell_thresh:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        try:
            buy_thresh = float(buy_thresh)
            sell_thresh = float(sell_thresh)
            
            if sell_thresh <= buy_thresh:
                messagebox.showerror("Error", "Sell threshold must be higher than buy threshold")
                return
            
            # Validate symbol
            price = self.get_stock_price(symbol)
            if price is None:
                messagebox.showerror("Error", f"Could not fetch price for {symbol}. Check symbol format.")
                return
            
            self.stocks_to_monitor[symbol] = {
                'buy_threshold': buy_thresh,
                'sell_threshold': sell_thresh
            }
            
            self.symbol_var.set('')
            self.buy_var.set('')
            self.sell_var.set('')
            self.update_display()
            self.log_message(f"✓ Added {symbol} to monitoring list")
            self.update_price_display()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for thresholds")
    
    def remove_stock(self):
        """Remove selected stock"""
        selection = self.stock_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a stock to remove")
            return
        
        for item in selection:
            symbol = self.stock_tree.item(item)['values'][0]
            if symbol in self.stocks_to_monitor:
                del self.stocks_to_monitor[symbol]
                self.log_message(f"✓ Removed {symbol} from monitoring list")
        
        self.update_display()
    
    def update_display(self):
        """Update the stocks list display"""
        self.stock_tree.delete(*self.stock_tree.get_children())
        for symbol, thresholds in self.stocks_to_monitor.items():
            self.stock_tree.insert('', 'end', values=(
                symbol, 
                f"${thresholds['buy_threshold']:.2f}", 
                f"${thresholds['sell_threshold']:.2f}"
            ))
    
    def log_message(self, message):
        """Add message to output console"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def show_notification(self, title, message):
        """Show desktop notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=10
            )
        except:
            # Fallback to log message if notification fails
            self.log_message(f"NOTIFICATION: {title} - {message}")
    
    def get_stock_price(self, symbol):
        """Fetch current stock price"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period='1d', interval='1m')
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            self.log_message(f"Error fetching {symbol}: {e}")
            return None

    def update_price_display(self, event=None):
        """Update the price label with current price and arrow"""
        symbol = self.symbol_var.get().strip().upper()
        if not symbol:
            self.price_label.config(text="")
            return
        
        price = self.get_stock_price(symbol)
        if price is None:
            self.price_label.config(text="Price: N/A")
            return
        
        prev_price = self.previous_prices.get(symbol)
        arrow = ""
        if prev_price is not None:
            if price > prev_price:
                arrow = "↑"
            elif price < prev_price:
                arrow = "↓"
            else:
                arrow = "→"
        else:
            arrow = ""
        
        self.price_label.config(text=f"Price: ${price:.2f} {arrow}")
        self.previous_prices[symbol] = price
    
    def check_alerts(self, symbol, current_price):
        """Check for alerts and trigger notifications"""
        alerts = []
        thresholds = self.stocks_to_monitor[symbol]
        
        # Buy alert
        if current_price <= thresholds['buy_threshold']:
            alert_msg = f"BUY ALERT: {symbol} at ${current_price:.2f} (below buy threshold ${thresholds['buy_threshold']})"
            alerts.append(alert_msg)
            self.show_notification("💰 BUY Alert", alert_msg)
        
        # Sell alert
        if current_price >= thresholds['sell_threshold']:
            alert_msg = f"SELL ALERT: {symbol} at ${current_price:.2f} (above sell threshold ${thresholds['sell_threshold']})"
            alerts.append(alert_msg)
            self.show_notification("📈 SELL Alert", alert_msg)
        
        # Movement alert
        if symbol in self.previous_prices:
            prev_price = self.previous_prices[symbol]
            if prev_price != 0:
                change_percent = ((current_price - prev_price) / prev_price) * 100
                if abs(change_percent) >= 2.0:
                    direction = "UP" if change_percent > 0 else "DOWN"
                    alert_msg = f"{symbol} moved {direction} {abs(change_percent):.2f}% to ${current_price:.2f}"
                    alerts.append(f"MOVEMENT: {alert_msg}")
                    self.show_notification("📊 Price Movement", alert_msg)
        
        self.previous_prices[symbol] = current_price
        return alerts
    
    def monitor_stocks(self):
        """Monitor stocks and check for alerts"""
        if not self.stocks_to_monitor:
            self.log_message("No stocks configured for monitoring")
            return
        
        self.log_message(f"=== Monitoring stocks (Interval: {self.monitoring_interval}min) ===")
        
        all_alerts = []
        for symbol in self.stocks_to_monitor:
            price = self.get_stock_price(symbol)
            if price is not None:
                self.log_message(f"{symbol}: ${price:.2f}")
                alerts = self.check_alerts(symbol, price)
                all_alerts.extend(alerts)
            else:
                self.log_message(f"{symbol}: Unable to fetch price")
        
        if all_alerts:
            for alert in all_alerts:
                self.log_message(f"🚨 {alert}")
        else:
            self.log_message("No alerts triggered")
    
    def start_monitoring(self):
        """Start the monitoring process"""
        if not self.stocks_to_monitor:
            messagebox.showerror("Error", "Please add at least one stock to monitor")
            return
        
        try:
            self.monitoring_interval = int(self.interval_var.get())
            if not 1 <= self.monitoring_interval <= 60:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid interval (1-60 minutes)")
            return
        
        self.monitoring_active = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.save_config()
        self.log_message("Monitoring started!")
        
        # Start monitoring in separate thread
        def monitor_loop():
            self.monitor_stocks()  # Run immediately
            schedule.every(self.monitoring_interval).minutes.do(self.monitor_stocks)
            
            while self.monitoring_active:
                schedule.run_pending()
                time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.monitoring_active = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("Monitoring stopped")

def main():
    root = tk.Tk()
    app = StockMonitorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
