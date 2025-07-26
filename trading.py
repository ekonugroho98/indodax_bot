import requests
import time

# Endpoint API Public Indodax
url = "https://indodax.com/api/pepe_idr/ticker"

# Variabel untuk menyimpan data sebelumnya
previous_data = None

def get_pepe_price():
    global previous_data
    try:
        response = requests.get(url)
        data = response.json()
        ticker = data['ticker']
        current_data = {
            'last': float(ticker['last']),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'volume': float(ticker['vol_pepe'])
        }
        
        # Cek apakah data berubah
        if previous_data != current_data:
            print(f"\n📈 Harga PEPE/IDR Sekarang: Rp {current_data['last']}")
            print(f"🔺 Tertinggi: Rp {current_data['high']}")
            print(f"🔻 Terendah: Rp {current_data['low']}")
            print(f"📊 Volume (24 jam): {current_data['volume']:.2f} PEPE")
            
            # Update data sebelumnya
            previous_data = current_data
        else:
            print(".", end="", flush=True)  # Indikator bahwa program masih berjalan
        
    except Exception as e:
        print("Gagal mengambil data:", e)

# Loop setiap 10 detik
while True:
    get_pepe_price()
    time.sleep(1)
