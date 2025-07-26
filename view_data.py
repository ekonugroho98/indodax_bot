import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

def load_historical_data(filename="pepe_historical_data.json"):
    """Load dan tampilkan data historis"""
    if not os.path.exists(filename):
        print(f"❌ File {filename} tidak ditemukan")
        return None
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Convert string timestamps back to datetime objects
        for item in data:
            item['timestamp'] = datetime.fromisoformat(item['timestamp'])
        
        return data
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def analyze_data(data):
    """Analisis data historis"""
    if not data:
        return
    
    print(f"\n📊 ANALISIS DATA HISTORIS PEPE/IDR")
    print("=" * 50)
    
    # Basic statistics
    prices = [item['price'] for item in data]
    volumes = [item['volume'] for item in data]
    timestamps = [item['timestamp'] for item in data]
    
    print(f"📈 Total data points: {len(data)}")
    print(f"📅 Periode: {timestamps[0].strftime('%Y-%m-%d %H:%M')} - {timestamps[-1].strftime('%Y-%m-%d %H:%M')}")
    print(f"⏱️  Durasi: {(timestamps[-1] - timestamps[0]).total_seconds() / 3600:.1f} jam")
    
    print(f"\n💰 STATISTIK HARGA:")
    print(f"   Tertinggi: Rp {max(prices):.6f}")
    print(f"   Terendah: Rp {min(prices):.6f}")
    print(f"   Rata-rata: Rp {np.mean(prices):.6f}")
    print(f"   Median: Rp {np.median(prices):.6f}")
    print(f"   Standar Deviasi: Rp {np.std(prices):.6f}")
    
    # Price change
    price_change = ((prices[-1] - prices[0]) / prices[0]) * 100
    print(f"   Perubahan total: {price_change:+.2f}%")
    
    print(f"\n📊 STATISTIK VOLUME:")
    print(f"   Volume tertinggi: {max(volumes):.2f}")
    print(f"   Volume terendah: {min(volumes):.2f}")
    print(f"   Volume rata-rata: {np.mean(volumes):.2f}")
    
    # Volatility analysis
    price_changes = np.diff(prices)
    volatility = np.std(price_changes)
    print(f"\n📈 VOLATILITAS:")
    print(f"   Volatilitas: {volatility:.6f}")
    print(f"   Perubahan terbesar: {max(abs(price_changes)):.6f}")
    print(f"   Perubahan rata-rata: {np.mean(abs(price_changes)):.6f}")
    
    # Find significant price movements
    significant_moves = []
    for i, change in enumerate(price_changes):
        if abs(change) > volatility * 2:  # 2x standard deviation
            significant_moves.append({
                'index': i,
                'change': change,
                'percentage': (change / prices[i]) * 100,
                'timestamp': timestamps[i+1]
            })
    
    if significant_moves:
        print(f"\n🚨 PERGERAKAN SIGNIFIKAN ({len(significant_moves)} kejadian):")
        for move in significant_moves[-5:]:  # Show last 5
            direction = "📈" if move['change'] > 0 else "📉"
            print(f"   {direction} {move['timestamp'].strftime('%H:%M:%S')}: {move['percentage']:+.2f}% (Rp {move['change']:+.6f})")

def plot_data(data):
    """Plot data historis"""
    if not data:
        return
    
    prices = [item['price'] for item in data]
    volumes = [item['volume'] for item in data]
    timestamps = [item['timestamp'] for item in data]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Price chart
    ax1.plot(timestamps, prices, 'b-', linewidth=1)
    ax1.set_title('PEPE/IDR Price History', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price (IDR)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Volume chart
    ax2.bar(timestamps, volumes, alpha=0.6, color='green')
    ax2.set_title('Trading Volume', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.set_xlabel('Time', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Rotate x-axis labels
    plt.setp(ax1.get_xticklabels(), rotation=45)
    plt.setp(ax2.get_xticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.show()

def export_to_csv(data, filename="pepe_data.csv"):
    """Export data ke CSV"""
    if not data:
        return
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"💾 Data berhasil di-export ke {filename}")

def main():
    """Main function"""
    print("🔍 PEPE Historical Data Viewer")
    print("=" * 30)
    
    # Load data
    data = load_historical_data()
    if not data:
        return
    
    while True:
        print(f"\n📋 MENU:")
        print("1. 📊 Tampilkan analisis")
        print("2. 📈 Plot grafik")
        print("3. 💾 Export ke CSV")
        print("4. 🔍 Cari data spesifik")
        print("5. ❌ Keluar")
        
        choice = input("\nPilih menu (1-5): ").strip()
        
        if choice == "1":
            analyze_data(data)
        elif choice == "2":
            plot_data(data)
        elif choice == "3":
            export_to_csv(data)
        elif choice == "4":
            search_data(data)
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Pilihan tidak valid!")

def search_data(data):
    """Search data berdasarkan kriteria"""
    if not data:
        return
    
    print(f"\n🔍 CARI DATA:")
    print("1. Cari berdasarkan tanggal")
    print("2. Cari berdasarkan range harga")
    print("3. Cari berdasarkan volume tinggi")
    
    choice = input("Pilih jenis pencarian (1-3): ").strip()
    
    if choice == "1":
        date_str = input("Masukkan tanggal (YYYY-MM-DD): ").strip()
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            filtered_data = [item for item in data if item['timestamp'].date() == target_date]
            print(f"📅 Ditemukan {len(filtered_data)} data points pada {date_str}")
            if filtered_data:
                prices = [item['price'] for item in filtered_data]
                print(f"   Harga: Rp {min(prices):.6f} - Rp {max(prices):.6f}")
        except ValueError:
            print("❌ Format tanggal tidak valid!")
    
    elif choice == "2":
        try:
            min_price = float(input("Harga minimum: "))
            max_price = float(input("Harga maksimum: "))
            filtered_data = [item for item in data if min_price <= item['price'] <= max_price]
            print(f"💰 Ditemukan {len(filtered_data)} data points dalam range Rp {min_price:.6f} - Rp {max_price:.6f}")
        except ValueError:
            print("❌ Input harga tidak valid!")
    
    elif choice == "3":
        try:
            threshold = float(input("Volume threshold: "))
            filtered_data = [item for item in data if item['volume'] >= threshold]
            print(f"📊 Ditemukan {len(filtered_data)} data points dengan volume >= {threshold}")
        except ValueError:
            print("❌ Input volume tidak valid!")

if __name__ == "__main__":
    main() 