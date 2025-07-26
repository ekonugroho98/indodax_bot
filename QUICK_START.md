# 🚀 Quick Start Guide - PEPE Trading Bot

## ⚡ Langkah Cepat (5 Menit)

### 1. Setup Awal

```bash
# Clone atau download project
cd indodax

# Aktifkan virtual environment
source venv/bin/activate

# Install dependencies (sudah terinstall)
pip install -r requirements.txt
```

### 2. Jalankan Bot

```bash
# Cara termudah
./run_bot.sh

# Pilih opsi 1 untuk bot dengan data persistence
```

### 3. Monitor Trading

- Bot akan menampilkan harga real-time PEPE/IDR
- Sinyal BUY/SELL akan muncul otomatis
- Data tersimpan di `pepe_historical_data.json`

### 4. Lihat Data Historis

```bash
# Di terminal baru
source venv/bin/activate
python view_data.py
```

## 📊 Fitur Utama

### ✅ Data Persistence

- Data tidak hilang saat bot dihentikan
- Auto-save setiap 10 update
- Load otomatis saat restart

### ✅ Technical Analysis

- RSI (Relative Strength Index)
- Moving Average Crossover
- Volume Analysis
- Bollinger Bands

### ✅ AI Prediction

- Random Forest Model
- Prediksi harga berikutnya
- Persentase perubahan

### ✅ Signal Generation

- BUY Signal (🟢)
- SELL Signal (🔴)
- HOLD Signal (⚪)

## 🎯 Strategi Scalping

### Kapan BELI:

- RSI < 30 (oversold)
- MA Crossover bullish
- Volume tinggi
- Harga di support level

### Kapan JUAL:

- RSI > 70 (overbought)
- MA Crossover bearish
- Volume tinggi
- Harga di resistance level

## ⚠️ Risk Management

- **Stop Loss**: 2-3% dari harga beli
- **Take Profit**: 1-2% profit per trade
- **Position Size**: Maksimal 10% modal
- **Time Frame**: 5-15 menit per trade

## 🔧 Troubleshooting

### Error "No module named 'pandas'"

```bash
source venv/bin/activate
pip install pandas numpy matplotlib seaborn ta scikit-learn
```

### Bot tidak bisa dihentikan

- Tekan `Ctrl+C` untuk stop
- Data akan otomatis tersimpan

### File data tidak ditemukan

- Jalankan bot dulu untuk mengumpulkan data
- File akan dibuat otomatis

## 📞 Support

Jika ada masalah:

1. Pastikan virtual environment aktif
2. Check semua dependencies terinstall
3. Restart terminal jika perlu

---

**Happy Trading! 🚀📈**
