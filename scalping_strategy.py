import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import ta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class PEPEScalpingStrategy:
    def __init__(self):
        self.url = "https://indodax.com/api/pepe_idr/ticker"
        self.historical_data = []
        self.model = None
        self.scaler = StandardScaler()
        self.previous_signal = None
        
    def get_current_price(self):
        """Mengambil harga saat ini"""
        try:
            response = requests.get(self.url)
            data = response.json()
            ticker = data['ticker']
            return {
                'timestamp': datetime.now(),
                'price': float(ticker['last']),
                'high': float(ticker['high']),
                'low': float(ticker['low']),
                'volume': float(ticker['vol_pepe']),
                'buy': float(ticker['buy']),
                'sell': float(ticker['sell'])
            }
        except Exception as e:
            print(f"Error mengambil data: {e}")
            return None
    
    def get_historical_data(self, hours=24):
        """Mengambil data historis (simulasi)"""
        # Untuk demo, kita akan generate data historis
        current_price = self.get_current_price()
        if not current_price:
            return []
        
        data = []
        base_price = current_price['price']
        
        for i in range(hours * 60):  # Data per menit
            timestamp = datetime.now() - timedelta(minutes=i)
            # Simulasi fluktuasi harga
            noise = np.random.normal(0, 0.001)
            price = base_price * (1 + noise)
            
            data.append({
                'timestamp': timestamp,
                'price': price,
                'volume': current_price['volume'] * (1 + np.random.normal(0, 0.1))
            })
        
        return list(reversed(data))
    
    def calculate_indicators(self, df):
        """Menghitung indikator teknikal"""
        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(df['price'], window=14).rsi()
        
        # Moving Averages
        df['sma_5'] = ta.trend.SMAIndicator(df['price'], window=5).sma_indicator()
        df['sma_20'] = ta.trend.SMAIndicator(df['price'], window=20).sma_indicator()
        df['ema_12'] = ta.trend.EMAIndicator(df['price'], window=12).ema_indicator()
        df['ema_26'] = ta.trend.EMAIndicator(df['price'], window=26).ema_indicator()
        
        # MACD
        macd = ta.trend.MACD(df['price'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['price'])
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_middle'] = bb.bollinger_mavg()
        
        # Volume indicators
        df['volume_sma'] = ta.volume.volume_sma(df['price'], df['volume'], window=20)
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Price momentum
        df['price_change'] = df['price'].pct_change()
        df['price_change_5'] = df['price'].pct_change(periods=5)
        
        return df
    
    def generate_signals(self, df):
        """Generate sinyal beli/jual berdasarkan indikator"""
        signals = []
        
        for i in range(len(df)):
            if i < 20:  # Skip data awal yang tidak cukup
                signals.append('HOLD')
                continue
                
            row = df.iloc[i]
            signal = 'HOLD'
            
            # RSI Strategy
            if row['rsi'] < 30:
                signal = 'BUY'
            elif row['rsi'] > 70:
                signal = 'SELL'
            
            # Moving Average Crossover
            if row['sma_5'] > row['sma_20'] and df.iloc[i-1]['sma_5'] <= df.iloc[i-1]['sma_20']:
                signal = 'BUY'
            elif row['sma_5'] < row['sma_20'] and df.iloc[i-1]['sma_5'] >= df.iloc[i-1]['sma_20']:
                signal = 'SELL'
            
            # MACD Strategy
            if row['macd'] > row['macd_signal'] and df.iloc[i-1]['macd'] <= df.iloc[i-1]['macd_signal']:
                signal = 'BUY'
            elif row['macd'] < row['macd_signal'] and df.iloc[i-1]['macd'] >= df.iloc[i-1]['macd_signal']:
                signal = 'SELL'
            
            # Bollinger Bands
            if row['price'] <= row['bb_lower']:
                signal = 'BUY'
            elif row['price'] >= row['bb_upper']:
                signal = 'SELL'
            
            # Volume confirmation
            if row['volume_ratio'] < 0.5:  # Volume rendah, kurang reliable
                if signal != 'HOLD':
                    signal = 'HOLD'
            
            signals.append(signal)
        
        return signals
    
    def train_ai_model(self, df):
        """Train AI model untuk prediksi harga"""
        # Prepare features
        features = ['rsi', 'sma_5', 'sma_20', 'ema_12', 'ema_26', 
                   'macd', 'macd_signal', 'macd_histogram',
                   'bb_upper', 'bb_lower', 'bb_middle',
                   'volume_ratio', 'price_change', 'price_change_5']
        
        # Remove NaN values
        df_clean = df.dropna()
        
        if len(df_clean) < 50:
            print("Data tidak cukup untuk training AI model")
            return
        
        X = df_clean[features]
        y = df_clean['price']
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        print("AI Model berhasil di-training!")
    
    def predict_price(self, current_data):
        """Prediksi harga menggunakan AI"""
        if self.model is None:
            return None
        
        features = [current_data['rsi'], current_data['sma_5'], current_data['sma_20'],
                   current_data['ema_12'], current_data['ema_26'], current_data['macd'],
                   current_data['macd_signal'], current_data['macd_histogram'],
                   current_data['bb_upper'], current_data['bb_lower'], current_data['bb_middle'],
                   current_data['volume_ratio'], current_data['price_change'], current_data['price_change_5']]
        
        # Handle NaN values
        features = [0 if pd.isna(f) else f for f in features]
        
        predicted_price = self.model.predict([features])[0]
        return predicted_price
    
    def run_strategy(self):
        """Menjalankan strategi scalping"""
        print("🚀 Memulai PEPE Scalping Strategy...")
        print("=" * 50)
        
        # Get historical data
        print("📊 Mengambil data historis...")
        historical_data = self.get_historical_data(hours=24)
        
        if not historical_data:
            print("❌ Gagal mengambil data historis")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        df = self.calculate_indicators(df)
        
        # Train AI model
        print("🤖 Training AI model...")
        self.train_ai_model(df)
        
        # Generate signals
        signals = self.generate_signals(df)
        df['signal'] = signals
        
        print("✅ Strategi siap! Monitoring harga PEPE...")
        print("=" * 50)
        
        # Real-time monitoring
        while True:
            current_data = self.get_current_price()
            if not current_data:
                time.sleep(5)
                continue
            
            # Update historical data
            self.historical_data.append(current_data)
            if len(self.historical_data) > 1440:  # Keep last 24 hours (1440 minutes)
                self.historical_data.pop(0)
            
            # Create current DataFrame
            current_df = pd.DataFrame(self.historical_data)
            if len(current_df) < 20:
                time.sleep(5)
                continue
            
            current_df = self.calculate_indicators(current_df)
            current_signals = self.generate_signals(current_df)
            
            current_signal = current_signals[-1] if current_signals else 'HOLD'
            current_row = current_df.iloc[-1]
            
            # AI Prediction
            ai_prediction = self.predict_price(current_row)
            
            # Display results
            timestamp = current_data['timestamp'].strftime('%H:%M:%S')
            print(f"\n⏰ {timestamp} | 💰 Rp {current_data['price']:.6f}")
            
            if current_signal != self.previous_signal:
                if current_signal == 'BUY':
                    print(f"🟢 SIGNAL: BELI PEPE!")
                    print(f"   RSI: {current_row['rsi']:.2f}")
                    print(f"   Volume Ratio: {current_row['volume_ratio']:.2f}")
                elif current_signal == 'SELL':
                    print(f"🔴 SIGNAL: JUAL PEPE!")
                    print(f"   RSI: {current_row['rsi']:.2f}")
                    print(f"   Volume Ratio: {current_row['volume_ratio']:.2f}")
                else:
                    print(f"⚪ SIGNAL: HOLD")
                
                if ai_prediction:
                    price_diff = ((ai_prediction - current_data['price']) / current_data['price']) * 100
                    print(f"🤖 AI Prediksi: Rp {ai_prediction:.6f} ({price_diff:+.2f}%)")
                
                self.previous_signal = current_signal
            else:
                print(f"   Signal: {current_signal} | RSI: {current_row['rsi']:.2f}")
            
            time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    strategy = PEPEScalpingStrategy()
    strategy.run_strategy() 