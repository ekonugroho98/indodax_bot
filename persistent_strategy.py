import requests
import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime
import ta

class PersistentPEPEStrategy:
    def __init__(self):
        self.url = "https://indodax.com/api/pepe_idr/ticker"
        self.price_history = []
        self.previous_signal = None
        self.data_file = "pepe_historical_data.json"
        
        # Load existing data when starting
        self.load_historical_data()
        
    def load_historical_data(self):
        """Load data historis dari file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    # Convert string timestamps back to datetime objects
                    for item in data:
                        item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                    self.price_history = data
                    print(f"📂 Loaded {len(self.price_history)} historical data points")
            else:
                print("📂 No historical data found, starting fresh")
        except Exception as e:
            print(f"⚠️ Error loading historical data: {e}")
            self.price_history = []
    
    def save_historical_data(self):
        """Save data historis ke file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            data_to_save = []
            for item in self.price_history:
                item_copy = item.copy()
                item_copy['timestamp'] = item['timestamp'].isoformat()
                data_to_save.append(item_copy)
            
            with open(self.data_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            print(f"💾 Saved {len(self.price_history)} data points to {self.data_file}")
        except Exception as e:
            print(f"⚠️ Error saving data: {e}")
    
    def get_price(self):
        """Mengambil harga PEPE saat ini"""
        try:
            response = requests.get(self.url)
            data = response.json()
            ticker = data['ticker']
            return {
                'timestamp': datetime.now(),
                'price': float(ticker['last']),
                'volume': float(ticker['vol_pepe']),
                'high': float(ticker['high']),
                'low': float(ticker['low'])
            }
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Menghitung RSI"""
        if len(prices) < period:
            return None
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_sma(self, prices, period):
        """Menghitung Simple Moving Average"""
        if len(prices) < period:
            return None
        return np.mean(prices[-period:])
    
    def generate_signal(self, current_data):
        """Generate sinyal trading sederhana"""
        if len(self.price_history) < 20:
            return "HOLD", "Data tidak cukup"
        
        prices = [p['price'] for p in self.price_history]
        
        # RSI
        rsi = self.calculate_rsi(prices)
        
        # SMA
        sma_5 = self.calculate_sma(prices, 5)
        sma_20 = self.calculate_sma(prices, 20)
        
        # Volume analysis
        volumes = [p['volume'] for p in self.price_history]
        avg_volume = np.mean(volumes[-20:])
        current_volume = current_data['volume']
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        signal = "HOLD"
        reason = []
        
        # RSI Strategy
        if rsi:
            if rsi < 30:
                signal = "BUY"
                reason.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > 70:
                signal = "SELL"
                reason.append(f"RSI overbought ({rsi:.1f})")
        
        # Moving Average Strategy
        if sma_5 and sma_20:
            if sma_5 > sma_20 and prices[-2] <= sma_20 and prices[-1] > sma_20:
                signal = "BUY"
                reason.append("MA Crossover (Bullish)")
            elif sma_5 < sma_20 and prices[-2] >= sma_20 and prices[-1] < sma_20:
                signal = "SELL"
                reason.append("MA Crossover (Bearish)")
        
        # Volume confirmation
        if volume_ratio < 0.5:
            if signal != "HOLD":
                signal = "HOLD"
                reason.append("Volume rendah")
        
        return signal, ", ".join(reason) if reason else "Tidak ada sinyal jelas"
    
    def show_statistics(self):
        """Menampilkan statistik data historis"""
        if len(self.price_history) == 0:
            print("📊 Tidak ada data historis")
            return
        
        prices = [p['price'] for p in self.price_history]
        volumes = [p['volume'] for p in self.price_history]
        
        print(f"\n📊 STATISTIK DATA HISTORIS:")
        print(f"   Total data points: {len(self.price_history)}")
        print(f"   Periode: {self.price_history[0]['timestamp'].strftime('%Y-%m-%d %H:%M')} - {self.price_history[-1]['timestamp'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   Harga tertinggi: Rp {max(prices):.6f}")
        print(f"   Harga terendah: Rp {min(prices):.6f}")
        print(f"   Harga rata-rata: Rp {np.mean(prices):.6f}")
        print(f"   Volume rata-rata: {np.mean(volumes):.2f}")
        
        # Calculate price change
        if len(prices) > 1:
            price_change = ((prices[-1] - prices[0]) / prices[0]) * 100
            print(f"   Perubahan harga: {price_change:+.2f}%")
    
    def run(self):
        """Menjalankan strategi"""
        print("🚀 PEPE Scalping Strategy - Persistent Version")
        print("=" * 50)
        print("Monitoring harga PEPE/IDR...")
        print("=" * 50)
        
        # Show initial statistics
        self.show_statistics()
        
        try:
            while True:
                current_data = self.get_price()
                if not current_data:
                    time.sleep(5)
                    continue
                
                # Update price history
                self.price_history.append(current_data)
                if len(self.price_history) > 1000:  # Keep last 1000 data points
                    self.price_history.pop(0)
                
                # Save data every 10 updates
                if len(self.price_history) % 10 == 0:
                    self.save_historical_data()
                
                # Generate signal
                signal, reason = self.generate_signal(current_data)
                
                # Display results
                timestamp = current_data['timestamp'].strftime('%H:%M:%S')
                print(f"\n⏰ {timestamp} | 💰 Rp {current_data['price']:.6f}")
                
                if signal != self.previous_signal:
                    if signal == "BUY":
                        print(f"🟢 SIGNAL: BELI PEPE!")
                        print(f"   Alasan: {reason}")
                    elif signal == "SELL":
                        print(f"🔴 SIGNAL: JUAL PEPE!")
                        print(f"   Alasan: {reason}")
                    else:
                        print(f"⚪ SIGNAL: HOLD")
                        print(f"   Alasan: {reason}")
                    
                    self.previous_signal = signal
                else:
                    print(f"   Signal: {signal} | {reason}")
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bot dihentikan oleh user")
            print("💾 Menyimpan data historis...")
            self.save_historical_data()
            print("✅ Data berhasil disimpan!")
            print("📊 Total data points:", len(self.price_history))
            print("👋 Goodbye!")

if __name__ == "__main__":
    strategy = PersistentPEPEStrategy()
    strategy.run() 