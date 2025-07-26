#!/usr/bin/env python3
"""
🧪 Telegram Test Script
Test koneksi Telegram tanpa menjalankan bot lengkap
"""

import requests
import os
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def test_telegram_connection():
    """Test koneksi Telegram"""
    print("🧪 Testing Telegram Connection...")
    print("=" * 50)
    
    # Check configuration
    print(f"📱 Token: {TELEGRAM_TOKEN[:10]}..." if len(TELEGRAM_TOKEN) > 10 else f"📱 Token: {TELEGRAM_TOKEN}")
    print(f"💬 Chat ID: {TELEGRAM_CHAT_ID}")
    
    if TELEGRAM_TOKEN == 'ISI_TOKEN_TELEGRAM_KAMU' or TELEGRAM_CHAT_ID == 'ISI_CHAT_ID_KAMU':
        print("\n❌ ERROR: Telegram belum dikonfigurasi!")
        print("\n📝 Cara setup Telegram:")
        print("   1. Buat bot di @BotFather di Telegram")
        print("   2. Dapatkan token bot")
        print("   3. Dapatkan chat_id (kirim /start ke bot)")
        print("   4. Edit config.py atau set environment variables:")
        print("      TELEGRAM_TOKEN=your_bot_token")
        print("      TELEGRAM_CHAT_ID=your_chat_id")
        return False
    
    # Test message
    test_message = f"""
🧪 <b>TELEGRAM CONNECTION TEST</b> 🧪

✅ Bot berhasil terhubung ke Telegram!
📱 Koneksi berfungsi dengan baik

⏰ <b>Test Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 <b>Configuration:</b>
• Token: {TELEGRAM_TOKEN[:10]}...
• Chat ID: {TELEGRAM_CHAT_ID}

🤖 <b>Status:</b> Connection OK

---
<i>Test message untuk verifikasi koneksi Telegram</i>
    """
    
    # Send test message
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': test_message,
        'parse_mode': 'HTML'
    }
    
    try:
        print("\n📤 Sending test message...")
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ SUCCESS: Telegram test message sent!")
                print(f"📨 Message ID: {result['result']['message_id']}")
                print(f"💬 Chat: {result['result']['chat']['title'] if 'title' in result['result']['chat'] else 'Private Chat'}")
                return True
            else:
                print(f"❌ ERROR: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT: Koneksi lambat")
        return False
    except requests.exceptions.ConnectionError:
        print("🌐 CONNECTION ERROR: Cek koneksi internet")
        return False
    except Exception as e:
        print(f"❌ UNKNOWN ERROR: {e}")
        return False

def send_custom_message(message):
    """Kirim pesan custom ke Telegram"""
    if TELEGRAM_TOKEN == 'ISI_TOKEN_TELEGRAM_KAMU' or TELEGRAM_CHAT_ID == 'ISI_CHAT_ID_KAMU':
        print("❌ Telegram belum dikonfigurasi!")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Custom message sent successfully!")
                return True
            else:
                print(f"❌ Error: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Telegram Test Script")
    print("=" * 50)
    
    # Test connection
    success = test_telegram_connection()
    
    if success:
        print("\n🎉 Telegram test berhasil!")
        print("Bot siap untuk mengirim notifikasi")
        
        # Ask for custom message
        print("\n💬 Kirim pesan custom? (y/n): ", end="")
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes', 'ya']:
                print("📝 Masukkan pesan: ", end="")
                custom_msg = input()
                if custom_msg:
                    send_custom_message(custom_msg)
        except KeyboardInterrupt:
            print("\n👋 Test selesai")
    else:
        print("\n❌ Telegram test gagal!")
        print("Periksa konfigurasi dan coba lagi")
    
    print("\n👋 Test selesai!") 