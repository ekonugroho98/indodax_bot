# === Konfigurasi Trading Pairs ===
# Anda bisa mengubah enabled menjadi False untuk menonaktifkan pair tertentu
TRADING_PAIRS = [
    {
        'name': 'ETH',
        'pair': 'eth_idr',
        'display_name': 'ETH/IDR',
        'emoji': '🔷',
        'enabled': True
    },
    {
        'name': 'BTC',
        'pair': 'btc_idr',
        'display_name': 'BTC/IDR',
        'emoji': '₿',
        'enabled': True
    },
    {
        'name': 'XRP',
        'pair': 'xrp_idr',
        'display_name': 'XRP/IDR',
        'emoji': '⚡',
        'enabled': True
    },
    {
        'name': 'ALPACA',
        'pair': 'alpaca_idr',
        'display_name': 'ALPACA/IDR',
        'emoji': '🦙',
        'enabled': True
    },
    {
        'name': 'ENA',
        'pair': 'ena_idr',
        'display_name': 'ENA/IDR',
        'emoji': '🌊',
        'enabled': True
    },
    {
        'name': 'FARTCOIN',
        'pair': 'fartcoin_idr',
        'display_name': 'FARTCOIN/IDR',
        'emoji': '💨',
        'enabled': True
    },
    {
        'name': 'PENGU',
        'pair': 'pengu_idr',
        'display_name': 'PENGU/IDR',
        'emoji': '🐧',
        'enabled': True
    },
    {
        'name': 'SOL',
        'pair': 'sol_idr',
        'display_name': 'SOL/IDR',
        'emoji': '☀️',
        'enabled': True
    },
    {
        'name': 'DOGE',
        'pair': 'doge_idr',
        'display_name': 'DOGE/IDR',
        'emoji': '🐕',
        'enabled': True
    },
    {
        'name': 'PEPE',
        'pair': 'pepe_idr',
        'display_name': 'PEPE/IDR',
        'emoji': '🐸',
        'enabled': True
    },
    {
        'name': 'HBAR',
        'pair': 'hbar_idr',
        'display_name': 'HBAR/IDR',
        'emoji': '🌳',
        'enabled': True
    },
    {
        'name': 'MOODENG',
        'pair': 'moodeng_idr',
        'display_name': 'MOODENG/IDR',
        'emoji': '🐮',
        'enabled': True
    },
    {
        'name': 'ZORA',
        'pair': 'zora_idr',
        'display_name': 'ZORA/IDR',
        'emoji': '🎨',
        'enabled': True
    },
    {
        'name': 'SUI',
        'pair': 'sui_idr',
        'display_name': 'SUI/IDR',
        'emoji': '💧',
        'enabled': True
    },
    {
        'name': 'SPX',
        'pair': 'spx_idr',
        'display_name': 'SPX/IDR',
        'emoji': '🚀',
        'enabled': True
    },
    {
        'name': 'ADA',
        'pair': 'ada_idr',
        'display_name': 'ADA/IDR',
        'emoji': '🔷',
        'enabled': True
    },
    {
        'name': 'MOONPIG',
        'pair': 'moonpig_idr',
        'display_name': 'MOONPIG/IDR',
        'emoji': '🐷',
        'enabled': True
    }
]

# === Konfigurasi Telegram ===
# Isi dengan token dan chat_id Telegram Anda
# Anda bisa menggunakan environment variables atau langsung isi di sini
import os
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'ISI_TOKEN_TELEGRAM_KAMU')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'ISI_CHAT_ID_KAMU')

# === Konfigurasi Risk Management ===
STOP_LOSS_PERCENT = 0.02  # 2% stop loss
TAKE_PROFIT_PERCENT = 0.015  # 1.5% take profit
MAX_HOLD_TIME = 1800  # 30 menit maksimal hold
SIGNAL_COOLDOWN = 120  # 2 menit cooldown

# === Konfigurasi Signal Strength ===
MIN_SIGNAL_STRENGTH = 3  # Minimal strength untuk generate signal
VOLUME_THRESHOLD = 0.8  # Volume minimal 0.8x rata-rata
VOLATILITY_THRESHOLD = 0.02  # 2% volatility threshold

# === Konfigurasi Data Management ===
# Data Management Tiers untuk berbagai jenis analisis
DATA_MANAGEMENT_TIERS = {
    'scalping': {
        'max_points': 2000,      # 2-3 jam data untuk scalping real-time
        'min_points': 100,       # Minimal untuk scalping
        'interval': 5,           # 5 detik interval
        'purpose': 'Real-time scalping signals'
    },
    'swing': {
        'max_points': 10000,     # 1-2 hari data untuk swing trading
        'min_points': 500,       # Minimal untuk swing analysis
        'interval': 30,          # 30 detik interval
        'purpose': 'Swing trading patterns'
    },
    'position': {
        'max_points': 50000,     # 1-2 minggu data untuk position trading
        'min_points': 2000,      # Minimal untuk position analysis
        'interval': 300,         # 5 menit interval
        'purpose': 'Long-term position analysis'
    }
}

# Default settings (backward compatibility)
MAX_DATA_POINTS = 10000  # Increased from 1000 to 10000
MIN_DATA_POINTS = 100    # Increased from 30 to 100

# Data Storage Optimization
ENABLE_DATA_COMPRESSION = True   # Compress old data
ENABLE_DATA_ARCHIVING = True     # Archive data older than 1 week
ARCHIVE_INTERVAL_HOURS = 168     # Archive after 1 week (168 hours)

# Performance Settings
ENABLE_LAZY_LOADING = True       # Load data on demand
ENABLE_DATA_CACHING = True       # Cache frequently used data
CACHE_SIZE_MB = 50               # 50MB cache size

# === Konfigurasi Scalping-Specific ===
SCALPING_MODE = True  # Enable scalping optimizations
SCALPING_RSI_3_OVERSOLD = 20  # RSI 3-period oversold threshold
SCALPING_RSI_3_OVERBOUGHT = 80  # RSI 3-period overbought threshold
SCALPING_MOMENTUM_ROC3_THRESHOLD = 1.0  # ROC 3-period threshold
SCALPING_VOLATILITY_CV_LOW = 1.0  # Low volatility threshold
SCALPING_VOLATILITY_CV_HIGH = 3.0  # High volatility threshold
SCALPING_MIN_SIGNAL_STRENGTH = 4  # Higher threshold for scalping
SCALPING_COOLDOWN = 60  # Shorter cooldown for scalping (1 minute) 