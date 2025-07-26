import json
import os
from datetime import datetime
import numpy as np

def analyze_storage_efficiency(filename="pepe_historical_data.json"):
    """Analyze storage efficiency of the data"""
    if not os.path.exists(filename):
        print(f"❌ File {filename} tidak ditemukan")
        return
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Convert string timestamps back to datetime objects
        for item in data:
            item['timestamp'] = datetime.fromisoformat(item['timestamp'])
        
        print(f"📊 ANALISIS STORAGE EFFICIENCY")
        print("=" * 50)
        
        # Basic stats
        total_points = len(data)
        if total_points == 0:
            print("❌ Tidak ada data untuk dianalisis")
            return
        
        # Time analysis
        start_time = data[0]['timestamp']
        end_time = data[-1]['timestamp']
        duration = (end_time - start_time).total_seconds() / 3600  # hours
        
        # Calculate theoretical data points (every 5 seconds)
        theoretical_points = int(duration * 3600 / 5)
        
        # Calculate storage efficiency
        efficiency = (total_points / theoretical_points) * 100 if theoretical_points > 0 else 0
        
        # Price change analysis
        prices = [item['price'] for item in data]
        price_changes = []
        for i in range(1, len(prices)):
            change = abs(prices[i] - prices[i-1])
            change_percent = (change / prices[i-1]) * 100
            price_changes.append(change_percent)
        
        # Volume change analysis
        volumes = [item['volume'] for item in data]
        volume_changes = []
        for i in range(1, len(volumes)):
            change = abs(volumes[i] - volumes[i-1])
            change_percent = (change / volumes[i-1]) * 100 if volumes[i-1] > 0 else 0
            volume_changes.append(change_percent)
        
        print(f"📈 STATISTIK DATA:")
        print(f"   Total data points: {total_points}")
        print(f"   Periode: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Durasi: {duration:.1f} jam")
        print(f"   Theoretical points (5s interval): {theoretical_points}")
        
        print(f"\n💾 STORAGE EFFICIENCY:")
        print(f"   Efficiency: {efficiency:.1f}%")
        print(f"   Data saved: {total_points} / {theoretical_points}")
        print(f"   Storage saved: {theoretical_points - total_points} points")
        
        if efficiency < 50:
            print(f"   ✅ Excellent! Smart saving working well")
        elif efficiency < 80:
            print(f"   ⚠️  Good efficiency, market is active")
        else:
            print(f"   📊 High data density, market is volatile")
        
        print(f"\n📊 CHANGE ANALYSIS:")
        if price_changes:
            avg_price_change = np.mean(price_changes)
            max_price_change = max(price_changes)
            print(f"   Average price change: {avg_price_change:.4f}%")
            print(f"   Max price change: {max_price_change:.4f}%")
            print(f"   Significant changes: {sum(1 for x in price_changes if x > 0.01)}")
        
        if volume_changes:
            avg_volume_change = np.mean(volume_changes)
            max_volume_change = max(volume_changes)
            print(f"   Average volume change: {avg_volume_change:.2f}%")
            print(f"   Max volume change: {max_volume_change:.2f}%")
        
        # Show data points with significant changes
        print(f"\n🚨 SIGNIFICANT CHANGES (last 10):")
        significant_changes = []
        for i in range(1, len(data)):
            price_change = abs(data[i]['price'] - data[i-1]['price'])
            price_change_percent = (price_change / data[i-1]['price']) * 100
            
            volume_change = abs(data[i]['volume'] - data[i-1]['volume'])
            volume_change_percent = (volume_change / data[i-1]['volume']) * 100 if data[i-1]['volume'] > 0 else 0
            
            if price_change_percent > 0.01 or volume_change_percent > 1:
                significant_changes.append({
                    'timestamp': data[i]['timestamp'],
                    'price_change': price_change_percent,
                    'volume_change': volume_change_percent,
                    'price': data[i]['price']
                })
        
        for change in significant_changes[-10:]:
            direction = "📈" if change['price_change'] > 0 else "📉"
            print(f"   {direction} {change['timestamp'].strftime('%H:%M:%S')}: "
                  f"Price {change['price_change']:+.3f}%, "
                  f"Volume {change['volume_change']:+.1f}%, "
                  f"Rp {change['price']:.6f}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if efficiency < 30:
            print(f"   ✅ Perfect! Smart saving sangat efektif")
            print(f"   💡 Market relatif stabil, data tersimpan optimal")
        elif efficiency < 60:
            print(f"   ⚠️  Good efficiency, market cukup aktif")
            print(f"   💡 Pertimbangkan menaikkan threshold untuk lebih efisien")
        else:
            print(f"   📊 Market sangat volatile, banyak perubahan")
            print(f"   💡 Data density tinggi, pertimbangkan menurunkan threshold")
        
        # File size analysis
        file_size = os.path.getsize(filename)
        file_size_kb = file_size / 1024
        print(f"\n📁 FILE SIZE:")
        print(f"   Size: {file_size_kb:.1f} KB")
        print(f"   Size per data point: {file_size_kb/total_points:.2f} KB")
        
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")

def compare_with_regular_saving():
    """Compare smart saving with regular saving"""
    print(f"\n🔄 COMPARISON: Smart vs Regular Saving")
    print("=" * 50)
    
    if not os.path.exists("pepe_historical_data.json"):
        print("❌ No data file found for comparison")
        return
    
    # Analyze current smart saving
    with open("pepe_historical_data.json", 'r') as f:
        data = json.load(f)
    
    smart_points = len(data)
    
    # Calculate theoretical regular saving points
    if len(data) > 1:
        start_time = datetime.fromisoformat(data[0]['timestamp'])
        end_time = datetime.fromisoformat(data[-1]['timestamp'])
        duration = (end_time - start_time).total_seconds() / 3600  # hours
        regular_points = int(duration * 3600 / 5)  # every 5 seconds
    else:
        regular_points = 0
    
    print(f"📊 COMPARISON RESULTS:")
    print(f"   Smart saving points: {smart_points}")
    print(f"   Regular saving points: {regular_points}")
    print(f"   Points saved: {regular_points - smart_points}")
    print(f"   Storage reduction: {((regular_points - smart_points) / regular_points * 100):.1f}%" if regular_points > 0 else "N/A")
    
    # Estimate file size savings
    avg_point_size = 200  # bytes per data point
    smart_size = smart_points * avg_point_size
    regular_size = regular_points * avg_point_size
    size_saved = regular_size - smart_size
    
    print(f"\n💾 STORAGE SAVINGS:")
    print(f"   Smart saving size: {smart_size/1024:.1f} KB")
    print(f"   Regular saving size: {regular_size/1024:.1f} KB")
    print(f"   Size saved: {size_saved/1024:.1f} KB")
    print(f"   Size reduction: {(size_saved/regular_size*100):.1f}%" if regular_size > 0 else "N/A")

def main():
    """Main function"""
    print("🔍 Storage Efficiency Analyzer")
    print("=" * 30)
    
    # Analyze current data
    analyze_storage_efficiency()
    
    # Compare with regular saving
    compare_with_regular_saving()
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 