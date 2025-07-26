import requests
import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime
import ta
from config import *

class SmartTradingStrategy:
    def __init__(self, trading_pairs=None):
        # Default ke pairs yang enabled jika tidak ada konfigurasi
        if trading_pairs is None:
            trading_pairs = [p for p in TRADING_PAIRS if p['enabled']]
        
        self.trading_pairs = trading_pairs
        self.base_url = "https://indodax.com/api"
        
        # Data storage untuk setiap pair
        self.price_history = {}  # {pair: [data]}
        self.previous_signals = {}  # {pair: signal}
        self.data_files = {}  # {pair: filename}
        self.last_saved_data = {}  # {pair: data}
        
        # Enhanced data management
        self.data_cache = {}  # {pair: cached_data}
        self.archived_data = {}  # {pair: archived_data}
        self.data_tiers = DATA_MANAGEMENT_TIERS
        self.current_tier = 'scalping'  # Default tier
        
        # Trading state untuk setiap pair
        self.current_positions = {}  # {pair: "LONG"/"SHORT"/None}
        self.entry_prices = {}  # {pair: price}
        self.entry_times = {}  # {pair: time}
        self.stop_losses = {}  # {pair: price}
        self.take_profits = {}  # {pair: price}
        
        # Signal management
        self.last_signal_times = {}  # {pair: time}
        self.signal_counts = {}  # {pair: {"BUY": 0, "SELL": 0, "HOLD": 0}}
        self.consecutive_signals = {}  # {pair: count}
        
        # Risk management parameters dari config
        self.stop_loss_percent = STOP_LOSS_PERCENT
        self.take_profit_percent = TAKE_PROFIT_PERCENT
        self.max_hold_time = MAX_HOLD_TIME
        self.signal_cooldown = SIGNAL_COOLDOWN
        
        # Initialize untuk setiap pair
        for pair_config in self.trading_pairs:
            pair = pair_config['pair']
            self.price_history[pair] = []
            self.previous_signals[pair] = None
            self.data_files[pair] = f"{pair}_historical_data.json"
            self.last_saved_data[pair] = None
            self.data_cache[pair] = None
            self.archived_data[pair] = []
            self.current_positions[pair] = None
            self.entry_prices[pair] = None
            self.entry_times[pair] = None
            self.stop_losses[pair] = None
            self.take_profits[pair] = None
            self.last_signal_times[pair] = None
            self.signal_counts[pair] = {"BUY": 0, "SELL": 0, "HOLD": 0}
            self.consecutive_signals[pair] = 0
        
        # Load existing data when starting
        self.load_all_historical_data()
        
    def get_pair_config(self, pair):
        """Dapatkan konfigurasi untuk pair tertentu"""
        for config in self.trading_pairs:
            if config['pair'] == pair:
                return config
        return None
        
    def load_all_historical_data(self):
        """Load data historis untuk semua pairs"""
        for pair_config in self.trading_pairs:
            pair = pair_config['pair']
            self.load_historical_data_enhanced(pair)
        
    def load_historical_data(self, pair):
        """Load data historis dari file untuk pair tertentu"""
        try:
            data_file = self.data_files[pair]
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    # Convert string timestamps back to datetime objects
                    for item in data:
                        item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                    self.price_history[pair] = data
                    print(f"📂 Loaded {len(self.price_history[pair])} historical data points for {pair}")
                    
                    # Set last saved data to the most recent entry
                    if self.price_history[pair]:
                        self.last_saved_data[pair] = self.price_history[pair][-1].copy()
            else:
                print(f"📂 No historical data found for {pair}, starting fresh")
        except Exception as e:
            print(f"⚠️ Error loading historical data for {pair}: {e}")
            self.price_history[pair] = []
    
    def save_historical_data(self, pair):
        """Save data historis ke file untuk pair tertentu"""
        try:
            data_file = self.data_files[pair]
            # Convert datetime objects to strings for JSON serialization
            data_to_save = []
            for item in self.price_history[pair]:
                item_copy = item.copy()
                item_copy['timestamp'] = item['timestamp'].isoformat()
                data_to_save.append(item_copy)
            
            with open(data_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            print(f"💾 Saved {len(self.price_history[pair])} data points to {data_file}")
        except Exception as e:
            print(f"⚠️ Error saving data for {pair}: {e}")
    
    def has_significant_change(self, current_data, pair):
        """Check if there's a significant change in data untuk pair tertentu"""
        if self.last_saved_data[pair] is None:
            return True
        
        # Define thresholds for significant changes
        price_threshold = 0.0001  # 0.01% change in price
        volume_threshold = 0.01   # 1% change in volume
        
        # Check price change
        price_change = abs(current_data['price'] - self.last_saved_data[pair]['price'])
        price_change_percent = price_change / self.last_saved_data[pair]['price']
        
        # Check volume change
        volume_change = abs(current_data['volume'] - self.last_saved_data[pair]['volume'])
        volume_change_percent = volume_change / self.last_saved_data[pair]['volume'] if self.last_saved_data[pair]['volume'] > 0 else 0
        
        # Check high/low changes
        high_change = abs(current_data['high'] - self.last_saved_data[pair]['high'])
        low_change = abs(current_data['low'] - self.last_saved_data[pair]['low'])
        
        # Return True if any significant change detected
        return (price_change_percent > price_threshold or 
                volume_change_percent > volume_threshold or
                high_change > price_threshold or
                low_change > price_threshold)
    
    def get_price(self, pair):
        """Mengambil harga untuk pair tertentu"""
        try:
            url = f"{self.base_url}/{pair}/ticker"
            response = requests.get(url)
            data = response.json()
            ticker = data['ticker']
            
            # Get volume field name based on pair
            volume_field = f"vol_{pair.split('_')[0]}"
            if volume_field not in ticker:
                volume_field = 'vol_idr'  # fallback
                
            return {
                'timestamp': datetime.now(),
                'price': float(ticker['last']),
                'volume': float(ticker[volume_field]),
                'high': float(ticker['high']),
                'low': float(ticker['low'])
            }
        except Exception as e:
            print(f"Error getting price for {pair}: {e}")
            return None
    
    def get_orderbook_pressure(self, pair):
        """Mengambil order book pressure untuk pair tertentu"""
        try:
            url = f"{self.base_url}/{pair}/depth"
            response = requests.get(url)
            data = response.json()
            
            # Hitung total volume pada 3 order teratas di sisi BUY
            top_buy_volume = sum(float(order[1]) for order in data['buy'][:3])
            
            # Hitung total volume pada 3 order teratas di sisi SELL
            top_sell_volume = sum(float(order[1]) for order in data['sell'][:3])
            
            # Hitung ratio buy/sell pressure
            if top_sell_volume > 0:
                ratio = top_buy_volume / top_sell_volume
            else:
                ratio = 1.0
            
            return ratio, top_buy_volume, top_sell_volume
            
        except Exception as e:
            print(f"Error getting orderbook for {pair}: {e}")
            return 1.0, 0, 0
    
    def get_trade_dominance(self, pair):
        """Mengambil trade dominance untuk pair tertentu"""
        try:
            url = f"{self.base_url}/{pair}/trades"
            response = requests.get(url)
            trades = response.json()
            
            # Ambil 10 transaksi terakhir
            last_trades = trades[:10]
            
            # Hitung berapa yang "buy" vs "sell"
            buy_count = sum(1 for trade in last_trades if trade['type'] == 'buy')
            sell_count = len(last_trades) - buy_count
            
            # Hitung ratio dominasi
            total_trades = len(last_trades)
            if total_trades > 0:
                buy_ratio = buy_count / total_trades
                sell_ratio = sell_count / total_trades
            else:
                buy_ratio = 0.5
                sell_ratio = 0.5
            
            return buy_ratio, sell_ratio, buy_count, sell_count
            
        except Exception as e:
            print(f"Error getting trades for {pair}: {e}")
            return 0.5, 0.5, 5, 5
    
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
    
    def calculate_multi_timeframe_rsi(self, prices):
        """RSI dengan multiple timeframe untuk konfirmasi"""
        rsi_3 = self.calculate_rsi(prices, 3)    # Ultra short term (scalping)
        rsi_5 = self.calculate_rsi(prices, 5)    # Short term
        rsi_14 = self.calculate_rsi(prices, 14)  # Medium term
        
        return rsi_3, rsi_5, rsi_14
    
    def calculate_momentum_indicators(self, prices):
        """Hitung momentum indicators untuk scalping"""
        if len(prices) < 10:
            return None, None, None
        
        # Rate of Change (ROC) - 3 period untuk scalping
        roc_3 = ((prices[-1] - prices[-4]) / prices[-4]) * 100 if len(prices) >= 4 else 0
        
        # Price Rate of Change - 5 period
        roc_5 = ((prices[-1] - prices[-6]) / prices[-6]) * 100 if len(prices) >= 6 else 0
        
        # Momentum - 10 period
        momentum_10 = prices[-1] - prices[-11] if len(prices) >= 11 else 0
        
        return roc_3, roc_5, momentum_10
    
    def calculate_volatility_indicators(self, prices):
        """Hitung volatility indicators untuk scalping"""
        if len(prices) < 20:
            return None, None, None
        
        # True Range (ATR) - 14 period
        high_low = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
        atr_14 = np.mean(high_low[-14:]) if len(high_low) >= 14 else 0
        
        # Standard Deviation - 10 period
        recent_prices = prices[-10:]
        std_dev = np.std(recent_prices)
        
        # Coefficient of Variation (CV)
        cv = (std_dev / np.mean(recent_prices)) * 100 if np.mean(recent_prices) > 0 else 0
        
        return atr_14, std_dev, cv
    
    def calculate_sma(self, prices, period):
        """Menghitung Simple Moving Average"""
        if len(prices) < period:
            return None
        return np.mean(prices[-period:])
    
    def check_trend_stability(self, prices, sma_5, sma_20):
        """Cek stabilitas trend untuk konfirmasi"""
        if len(prices) < 15:
            return False, False
        
        # Cek apakah trend konsisten dalam 15 data terakhir
        recent_prices = prices[-15:]
        price_trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
        
        # Trend bullish jika slope positif dan MA konsisten
        is_bullish = price_trend > 0 and sma_5 > sma_20
        
        # Trend bearish jika slope negatif dan MA konsisten  
        is_bearish = price_trend < 0 and sma_5 < sma_20
        
        return is_bullish, is_bearish
    
    def check_volatility(self, prices):
        """Cek volatilitas harga untuk filter signal"""
        if len(prices) < 10:
            return 0
        
        # Hitung standard deviation dari 10 data terakhir
        recent_prices = prices[-10:]
        volatility = np.std(recent_prices) / np.mean(recent_prices)
        return volatility
    
    def check_exit_conditions(self, current_data, pair):
        """Cek kondisi untuk exit dari posisi untuk pair tertentu"""
        if self.current_positions[pair] is None:
            return None, "Tidak ada posisi aktif"
        
        current_price = current_data['price']
        current_time = current_data['timestamp']
        
        # Hitung profit/loss
        if self.current_positions[pair] == "LONG":
            profit_loss = ((current_price - self.entry_prices[pair]) / self.entry_prices[pair]) * 100
        else:  # SHORT
            profit_loss = ((self.entry_prices[pair] - current_price) / self.entry_prices[pair]) * 100
        
        exit_signal = None
        exit_reason = []
        
        # 1. Stop Loss
        if profit_loss <= -self.stop_loss_percent * 100:
            exit_signal = "SELL" if self.current_positions[pair] == "LONG" else "BUY"
            exit_reason.append(f"Stop Loss ({profit_loss:.2f}%)")
        
        # 2. Take Profit
        elif profit_loss >= self.take_profit_percent * 100:
            exit_signal = "SELL" if self.current_positions[pair] == "LONG" else "BUY"
            exit_reason.append(f"Take Profit ({profit_loss:.2f}%)")
        
        # 3. Time-based exit
        elif self.entry_times[pair]:
            hold_time = (current_time - self.entry_times[pair]).total_seconds()
            if hold_time >= self.max_hold_time:
                exit_signal = "SELL" if self.current_positions[pair] == "LONG" else "BUY"
                exit_reason.append(f"Time Exit ({hold_time/60:.1f} menit)")
        
        # 4. Technical exit signals
        else:
            # RSI overbought/oversold untuk exit
            prices = [p['price'] for p in self.price_history[pair]]
            rsi_5, rsi_14 = self.calculate_multi_timeframe_rsi(prices)
            
            if self.current_positions[pair] == "LONG" and rsi_5 and rsi_14:
                if rsi_5 > 75 and rsi_14 > 70:
                    exit_signal = "SELL"
                    exit_reason.append(f"RSI Overbought (5m:{rsi_5:.1f}, 14m:{rsi_14:.1f})")
            
            elif self.current_positions[pair] == "SHORT" and rsi_5 and rsi_14:
                if rsi_5 < 25 and rsi_14 < 30:
                    exit_signal = "BUY"
                    exit_reason.append(f"RSI Oversold (5m:{rsi_5:.1f}, 14m:{rsi_14:.1f})")
        
        return exit_signal, ", ".join(exit_reason) if exit_reason else None
    
    def check_entry_timing(self, current_data, signal, pair):
        """Cek timing entry yang lebih baik untuk pair tertentu"""
        if len(self.price_history[pair]) < 10:
            return True, "Data tidak cukup"
        
        prices = [p['price'] for p in self.price_history[pair][-10:]]
        current_price = current_data['price']
        
        # 1. Cek apakah harga sedang dalam uptrend untuk BUY
        if signal == "BUY":
            # Pastikan 3 harga terakhir naik
            if len(prices) >= 3:
                if not (prices[-3] < prices[-2] < prices[-1]):
                    return False, "Harga tidak dalam uptrend"
            
            # Cek apakah harga tidak terlalu tinggi dari MA
            sma_20 = self.calculate_sma(prices, 20) if len(prices) >= 20 else None
            if sma_20:
                price_vs_ma = ((current_price - sma_20) / sma_20) * 100
                if price_vs_ma > 1.0:  # Harga terlalu tinggi dari MA
                    return False, f"Harga terlalu tinggi dari MA ({price_vs_ma:.1f}%)"
        
        # 2. Cek apakah harga sedang dalam downtrend untuk SELL
        elif signal == "SELL":
            # Pastikan 3 harga terakhir turun
            if len(prices) >= 3:
                if not (prices[-3] > prices[-2] > prices[-1]):
                    return False, "Harga tidak dalam downtrend"
            
            # Cek apakah harga tidak terlalu rendah dari MA
            sma_20 = self.calculate_sma(prices, 20) if len(prices) >= 20 else None
            if sma_20:
                price_vs_ma = ((current_price - sma_20) / sma_20) * 100
                if price_vs_ma < -1.0:  # Harga terlalu rendah dari MA
                    return False, f"Harga terlalu rendah dari MA ({price_vs_ma:.1f}%)"
        
        return True, "Timing OK"

    def calculate_better_entry_price(self, current_data, signal, pair):
        """Hitung entry price yang lebih baik untuk pair tertentu"""
        current_price = current_data['price']
        
        if len(self.price_history[pair]) < 5:
            return current_price
        
        prices = [p['price'] for p in self.price_history[pair][-5:]]
        
        if signal == "BUY":
            # Gunakan harga terendah dari 5 data terakhir + buffer kecil
            min_price = min(prices)
            entry_price = min_price * 1.001  # 0.1% buffer
            return min(entry_price, current_price)
        
        elif signal == "SELL":
            # Gunakan harga tertinggi dari 5 data terakhir - buffer kecil
            max_price = max(prices)
            entry_price = max_price * 0.999  # 0.1% buffer
            return max(entry_price, current_price)
        
        return current_price

    def generate_signal(self, current_data, pair):
        """Generate sinyal trading dengan konfirmasi ganda dan cooldown untuk pair tertentu"""
        if len(self.price_history[pair]) < MIN_DATA_POINTS:  # Minimal data points dari config
            return "HOLD", f"Data tidak cukup (minimal {MIN_DATA_POINTS} points)"
        
        # Cek exit conditions terlebih dahulu
        exit_signal, exit_reason = self.check_exit_conditions(current_data, pair)
        if exit_signal:
            return exit_signal, f"EXIT: {exit_reason}"
        
        prices = [p['price'] for p in self.price_history[pair]]
        
        # Multi-timeframe RSI dengan ultra-short term
        rsi_3, rsi_5, rsi_14 = self.calculate_multi_timeframe_rsi(prices)
        
        # Momentum indicators untuk scalping
        roc_3, roc_5, momentum_10 = self.calculate_momentum_indicators(prices)
        
        # Volatility indicators
        atr_14, std_dev, cv = self.calculate_volatility_indicators(prices)
        
        # SMA dengan periode berbeda
        sma_5 = self.calculate_sma(prices, 5)
        sma_10 = self.calculate_sma(prices, 10)
        sma_20 = self.calculate_sma(prices, 20)
        
        # Volume analysis dengan threshold lebih tinggi
        volumes = [p['volume'] for p in self.price_history[pair]]
        avg_volume = np.mean(volumes[-20:])
        current_volume = current_data['volume']
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Volatility check
        volatility = self.check_volatility(prices)
        
        # Order book pressure analysis
        orderbook_ratio, buy_volume, sell_volume = self.get_orderbook_pressure(pair)
        
        # Trade dominance analysis
        buy_ratio, sell_ratio, buy_count, sell_count = self.get_trade_dominance(pair)
        
        signal = "HOLD"
        reason = []
        signal_strength = 0
        
        # 1. Ultra-Short Term RSI Strategy (scalping specific)
        if rsi_3 and rsi_5 and rsi_14:
            # Scalping BUY: RSI 3-period oversold dengan konfirmasi
            if rsi_3 < SCALPING_RSI_3_OVERSOLD and rsi_5 < 30 and rsi_14 < 35:
                signal_strength += 2  # Higher weight for scalping
                reason.append(f"RSI Scalping BUY (3m:{rsi_3:.1f}, 5m:{rsi_5:.1f}, 14m:{rsi_14:.1f})")
            # Scalping SELL: RSI 3-period overbought dengan konfirmasi
            elif rsi_3 > SCALPING_RSI_3_OVERBOUGHT and rsi_5 > 70 and rsi_14 > 65:
                signal_strength += 2  # Higher weight for scalping
                reason.append(f"RSI Scalping SELL (3m:{rsi_3:.1f}, 5m:{rsi_5:.1f}, 14m:{rsi_14:.1f})")
            # Regular RSI signals
            elif rsi_5 < 25 and rsi_14 < 30:
                signal_strength += 1
                reason.append(f"RSI oversold (5m:{rsi_5:.1f}, 14m:{rsi_14:.1f})")
            elif rsi_5 > 75 and rsi_14 > 70:
                signal_strength += 1
                reason.append(f"RSI overbought (5m:{rsi_5:.1f}, 14m:{rsi_14:.1f})")
        
        # 2. Moving Average Strategy (dengan trend confirmation)
        if sma_5 and sma_10 and sma_20:
            # Cek trend stability
            is_bullish, is_bearish = self.check_trend_stability(prices, sma_5, sma_20)
            
            # MA Crossover dengan konfirmasi trend
            if (sma_5 > sma_10 > sma_20 and is_bullish and 
                prices[-2] <= sma_10 and prices[-1] > sma_10):
                signal_strength += 2  # Bobot lebih tinggi
                reason.append("MA Crossover Bullish (Trend Confirmed)")
            elif (sma_5 < sma_10 < sma_20 and is_bearish and 
                  prices[-2] >= sma_10 and prices[-1] < sma_10):
                signal_strength += 2  # Bobot lebih tinggi
                reason.append("MA Crossover Bearish (Trend Confirmed)")
        
        # 3. Order Book Pressure Analysis
        if orderbook_ratio > 1.2:  # Buy pressure lebih besar 1.2x
            signal_strength += 1
            reason.append(f"Orderbook Buy Pressure ({orderbook_ratio:.2f}x)")
        elif orderbook_ratio < 0.8:  # Sell pressure lebih besar
            signal_strength += 1
            reason.append(f"Orderbook Sell Pressure ({orderbook_ratio:.2f}x)")
        
        # 4. Momentum-Based Scalping Signals
        if roc_3 and roc_5 and momentum_10:
            # Strong momentum BUY signals
            if roc_3 > SCALPING_MOMENTUM_ROC3_THRESHOLD and roc_5 > 0.5 and momentum_10 > 0:
                signal_strength += 2
                reason.append(f"Momentum BUY (ROC3:{roc_3:.2f}%, ROC5:{roc_5:.2f}%)")
            # Strong momentum SELL signals
            elif roc_3 < -SCALPING_MOMENTUM_ROC3_THRESHOLD and roc_5 < -0.5 and momentum_10 < 0:
                signal_strength += 2
                reason.append(f"Momentum SELL (ROC3:{roc_3:.2f}%, ROC5:{roc_5:.2f}%)")
        
        # 5. Volatility-Based Scalping Signals
        if atr_14 and cv:
            # Low volatility = good for scalping
            if cv < SCALPING_VOLATILITY_CV_LOW:  # Low volatility
                signal_strength += 1
                reason.append(f"Low Volatility (CV:{cv:.2f}%)")
            # High volatility = avoid scalping
            elif cv > SCALPING_VOLATILITY_CV_HIGH:
                signal_strength = 0
                reason.append(f"High Volatility (CV:{cv:.2f}%)")
        
        # 6. Trade Dominance Analysis
        if buy_ratio > 0.7:  # 70% transaksi adalah BUY
            signal_strength += 1
            reason.append(f"Trade Dominance BUY ({buy_ratio*100:.1f}%)")
        elif sell_ratio > 0.7:  # 70% transaksi adalah SELL
            signal_strength += 1
            reason.append(f"Trade Dominance SELL ({sell_ratio*100:.1f}%)")
        
        # 5. Volume confirmation (wajib dengan threshold lebih tinggi)
        if volume_ratio < VOLUME_THRESHOLD:  # Threshold dari config
            signal_strength = 0
            reason.append(f"Volume rendah ({volume_ratio:.2f}x rata-rata)")
        
        # 6. Volatility filter (hindari signal saat terlalu volatile)
        if volatility > VOLATILITY_THRESHOLD:  # Threshold dari config
            signal_strength = 0
            reason.append(f"Volatilitas tinggi ({volatility*100:.1f}%)")
        
        # 7. Cooldown check (scalping mode uses shorter cooldown)
        cooldown_time = SCALPING_COOLDOWN if SCALPING_MODE else self.signal_cooldown
        if self.last_signal_times[pair]:
            time_since_last = (current_data['timestamp'] - self.last_signal_times[pair]).total_seconds()
            if time_since_last < cooldown_time and signal_strength > 0:
                remaining_cooldown = cooldown_time - time_since_last
                signal_strength = 0
                reason.append(f"Cooldown ({remaining_cooldown:.0f}s tersisa)")
        
        # 8. Consecutive signal protection
        if self.consecutive_signals[pair] >= 3:  # Maksimal 3 signal berturut-turut
            signal_strength = 0
            reason.append(f"Terlalu banyak signal berturut-turut ({self.consecutive_signals[pair]})")
        
        # 9. Generate final signal berdasarkan strength
        min_strength = SCALPING_MIN_SIGNAL_STRENGTH if SCALPING_MODE else MIN_SIGNAL_STRENGTH
        if signal_strength >= min_strength:  # Minimal strength dari config
            if ("Bullish" in str(reason) or "Buy Pressure" in str(reason) or 
                ("oversold" in str(reason) and signal_strength >= min_strength)):
                signal = "BUY"
            elif ("Bearish" in str(reason) or "Sell Pressure" in str(reason) or 
                  ("overbought" in str(reason) and signal_strength >= min_strength)):
                signal = "SELL"
        
        # 10. Entry timing check
        if signal != "HOLD":
            timing_ok, timing_reason = self.check_entry_timing(current_data, signal, pair)
            if not timing_ok:
                signal = "HOLD"
                reason.append(f"Entry timing: {timing_reason}")
        
        # Update consecutive signals
        if signal == self.previous_signals[pair] and signal != "HOLD":
            self.consecutive_signals[pair] += 1
        else:
            self.consecutive_signals[pair] = 0
        
        # Update signal count
        self.signal_counts[pair][signal] += 1
        
        # Update last signal time jika ada signal
        if signal != "HOLD":
            self.last_signal_times[pair] = current_data['timestamp']
        
        # Tambahkan market data ke reason untuk informasi lengkap
        market_info = []
        market_info.append(f"OB:{orderbook_ratio:.2f}x")
        market_info.append(f"TD:{buy_ratio*100:.0f}%")
        market_info.append(f"Vol:{volume_ratio:.2f}x")
        
        # Add scalping-specific indicators
        if roc_3:
            market_info.append(f"ROC3:{roc_3:.2f}%")
        if cv:
            market_info.append(f"CV:{cv:.2f}%")
        
        full_reason = ", ".join(reason) if reason else "Tidak ada sinyal jelas"
        full_reason += f" | Market: {' | '.join(market_info)}"
        
        return signal, full_reason

    def send_telegram_message(self, message):
        """Kirim pesan ke Telegram jika signal BUY/SELL/EXIT"""
        # Check if Telegram is properly configured
        if TELEGRAM_TOKEN == 'ISI_TOKEN_TELEGRAM_KAMU' or TELEGRAM_CHAT_ID == 'ISI_CHAT_ID_KAMU':
            print("⚠️ [Telegram] Konfigurasi Telegram belum diatur!")
            print("📝 Cara setup Telegram:")
            print("   1. Buat bot di @BotFather di Telegram")
            print("   2. Dapatkan token bot")
            print("   3. Dapatkan chat_id (kirim /start ke bot)")
            print("   4. Edit config.py atau set environment variables:")
            print("      TELEGRAM_TOKEN=your_bot_token")
            print("      TELEGRAM_CHAT_ID=your_chat_id")
            return False
        
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            print("⚠️ [Telegram] Token atau chat_id kosong!")
            return False
            
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        try:
            resp = requests.post(url, data=payload, timeout=10)
            if resp.status_code == 200:
                print("✅ [Telegram] Pesan terkirim!")
                return True
            else:
                print(f"❌ [Telegram] Gagal kirim pesan: {resp.status_code}")
                print(f"   Response: {resp.text}")
                return False
        except requests.exceptions.Timeout:
            print("⏰ [Telegram] Timeout - koneksi lambat")
            return False
        except requests.exceptions.ConnectionError:
            print("🌐 [Telegram] Error koneksi - cek internet")
            return False
        except Exception as e:
            print(f"❌ [Telegram] Error: {e}")
            return False

    def create_telegram_message(self, signal_type, current_data, reason, pair, additional_info=None):
        """Buat pesan Telegram yang menarik dan informatif"""
        current_price = current_data['price']
        current_time = current_data['timestamp']
        pair_config = self.get_pair_config(pair)
        
        # Emoji dan warna berdasarkan signal
        if signal_type == "BUY":
            emoji = "🟢"
            signal_text = f"BELI {pair_config['name']}"
            color = "🟢"
        elif signal_type == "SELL":
            emoji = "🔴"
            signal_text = f"JUAL {pair_config['name']}"
            color = "🔴"
        elif signal_type == "EXIT":
            emoji = "🔄"
            signal_text = f"EXIT {pair_config['name']}"
            color = "🟡"
        else:
            emoji = "⚪"
            signal_text = f"HOLD {pair_config['name']}"
            color = "⚪"
        
        # Header dengan emoji
        message = f"{emoji} <b>MULTI-PAIR TRADING BOT</b> {emoji}\n"
        message += f"{'='*40}\n\n"
        
        # Pair info
        message += f"{pair_config['emoji']} <b>{pair_config['display_name']}</b>\n\n"
        
        # Signal utama
        message += f"<b>{color} SIGNAL: {signal_text}</b>\n\n"
        
        # Informasi harga
        message += f"💰 <b>Harga Saat Ini:</b> Rp {current_price:,.6f}\n"
        
        # Informasi waktu
        message += f"⏰ <b>Waktu:</b> {current_time.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        
        # Alasan signal
        message += f"📊 <b>Analisis:</b>\n{reason}\n\n"
        
        # Informasi tambahan jika ada
        if additional_info:
            message += f"📈 <b>Detail Posisi:</b>\n"
            for key, value in additional_info.items():
                message += f"   • {key}: {value}\n"
            message += "\n"
        
        # Market data
        try:
            orderbook_ratio, buy_vol, sell_vol = self.get_orderbook_pressure(pair)
            buy_ratio, sell_ratio, buy_count, sell_count = self.get_trade_dominance(pair)
            
            message += f"📊 <b>Market Data:</b>\n"
            message += f"   • Order Book: {orderbook_ratio:.2f}x (Buy/Sell)\n"
            message += f"   • Trade Dominance: {buy_ratio*100:.0f}% Buy, {sell_ratio*100:.0f}% Sell\n"
            message += f"   • Volume Buy: {buy_vol:,.0f}\n"
            message += f"   • Volume Sell: {sell_vol:,.0f}\n\n"
        except:
            pass
        
        # Footer
        message += f"{'='*40}\n"
        message += f"🤖 <i>Multi-Pair Trading Bot v2.0</i>\n"
        message += f"📱 <i>Powered by AI & Technical Analysis</i>"
        
        return message

    def execute_trade(self, signal, current_data, reason, pair):
        """Execute trade berdasarkan signal untuk pair tertentu"""
        current_price = current_data['price']
        current_time = current_data['timestamp']
        
        # === Kirim signal ke Telegram untuk BUY/SELL/EXIT ===
        if signal in ("BUY", "SELL", "EXIT"):
            additional_info = {}
            
            if signal == "BUY" and self.current_positions[pair] != "LONG":
                # Close SHORT position if exists
                if self.current_positions[pair] == "SHORT":
                    profit_loss = ((self.entry_prices[pair] - current_price) / self.entry_prices[pair]) * 100
                    print(f"🔄 CLOSE SHORT {pair}: Profit/Loss {profit_loss:+.2f}%")
                    additional_info["Close SHORT P/L"] = f"{profit_loss:+.2f}%"
                
                # Calculate better entry price
                entry_price = self.calculate_better_entry_price(current_data, "BUY", pair)
                
                # Open LONG position
                self.current_positions[pair] = "LONG"
                self.entry_prices[pair] = entry_price
                self.entry_times[pair] = current_time
                self.stop_losses[pair] = entry_price * (1 - self.stop_loss_percent)
                self.take_profits[pair] = entry_price * (1 + self.take_profit_percent)
                
                # Tambahkan info posisi
                additional_info["Entry Price"] = f"Rp {entry_price:,.6f}"
                additional_info["Stop Loss"] = f"Rp {self.stop_losses[pair]:,.6f} (-{self.stop_loss_percent*100:.1f}%)"
                additional_info["Take Profit"] = f"Rp {self.take_profits[pair]:,.6f} (+{self.take_profit_percent*100:.1f}%)"
                additional_info["Position"] = "LONG"
                
                print(f"🟢 ENTRY LONG {pair}: Rp {entry_price:.6f} (Market: Rp {current_price:.6f})")
                print(f"   Stop Loss: Rp {self.stop_losses[pair]:.6f} (-{self.stop_loss_percent*100:.1f}%)")
                print(f"   Take Profit: Rp {self.take_profits[pair]:.6f} (+{self.take_profit_percent*100:.1f}%)")
                
            elif signal == "SELL" and self.current_positions[pair] != "SHORT":
                # Close LONG position if exists
                if self.current_positions[pair] == "LONG":
                    profit_loss = ((current_price - self.entry_prices[pair]) / self.entry_prices[pair]) * 100
                    print(f" CLOSE LONG {pair}: Profit/Loss {profit_loss:+.2f}%")
                    additional_info["Close LONG P/L"] = f"{profit_loss:+.2f}%"
                
                # Calculate better entry price
                entry_price = self.calculate_better_entry_price(current_data, "SELL", pair)
                
                # Open SHORT position
                self.current_positions[pair] = "SHORT"
                self.entry_prices[pair] = entry_price
                self.entry_times[pair] = current_time
                self.stop_losses[pair] = entry_price * (1 + self.stop_loss_percent)
                self.take_profits[pair] = entry_price * (1 - self.take_profit_percent)
                
                # Tambahkan info posisi
                additional_info["Entry Price"] = f"Rp {entry_price:,.6f}"
                additional_info["Stop Loss"] = f"Rp {self.stop_losses[pair]:,.6f} (+{self.stop_loss_percent*100:.1f}%)"
                additional_info["Take Profit"] = f"Rp {self.take_profits[pair]:,.6f} (-{self.take_profit_percent*100:.1f}%)"
                additional_info["Position"] = "SHORT"
                
                print(f"🔴 ENTRY SHORT {pair}: Rp {entry_price:.6f} (Market: Rp {current_price:.6f})")
                print(f"   Stop Loss: Rp {self.stop_losses[pair]:.6f} (+{self.stop_loss_percent*100:.1f}%)")
                print(f"   Take Profit: Rp {self.take_profits[pair]:.6f} (-{self.take_profit_percent*100:.1f}%)")
            
            elif signal.startswith("EXIT"):
                # Close current position
                if self.current_positions[pair] == "LONG":
                    profit_loss = ((current_price - self.entry_prices[pair]) / self.entry_prices[pair]) * 100
                    print(f"🔄 EXIT LONG {pair}: Profit/Loss {profit_loss:+.2f}%")
                    additional_info["Position"] = "LONG"
                    additional_info["Entry Price"] = f"Rp {self.entry_prices[pair]:,.6f}"
                    additional_info["Exit Price"] = f"Rp {current_price:,.6f}"
                    additional_info["Profit/Loss"] = f"{profit_loss:+.2f}%"
                    
                    # Tambahkan emoji berdasarkan profit/loss
                    if profit_loss > 0:
                        additional_info["Status"] = "✅ PROFIT"
                    elif profit_loss < 0:
                        additional_info["Status"] = "❌ LOSS"
                    else:
                        additional_info["Status"] = "➖ BREAKEVEN"
                        
                elif self.current_positions[pair] == "SHORT":
                    profit_loss = ((self.entry_prices[pair] - current_price) / self.entry_prices[pair]) * 100
                    print(f" EXIT SHORT {pair}: Profit/Loss {profit_loss:+.2f}%")
                    additional_info["Position"] = "SHORT"
                    additional_info["Entry Price"] = f"Rp {self.entry_prices[pair]:,.6f}"
                    additional_info["Exit Price"] = f"Rp {current_price:,.6f}"
                    additional_info["Profit/Loss"] = f"{profit_loss:+.2f}%"
                    
                    # Tambahkan emoji berdasarkan profit/loss
                    if profit_loss > 0:
                        additional_info["Status"] = "✅ PROFIT"
                    elif profit_loss < 0:
                        additional_info["Status"] = "❌ LOSS"
                    else:
                        additional_info["Status"] = "➖ BREAKEVEN"
                
                # Reset position
                self.current_positions[pair] = None
                self.entry_prices[pair] = None
                self.entry_times[pair] = None
                self.stop_losses[pair] = None
                self.take_profits[pair] = None
            
            # Kirim pesan Telegram
            telegram_msg = self.create_telegram_message(signal, current_data, reason, pair, additional_info)
            self.send_telegram_message(telegram_msg)
    
    def show_statistics(self):
        """Menampilkan statistik data historis untuk semua pairs"""
        print(f"\n📊 STATISTIK SEMUA PAIRS:")
        print(f"{'='*60}")
        
        for pair_config in self.trading_pairs:
            if not pair_config['enabled']:
                continue
                
            pair = pair_config['pair']
            if len(self.price_history[pair]) == 0:
                print(f"📊 {pair_config['display_name']}: Tidak ada data historis")
                continue
            
            prices = [p['price'] for p in self.price_history[pair]]
            volumes = [p['volume'] for p in self.price_history[pair]]
            
            print(f"\n{pair_config['emoji']} <b>{pair_config['display_name']}:</b>")
            print(f"   Total data points: {len(self.price_history[pair])}")
            print(f"   Periode: {self.price_history[pair][0]['timestamp'].strftime('%Y-%m-%d %H:%M')} - {self.price_history[pair][-1]['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            print(f"   Harga tertinggi: Rp {max(prices):.6f}")
            print(f"   Harga terendah: Rp {min(prices):.6f}")
            print(f"   Harga rata-rata: Rp {np.mean(prices):.6f}")
            print(f"   Volume rata-rata: {np.mean(volumes):.2f}")
            
            # Calculate price change
            if len(prices) > 1:
                price_change = ((prices[-1] - prices[0]) / prices[0]) * 100
                print(f"   Perubahan harga: {price_change:+.2f}%")
            
                # Signal statistics
                total_signals = sum(self.signal_counts[pair].values())
                if total_signals > 0:
                    print(f"   BUY signals: {self.signal_counts[pair]['BUY']} ({self.signal_counts[pair]['BUY']/total_signals*100:.1f}%)")
                    print(f"   SELL signals: {self.signal_counts[pair]['SELL']} ({self.signal_counts[pair]['SELL']/total_signals*100:.1f}%)")
                    print(f"   HOLD signals: {self.signal_counts[pair]['HOLD']} ({self.signal_counts[pair]['HOLD']/total_signals*100:.1f}%)")
                
                # Current position
                if self.current_positions[pair]:
                    print(f"   Posisi saat ini: {self.current_positions[pair]}")
                    if self.entry_prices[pair]:
                        current_price = prices[-1] if prices else 0
                        if self.current_positions[pair] == "LONG":
                            profit_loss = ((current_price - self.entry_prices[pair]) / self.entry_prices[pair]) * 100
                        else:
                            profit_loss = ((self.entry_prices[pair] - current_price) / self.entry_prices[pair]) * 100
                        print(f"   P/L: {profit_loss:+.2f}%")
                else:
                    print(f"   Posisi saat ini: Tidak ada posisi aktif")
            else:
                print(f"   Perubahan harga: Data tidak cukup")
                print(f"   Posisi saat ini: Tidak ada posisi aktif")
        
        # Trading parameters
        print(f"\n💰 PARAMETER TRADING:")
        print(f"   Stop Loss: {self.stop_loss_percent*100:.1f}%")
        print(f"   Take Profit: {self.take_profit_percent*100:.1f}%")
        print(f"   Max Hold Time: {self.max_hold_time/60:.0f} menit")
        print(f"   Cooldown: {self.signal_cooldown} detik")
        print(f"   Signal Strength Required: 3+ points")
        print(f"   Smart saving: Hanya perubahan signifikan")
    
    def run(self):
        """Menjalankan strategi untuk semua pairs"""
        print("🚀 Multi-Pair Trading Bot - Advanced Version")
        print("=" * 80)
        print("Monitoring multiple pairs dengan Order Book + Trade Dominance analysis...")
        print("=" * 80)
        
        # Show enabled pairs
        enabled_pairs = [p for p in self.trading_pairs if p['enabled']]
        print(f"\n📈 Monitoring {len(enabled_pairs)} pairs:")
        for pair in enabled_pairs:
            print(f"   {pair['emoji']} {pair['display_name']}")
        
        # Show initial statistics
        self.show_statistics()
        
        # Show timeframe quality analysis
        self.show_timeframe_analysis()
        
        # Show data management dashboard
        self.show_data_management_dashboard()
        
        try:
            while True:
                # Process each pair
                for pair_config in self.trading_pairs:
                    if not pair_config['enabled']:
                        continue
                        
                    pair = pair_config['pair']
                    current_data = self.get_price(pair)
                    if not current_data:
                        continue
                
                    # Check if there's a significant change
                    if self.has_significant_change(current_data, pair):
                        # Update price history only when there's a change
                        self.price_history[pair].append(current_data)
                        
                        # Optimize data points based on current tier
                        self.get_optimized_data_points(pair)
                        
                        # Update last saved data
                        self.last_saved_data[pair] = current_data.copy()
                        
                        # Save data immediately when there's a change
                        self.save_historical_data_enhanced(pair)
                        
                        # Generate signal
                        signal, reason = self.generate_signal(current_data, pair)
                        
                        # Execute trade
                        self.execute_trade(signal, current_data, reason, pair)
                        
                        # Display results
                        timestamp = current_data['timestamp'].strftime('%H:%M:%S')
                        print(f"\n⏰ {timestamp} | {pair_config['emoji']} {pair_config['display_name']} | Rp {current_data['price']:.6f} | 📊 {len(self.price_history[pair])} data points")
                        
                        if signal != self.previous_signals[pair]:
                            if signal == "BUY":
                                print(f"🟢 SIGNAL: BELI {pair_config['name']}!")
                                print(f"   Alasan: {reason}")
                            elif signal == "SELL":
                                print(f"🔴 SIGNAL: JUAL {pair_config['name']}!")
                                print(f"   Alasan: {reason}")
                            elif signal.startswith("EXIT"):
                                print(f"🔄 SIGNAL: {signal}")
                                print(f"   Alasan: {reason}")
                            else:
                                print(f"⚪ SIGNAL: HOLD")
                                print(f"   Alasan: {reason}")
                            
                            self.previous_signals[pair] = signal
                        else:
                            print(f"   Signal: {signal} | {reason}")
                            
                            # Show current position info
                            if self.current_positions[pair]:
                                current_price = current_data['price']
                                if self.current_positions[pair] == "LONG":
                                    profit_loss = ((current_price - self.entry_prices[pair]) / self.entry_prices[pair]) * 100
                                else:  # SHORT
                                    profit_loss = ((self.entry_prices[pair] - current_price) / self.entry_prices[pair]) * 100
                                
                                print(f"   📊 Posisi: {self.current_positions[pair]} | P/L: {profit_loss:+.2f}%")
                    else:
                        # No significant change, just show current status
                        timestamp = current_data['timestamp'].strftime('%H:%M:%S')
                        print(f"⏰ {timestamp} | {pair_config['emoji']} {pair_config['display_name']} | Rp {current_data['price']:.6f} | 📊 {len(self.price_history[pair])} data points")
                        print(f"   Signal: HOLD | Tidak ada perubahan signifikan")
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bot dihentikan oleh user")
            print("💾 Menyimpan data historis...")
            for pair_config in self.trading_pairs:
                if pair_config['enabled']:
                    self.save_historical_data(pair_config['pair'])
            print("✅ Data berhasil disimpan!")
            print("📊 Total pairs monitored:", len([p for p in self.trading_pairs if p['enabled']]))
            print("📈 Signal statistics:")
            for pair_config in self.trading_pairs:
                if pair_config['enabled']:
                    pair = pair_config['pair']
                    total_signals = sum(self.signal_counts[pair].values())
                    if total_signals > 0:
                        print(f"   {pair_config['display_name']}: BUY:{self.signal_counts[pair]['BUY']} SELL:{self.signal_counts[pair]['SELL']} HOLD:{self.signal_counts[pair]['HOLD']}")
            print(" Storage efficiency: Smart saving (hanya perubahan)")
            print("👋 Goodbye!")

    def analyze_timeframe_quality(self, pair):
        """Analisis kualitas timeframe untuk pair tertentu"""
        if len(self.price_history[pair]) < 10:
            return {
                'quality_score': 0,
                'quality_level': "🔴 INSUFFICIENT",
                'quality_factors': ["Data tidak cukup untuk analisis"],
                'recommendation': "Perlu minimal 10 data points",
                'stats': {
                    'data_points': len(self.price_history[pair]),
                    'duration_hours': 0,
                    'avg_interval_seconds': 0,
                    'price_volatility_percent': 0,
                    'price_range_percent': 0
                }
            }
        
        prices = [p['price'] for p in self.price_history[pair]]
        timestamps = [p['timestamp'] for p in self.price_history[pair]]
        
        # Calculate timeframe statistics
        total_duration = (timestamps[-1] - timestamps[0]).total_seconds() / 3600  # hours
        data_points = len(self.price_history[pair])
        avg_interval = total_duration / data_points if data_points > 1 else 0
        
        # Calculate data quality metrics
        price_volatility = np.std(prices) / np.mean(prices) * 100
        price_range = ((max(prices) - min(prices)) / min(prices)) * 100
        
        # Determine timeframe quality
        quality_score = 0
        quality_factors = []
        
        # Data quantity factor
        if data_points >= 1000:
            quality_score += 30
            quality_factors.append("Data points: Excellent (1000+)")
        elif data_points >= 500:
            quality_score += 20
            quality_factors.append("Data points: Good (500+)")
        elif data_points >= 100:
            quality_score += 10
            quality_factors.append("Data points: Fair (100+)")
        else:
            quality_factors.append("Data points: Poor (<100)")
        
        # Time duration factor
        if total_duration >= 168:  # 1 week
            quality_score += 25
            quality_factors.append("Duration: Excellent (1+ week)")
        elif total_duration >= 72:  # 3 days
            quality_score += 15
            quality_factors.append("Duration: Good (3+ days)")
        elif total_duration >= 24:  # 1 day
            quality_score += 10
            quality_factors.append("Duration: Fair (1+ day)")
        else:
            quality_factors.append("Duration: Poor (<1 day)")
        
        # Data consistency factor
        if avg_interval <= 10:  # 10 seconds or less
            quality_score += 25
            quality_factors.append("Interval: Excellent (≤10s)")
        elif avg_interval <= 30:  # 30 seconds
            quality_score += 15
            quality_factors.append("Interval: Good (≤30s)")
        elif avg_interval <= 60:  # 1 minute
            quality_score += 10
            quality_factors.append("Interval: Fair (≤1m)")
        else:
            quality_factors.append("Interval: Poor (>1m)")
        
        # Market activity factor
        if price_volatility >= 1.0:
            quality_score += 20
            quality_factors.append("Volatility: Active market")
        elif price_volatility >= 0.5:
            quality_score += 15
            quality_factors.append("Volatility: Moderate")
        else:
            quality_score += 5
            quality_factors.append("Volatility: Low activity")
        
        # Determine overall quality
        if quality_score >= 80:
            quality_level = "🟢 EXCELLENT"
            recommendation = "Timeframe optimal untuk scalping"
        elif quality_score >= 60:
            quality_level = "🟡 GOOD"
            recommendation = "Timeframe cukup baik, lanjutkan monitoring"
        elif quality_score >= 40:
            quality_level = "🟠 FAIR"
            recommendation = "Perlu lebih banyak data untuk akurasi optimal"
        else:
            quality_level = "🔴 POOR"
            recommendation = "Perlu waktu lebih lama untuk membangun timeframe"
        
        return {
            'quality_score': quality_score,
            'quality_level': quality_level,
            'quality_factors': quality_factors,
            'recommendation': recommendation,
            'stats': {
                'data_points': data_points,
                'duration_hours': total_duration,
                'avg_interval_seconds': avg_interval,
                'price_volatility_percent': price_volatility,
                'price_range_percent': price_range
            }
        }
    
    def show_timeframe_analysis(self):
        """Tampilkan analisis timeframe untuk semua pairs"""
        print(f"\n📊 TIMEFRAME QUALITY ANALYSIS:")
        print(f"{'='*60}")
        
        for pair_config in self.trading_pairs:
            if not pair_config['enabled']:
                continue
                
            pair = pair_config['pair']
            analysis = self.analyze_timeframe_quality(pair)
            
            print(f"\n{pair_config['emoji']} {pair_config['display_name']}:")
            print(f"   Quality: {analysis['quality_level']} ({analysis['quality_score']}/100)")
            print(f"   Recommendation: {analysis['recommendation']}")
            
            stats = analysis['stats']
            print(f"   📈 Data Points: {stats['data_points']:,}")
            print(f"   ⏰ Duration: {stats['duration_hours']:.1f} hours")
            print(f"   🔄 Avg Interval: {stats['avg_interval_seconds']:.1f}s")
            print(f"   📊 Volatility: {stats['price_volatility_percent']:.2f}%")
            print(f"   📈 Price Range: {stats['price_range_percent']:.2f}%")
            
            print(f"   📋 Quality Factors:")
            for factor in analysis['quality_factors']:
                print(f"      • {factor}")

    def get_current_tier_settings(self):
        """Dapatkan setting untuk tier saat ini"""
        return self.data_tiers.get(self.current_tier, self.data_tiers['scalping'])
    
    def switch_data_tier(self, tier_name):
        """Switch ke tier data yang berbeda"""
        if tier_name in self.data_tiers:
            self.current_tier = tier_name
            print(f"🔄 Switched to {tier_name} tier: {self.data_tiers[tier_name]['purpose']}")
            return True
        else:
            print(f"❌ Invalid tier: {tier_name}")
            return False
    
    def compress_data(self, data_list):
        """Compress data untuk menghemat storage"""
        if not ENABLE_DATA_COMPRESSION:
            return data_list
        
        compressed_data = []
        for i, item in enumerate(data_list):
            if i == 0 or i == len(data_list) - 1:  # Keep first and last
                compressed_data.append(item)
            elif i % 5 == 0:  # Keep every 5th item
                compressed_data.append(item)
            elif abs(item['price'] - data_list[i-1]['price']) / data_list[i-1]['price'] > 0.001:  # Keep significant changes
                compressed_data.append(item)
        
        return compressed_data
    
    def archive_old_data(self, pair):
        """Archive data yang sudah lama"""
        if not ENABLE_DATA_ARCHIVING:
            return
        
        current_time = datetime.now()
        data_to_archive = []
        data_to_keep = []
        
        for item in self.price_history[pair]:
            age_hours = (current_time - item['timestamp']).total_seconds() / 3600
            if age_hours > ARCHIVE_INTERVAL_HOURS:
                data_to_archive.append(item)
            else:
                data_to_keep.append(item)
        
        if data_to_archive:
            self.archived_data[pair].extend(data_to_archive)
            self.price_history[pair] = data_to_keep
            print(f"📦 Archived {len(data_to_archive)} old data points for {pair}")
    
    def get_optimized_data_points(self, pair):
        """Dapatkan jumlah data points optimal berdasarkan tier"""
        tier_settings = self.get_current_tier_settings()
        max_points = tier_settings['max_points']
        
        # Jika data melebihi max_points, compress atau archive
        if len(self.price_history[pair]) > max_points:
            if ENABLE_DATA_ARCHIVING:
                self.archive_old_data(pair)
            
            # Trim ke max_points
            if len(self.price_history[pair]) > max_points:
                excess = len(self.price_history[pair]) - max_points
                self.price_history[pair] = self.price_history[pair][excess:]
                print(f"✂️ Trimmed {excess} data points for {pair}")
        
        return len(self.price_history[pair])
    
    def save_historical_data_enhanced(self, pair):
        """Save data historis dengan compression dan archiving"""
        try:
            data_file = self.data_files[pair]
            
            # Compress data jika enabled
            data_to_save = self.compress_data(self.price_history[pair]) if ENABLE_DATA_COMPRESSION else self.price_history[pair]
            
            # Convert datetime objects to strings for JSON serialization
            data_to_save_serialized = []
            for item in data_to_save:
                item_copy = item.copy()
                item_copy['timestamp'] = item['timestamp'].isoformat()
                data_to_save_serialized.append(item_copy)
            
            # Save main data
            with open(data_file, 'w') as f:
                json.dump(data_to_save_serialized, f, indent=2)
            
            # Save archived data if exists
            if self.archived_data[pair]:
                archive_file = f"{pair}_archived_data.json"
                archived_serialized = []
                for item in self.archived_data[pair]:
                    item_copy = item.copy()
                    item_copy['timestamp'] = item['timestamp'].isoformat()
                    archived_serialized.append(item_copy)
                
                with open(archive_file, 'w') as f:
                    json.dump(archived_serialized, f, indent=2)
            
            print(f"💾 Saved {len(data_to_save)} data points to {data_file}")
            if self.archived_data[pair]:
                print(f"📦 Archived data: {len(self.archived_data[pair])} points")
                
        except Exception as e:
            print(f"⚠️ Error saving data for {pair}: {e}")
    
    def load_historical_data_enhanced(self, pair):
        """Load data historis dengan archived data"""
        try:
            data_file = self.data_files[pair]
            archive_file = f"{pair}_archived_data.json"
            
            # Load main data
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    # Convert string timestamps back to datetime objects
                    for item in data:
                        item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                    self.price_history[pair] = data
                    print(f"📂 Loaded {len(self.price_history[pair])} historical data points for {pair}")
                    
                    # Set last saved data to the most recent entry
                    if self.price_history[pair]:
                        self.last_saved_data[pair] = self.price_history[pair][-1].copy()
            else:
                print(f"📂 No historical data found for {pair}, starting fresh")
            
            # Load archived data
            if os.path.exists(archive_file):
                with open(archive_file, 'r') as f:
                    archived_data = json.load(f)
                    # Convert string timestamps back to datetime objects
                    for item in archived_data:
                        item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                    self.archived_data[pair] = archived_data
                    print(f"📦 Loaded {len(self.archived_data[pair])} archived data points for {pair}")
                    
        except Exception as e:
            print(f"⚠️ Error loading historical data for {pair}: {e}")
            self.price_history[pair] = []
            self.archived_data[pair] = []

    def show_data_management_dashboard(self):
        """Tampilkan dashboard manajemen data"""
        print(f"\n📊 DATA MANAGEMENT DASHBOARD:")
        print(f"{'='*60}")
        
        current_tier = self.get_current_tier_settings()
        print(f"🎯 Current Tier: {self.current_tier.upper()}")
        print(f"📋 Purpose: {current_tier['purpose']}")
        print(f"📈 Max Points: {current_tier['max_points']:,}")
        print(f"⏰ Interval: {current_tier['interval']} seconds")
        
        print(f"\n📊 Available Tiers:")
        for tier_name, settings in self.data_tiers.items():
            status = "🟢 ACTIVE" if tier_name == self.current_tier else "⚪ Available"
            print(f"   {tier_name.upper()}: {settings['max_points']:,} points | {settings['interval']}s | {status}")
        
        print(f"\n💾 Storage Settings:")
        print(f"   Compression: {'✅ Enabled' if ENABLE_DATA_COMPRESSION else '❌ Disabled'}")
        print(f"   Archiving: {'✅ Enabled' if ENABLE_DATA_ARCHIVING else '❌ Disabled'}")
        print(f"   Cache: {'✅ Enabled' if ENABLE_DATA_CACHING else '❌ Disabled'}")
        print(f"   Archive Interval: {ARCHIVE_INTERVAL_HOURS} hours")
        
        print(f"\n📈 Data Statistics by Pair:")
        total_main_data = 0
        total_archived_data = 0
        
        for pair_config in self.trading_pairs:
            if not pair_config['enabled']:
                continue
                
            pair = pair_config['pair']
            main_data_count = len(self.price_history[pair])
            archived_data_count = len(self.archived_data[pair])
            total_main_data += main_data_count
            total_archived_data += archived_data_count
            
            print(f"   {pair_config['emoji']} {pair_config['display_name']}:")
            print(f"      Main: {main_data_count:,} points")
            print(f"      Archived: {archived_data_count:,} points")
            print(f"      Total: {main_data_count + archived_data_count:,} points")
        
        print(f"\n📊 Total Data:")
        print(f"   Main Data: {total_main_data:,} points")
        print(f"   Archived Data: {total_archived_data:,} points")
        print(f"   Total: {total_main_data + total_archived_data:,} points")
        
        # Calculate storage usage
        estimated_size_mb = (total_main_data + total_archived_data) * 0.0002  # ~200 bytes per data point
        print(f"   Estimated Size: {estimated_size_mb:.2f} MB")
        
        print(f"\n💡 Recommendations:")
        if total_main_data < 1000:
            print(f"   🔴 Need more data: Current data insufficient for reliable analysis")
        elif total_main_data < 5000:
            print(f"   🟡 Good progress: Data building up nicely")
        else:
            print(f"   🟢 Excellent: Sufficient data for advanced analysis")
        
        if total_archived_data > 0:
            print(f"   📦 Archiving working: {total_archived_data:,} points archived")
        
        print(f"   💾 Consider switching tiers based on your trading strategy")

if __name__ == "__main__":
    # Buat bot dengan semua pairs yang enabled
    enabled_pairs = [p for p in TRADING_PAIRS if p['enabled']]
    strategy = SmartTradingStrategy(enabled_pairs)
    strategy.run() 