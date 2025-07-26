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
MAX_DATA_POINTS = 1000  # Maksimal data points per pair
MIN_DATA_POINTS = 30  # Minimal data points untuk generate signal 