# PEPE/IDR Scalping Strategy Bot

Bot trading otomatis untuk strategi scalping PEPE/IDR di Indodax dengan analisis teknikal dan AI prediction.

## 🚀 Fitur

### 📊 Indikator Teknikal

- **RSI (Relative Strength Index)** - Deteksi oversold/overbought
- **Moving Average Crossover** - SMA 5 & 20, EMA 12 & 26
- **MACD** - Momentum dan trend analysis
- **Bollinger Bands** - Support/resistance levels
- **Volume Analysis** - Konfirmasi sinyal dengan volume

### 🤖 AI Prediction

- **Random Forest Model** - Prediksi harga berdasarkan indikator teknikal
- **Real-time Learning** - Model terus belajar dari data baru
- **Price Prediction** - Estimasi harga berikutnya dengan persentase perubahan

### 📈 Sinyal Trading

- **🟢 BUY Signal** - Saat kondisi bullish terdeteksi
- **🔴 SELL Signal** - Saat kondisi bearish terdeteksi
- **⚪ HOLD Signal** - Saat tidak ada sinyal jelas

## 📋 Strategi Scalping

### Kapan Beli (BUY):

1. **RSI < 30** (oversold)
2. **MA Crossover** - SMA 5 menembus SMA 20 ke atas
3. **MACD Crossover** - MACD menembus Signal Line ke atas
4. **Bollinger Bands** - Harga menyentuh lower band
5. **Volume Confirmation** - Volume tinggi (>0.5x rata-rata)

### Kapan Jual (SELL):

1. **RSI > 70** (overbought)
2. **MA Crossover** - SMA 5 menembus SMA 20 ke bawah
3. **MACD Crossover** - MACD menembus Signal Line ke bawah
4. **Bollinger Bands** - Harga menyentuh upper band
5. **Volume Confirmation** - Volume tinggi untuk konfirmasi

### Risk Management:

- **Stop Loss**: 2-3% dari harga beli
- **Take Profit**: 1-2% profit per trade
- **Position Size**: Maksimal 10% dari modal per trade
- **Time Frame**: 5-15 menit per trade

## 🛠️ Instalasi

1. **Clone repository**

```bash
git clone <repository-url>
cd indodax
```

2. **Install dependencies**

```bash
# Aktifkan virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Jalankan bot**

```bash
# Cara mudah dengan script
./run_bot.sh

# Atau manual dengan virtual environment
source venv/bin/activate

# Versi lengkap dengan AI
python scalping_strategy.py

# Versi sederhana dengan persistent data
python persistent_strategy.py

# Versi basic
python simple_strategy.py
```

4. **Lihat data historis**

```bash
source venv/bin/activate
python view_data.py
```

## 📊 Cara Kerja

### 1. Data Collection

- Mengambil data real-time dari API Indodax
- Menyimpan data historis 24 jam terakhir
- Update setiap 5 detik

### 2. Technical Analysis

- Menghitung semua indikator teknikal
- Generate sinyal berdasarkan kombinasi indikator
- Filter sinyal dengan volume confirmation

### 3. AI Prediction

- Training model dengan data historis
- Prediksi harga berikutnya
- Menampilkan persentase perubahan yang diharapkan

### 4. Signal Generation

- Kombinasi analisis teknikal + AI
- Hanya tampilkan sinyal ketika ada perubahan
- Indikator visual untuk monitoring

### 5. Data Persistence

- Data historis disimpan ke file JSON
- Tidak hilang ketika bot dihentikan
- Dapat diload kembali saat restart
- Backup otomatis setiap 10 update

## ⚠️ Disclaimer

**PERINGATAN RISIKO:**

- Trading kripto memiliki risiko tinggi
- Bot ini hanya untuk edukasi dan analisis
- Selalu lakukan research sendiri sebelum trading
- Jangan investasi lebih dari yang bisa Anda rugi
- Pastikan memahami strategi sebelum menggunakan

## 🔧 Customization

### Mengubah Parameter:

```python
# RSI Settings
rsi_oversold = 30  # Default: 30
rsi_overbought = 70  # Default: 70

# Moving Average Settings
sma_short = 5  # Default: 5
sma_long = 20  # Default: 20

# Volume Threshold
volume_threshold = 0.5  # Default: 0.5
```

### Menambah Indikator:

```python
# Stochastic RSI
df['stoch_rsi'] = ta.momentum.StochRSIIndicator(df['price']).stochrsi()

# Williams %R
df['williams_r'] = ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['price']).williams_r()
```

## 📈 Performance Tracking

Bot akan menampilkan:

- Harga real-time PEPE/IDR
- Sinyal trading dengan alasan
- AI prediction dengan persentase
- Indikator teknikal terkini

## 🤝 Contributing

1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Buat Pull Request

## 📞 Support

Jika ada pertanyaan atau masalah:

- Buat issue di GitHub
- Email: [your-email@domain.com]
- Telegram: [@your-username]

---

**Happy Trading! 🚀📈**
