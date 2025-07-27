# === Konfigurasi Trading Pairs ===
# Anda bisa mengubah enabled menjadi False untuk menonaktifkan pair tertentu
TRADING_PAIRS = [
    {
        'name': 'ETH',
        'pair': 'eth_idr',
        'display_name': 'ETH/IDR',
        'emoji': '🔷',
        'enabled': False
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
        'enabled': False
    },
    {
        'name': 'ENA',
        'pair': 'ena_idr',
        'display_name': 'ENA/IDR',
        'emoji': '🌊',
        'enabled': False
    },
    {
        'name': 'FARTCOIN',
        'pair': 'fartcoin_idr',
        'display_name': 'FARTCOIN/IDR',
        'emoji': '💨',
        'enabled': False
    },
    {
        'name': 'PENGU',
        'pair': 'pengu_idr',
        'display_name': 'PENGU/IDR',
        'emoji': '🐧',
        'enabled': False
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
        'enabled': False
    },
    {
        'name': 'MOODENG',
        'pair': 'moodeng_idr',
        'display_name': 'MOODENG/IDR',
        'emoji': '🐮',
        'enabled': False
    },
    {
        'name': 'ZORA',
        'pair': 'zora_idr',
        'display_name': 'ZORA/IDR',
        'emoji': '🎨',
        'enabled': False
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
        'enabled': False
    },
    {
        'name': 'ADA',
        'pair': 'ada_idr',
        'display_name': 'ADA/IDR',
        'emoji': '🔷',
        'enabled': False
    },
    {
        'name': 'MOONPIG',
        'pair': 'moonpig_idr',
        'display_name': 'MOONPIG/IDR',
        'emoji': '🐷',
        'enabled': False
    }
]

# === Konfigurasi Telegram ===
# Isi dengan token dan chat_id Telegram Anda
# Anda bisa menggunakan environment variables atau langsung isi di sini
import os
# ===============================================
# TELEGRAM CONFIGURATION
# ===============================================

# Telegram Bot Token (dari @BotFather)
TELEGRAM_TOKEN = '8430603365:AAEtZf6AjhsbQuaHnec5EJwmi-pzGfXITWs'

# Telegram Chat ID (dari bot atau @userinfobot)
TELEGRAM_CHAT_ID = '1433257992'

# Kirim semua signal atau hanya BUY/SELL/EXIT
SEND_ALL_SIGNALS = False  # Kirim semua jenis signal
SEND_HOLD_SIGNALS = False  # Jangan kirim signal HOLD

# Mode test Telegram (kirim pesan test saat startup)
TELEGRAM_TEST_MODE = True

# === Konfigurasi Risk Management ===
STOP_LOSS_PERCENT = 0.053    # 5.3% stop loss
TAKE_PROFIT_PERCENT = 0.02   # 2% take profit (reduced from 5.5%)
MAX_HOLD_TIME = 120          # 120 menit max holding time
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

# ===============================================
# SCALPING MODE CONFIGURATION  
# ===============================================

# Enable scalping mode (more aggressive, faster signals)
SCALPING_MODE = True

# Scalping RSI thresholds (more aggressive)
SCALPING_RSI_3_OVERSOLD = 25    # Reduced from 20 for more entries
SCALPING_RSI_3_OVERBOUGHT = 75  # Reduced from 80 for more entries

# Scalping momentum thresholds
SCALPING_MOMENTUM_ROC3_THRESHOLD = 0.8  # Reduced from 1.2% for more sensitivity

# Scalping volatility thresholds  
SCALPING_VOLATILITY_CV_LOW = 1.0   # Increased from 0.5% 
SCALPING_VOLATILITY_CV_HIGH = 3.0  # Increased from 2.0%

# Scalping signal strength (more aggressive)
SCALPING_MIN_SIGNAL_STRENGTH = 2  # Reduced from 4 for more signals

# Scalping cooldown (faster signals)
SCALPING_COOLDOWN = 30  # Reduced from 60 seconds

# Volume threshold for scalping (more lenient)
VOLUME_THRESHOLD = 0.7  # Reduced from 1.0

# Volatility threshold for scalping (more tolerant)
VOLATILITY_THRESHOLD = 0.025  # Increased from 0.02 (2.5%)

# Add proxy configuration at the end of the config file

# ===============================================
# BINANCE PROXY CONFIGURATION
# ===============================================

# Set to True if you need proxy to access Binance
USE_BINANCE_PROXY = False

# Proxy URL (format: 'http://username:password@proxy_host:port' or 'http://proxy_host:port')
# Examples:
# 'http://127.0.0.1:1080'  # SOCKS proxy
# 'http://proxy.example.com:8080'  # HTTP proxy
# 'http://user:pass@proxy.example.com:8080'  # Authenticated proxy
BINANCE_PROXY_URL = 'http://23673857ee9ee25b9423__cr:746b6cd758b190ee@gw.dataimpulse.com:823'

# Alternative proxy providers (uncomment if needed)
# Free proxy examples (not recommended for production):
# BINANCE_PROXY_URL = 'http://free-proxy.cz:8080'
# BINANCE_PROXY_URL = 'http://proxy-list.download:8080'

# Paid proxy examples:
# BINANCE_PROXY_URL = 'http://username:password@premium-proxy.com:1080'

# ===============================================
# BINANCE CONNECTION SETTINGS
# ===============================================

# Connection timeout for Binance API (seconds)
BINANCE_TIMEOUT = 10

# Retry attempts if Binance connection fails
BINANCE_RETRY_ATTEMPTS = 3

# Fallback mode (use direct requests instead of ccxt)
BINANCE_USE_FALLBACK_ONLY = False 