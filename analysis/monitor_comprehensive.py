#!/usr/bin/env python3
"""
Monitor the comprehensive market scraper progress.
"""

import time
import pandas as pd
import glob
import os
from datetime import datetime

def monitor_comprehensive_scraper():
    """Monitor comprehensive scraper progress"""
    
    print("🔍 COMPREHENSIVE MARKET SCRAPER MONITOR")
    print("=" * 60)
    
    while True:
        # Check for latest comprehensive data file
        csv_files = glob.glob("comprehensive_market_ownership_*.csv")
        
        if csv_files:
            latest_file = max(csv_files, key=os.path.getctime)
            
            try:
                df = pd.read_csv(latest_file)
                
                print(f"\n📊 COMPREHENSIVE PROGRESS ({datetime.now().strftime('%H:%M:%S')})")
                print(f"📁 Data file: {latest_file}")
                print(f"📈 Total ownership records: {len(df)}")
                print(f"🏢 Companies processed: {df['ticker'].nunique()}")
                print(f"🏛️  Institutional holders found: {df['holder_name'].nunique()}")
                
                if len(df) > 0:
                    # Show institutional dominance
                    holder_counts = df['holder_name'].value_counts()
                    total_companies = df['ticker'].nunique()
                    
                    print(f"\n🏆 INSTITUTIONAL MARKET DOMINANCE:")
                    for holder, count in holder_counts.head(8).items():
                        percentage = (count / total_companies) * 100
                        print(f"   {holder}: {count}/{total_companies} companies ({percentage:.1f}%)")
                    
                    # Show recent companies processed
                    recent_companies = df.drop_duplicates('ticker').tail(5)
                    print(f"\n🔥 Recently processed companies:")
                    for _, row in recent_companies.iterrows():
                        company_holders = df[df['ticker'] == row['ticker']]['holder_name'].count()
                        print(f"   {row['ticker']} ({row['company_name']}): {company_holders} institutional holders")
                    
                    # Market concentration insights
                    vanguard_presence = holder_counts.get('Vanguard Group', 0)
                    blackrock_presence = holder_counts.get('BlackRock', 0)
                    combined_presence = len(df[df['holder_name'].isin(['Vanguard Group', 'BlackRock'])]['ticker'].unique())
                    
                    print(f"\n🎯 BIG 2 DOMINANCE ANALYSIS:")
                    print(f"   Vanguard presence: {vanguard_presence} companies")
                    print(f"   BlackRock presence: {blackrock_presence} companies")
                    print(f"   Combined Vanguard+BlackRock: {combined_presence} companies")
                    
                    if total_companies > 0:
                        print(f"   Market dominance: {combined_presence/total_companies*100:.1f}%")
                
            except Exception as e:
                print(f"⚠️  Error reading comprehensive data: {e}")
        else:
            print(f"⏳ Waiting for comprehensive data file to be created...")
        
        print(f"\n{'='*60}")
        print("Monitoring comprehensive market scraper... Press Ctrl+C to stop")
        
        try:
            time.sleep(45)  # Check every 45 seconds for comprehensive run
        except KeyboardInterrupt:
            print(f"\n👋 Comprehensive monitoring stopped")
            break

if __name__ == "__main__":
    monitor_comprehensive_scraper()
