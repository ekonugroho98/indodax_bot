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
            self.load_historical_data(pair)
        
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
        rsi_5 = self.calculate_rsi(prices, 5)   # Short term
        rsi_14 = self.calculate_rsi(prices, 14) # Medium term
        
        return rsi_5, rsi_14
    
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
        
        # Multi-timeframe RSI
        rsi_5, rsi_14 = self.calculate_multi_timeframe_rsi(prices)
        
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
        
        # 1. RSI Strategy (dengan konfirmasi multi-timeframe)
        if rsi_5 and rsi_14:
            if rsi_5 < 25 and rsi_14 < 30:  # Lebih ekstrem
                signal_strength += 1
                reason.append(f"RSI oversold (5m:{rsi_5:.1f}, 14m:{rsi_14:.1f})")
            elif rsi_5 > 75 and rsi_14 > 70:  # Lebih ekstrem
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
        
        # 4. Trade Dominance Analysis
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
        
        # 7. Cooldown check
        if self.last_signal_times[pair]:
            time_since_last = (current_data['timestamp'] - self.last_signal_times[pair]).total_seconds()
            if time_since_last < self.signal_cooldown and signal_strength > 0:
                remaining_cooldown = self.signal_cooldown - time_since_last
                signal_strength = 0
                reason.append(f"Cooldown ({remaining_cooldown:.0f}s tersisa)")
        
        # 8. Consecutive signal protection
        if self.consecutive_signals[pair] >= 3:  # Maksimal 3 signal berturut-turut
            signal_strength = 0
            reason.append(f"Terlalu banyak signal berturut-turut ({self.consecutive_signals[pair]})")
        
        # 9. Generate final signal berdasarkan strength
        if signal_strength >= MIN_SIGNAL_STRENGTH:  # Minimal strength dari config
            if ("Bullish" in str(reason) or "Buy Pressure" in str(reason) or 
                ("oversold" in str(reason) and signal_strength >= MIN_SIGNAL_STRENGTH)):
                signal = "BUY"
            elif ("Bearish" in str(reason) or "Sell Pressure" in str(reason) or 
                  ("overbought" in str(reason) and signal_strength >= MIN_SIGNAL_STRENGTH)):
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
                        if len(self.price_history[pair]) > MAX_DATA_POINTS:  # Keep last data points dari config
                            self.price_history[pair].pop(0)
                        
                        # Update last saved data
                        self.last_saved_data[pair] = current_data.copy()
                        
                        # Save data immediately when there's a change
                        self.save_historical_data(pair)
                        
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

if __name__ == "__main__":
    # Buat bot dengan semua pairs yang enabled
    enabled_pairs = [p for p in TRADING_PAIRS if p['enabled']]
    strategy = SmartTradingStrategy(enabled_pairs)
    strategy.run() 