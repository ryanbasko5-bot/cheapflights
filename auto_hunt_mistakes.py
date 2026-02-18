"""
Automated Mistake Fare Hunter - Runs continuously

Scans every 2 hours for pricing errors and creates alerts
"""
import schedule
import time
import subprocess
from datetime import datetime

print("="*80)
print("🤖 AUTOMATED MISTAKE FARE HUNTER")
print("="*80)
print("\nThis will run the mistake fare scanner every 2 hours")
print("Press Ctrl+C to stop\n")

def run_mistake_fare_hunt():
    """Execute the mistake fare hunter"""
    print(f"\n{'='*80}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting hunt...")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            ['python', 'hunt_mistake_fares.py'],
            capture_output=True,
            text=True,
            cwd='/workspaces/cheapflights'
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("✅ Hunt completed successfully")
        else:
            print(f"❌ Hunt failed with error code {result.returncode}")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running hunt: {e}")
    
    print(f"\n⏰ Next hunt in 2 hours at {datetime.now().replace(hour=(datetime.now().hour + 2) % 24).strftime('%H:%M')}")

# Schedule the hunt every 2 hours
schedule.every(2).hours.do(run_mistake_fare_hunt)

# Run immediately on startup
print("🚀 Running initial hunt...")
run_mistake_fare_hunt()

# Keep running
print("\n" + "="*80)
print("🔄 Automated hunting active - scanning every 2 hours")
print("Press Ctrl+C to stop")
print("="*80 + "\n")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
