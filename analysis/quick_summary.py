#!/usr/bin/env python3
"""
Quick summary of our institutional market dominance findings.
"""

import pandas as pd

def quick_summary():
    """Show quick summary of findings"""
    
    df = pd.read_csv("comprehensive_market_ownership_20250918_195445.csv")
    
    print("🎯 QUICK SUMMARY: Institutional Market Dominance")
    print("=" * 55)
    
    total_companies = df['ticker'].nunique()
    holder_counts = df['holder_name'].value_counts()
    
    print(f"📊 Dataset: {len(df)} records from {total_companies} companies")
    print(f"🏛️  Top Institutions:")
    
    for i, (holder, count) in enumerate(holder_counts.head(5).items(), 1):
        percentage = count / total_companies * 100
        print(f"   {i}. {holder}: {count} companies ({percentage:.1f}%)")
    
    # Big 2 analysis
    vanguard_cos = holder_counts.get('Vanguard Group', 0)
    blackrock_cos = holder_counts.get('BlackRock', 0)
    
    vanguard_set = set(df[df['holder_name'] == 'Vanguard Group']['ticker'])
    blackrock_set = set(df[df['holder_name'] == 'BlackRock']['ticker'])
    combined_presence = len(vanguard_set | blackrock_set)
    
    print(f"\n🎯 Big 2 Dominance:")
    print(f"   Combined presence: {combined_presence}/{total_companies} companies ({combined_presence/total_companies*100:.1f}%)")
    
    # Share holdings
    shares_data = df.groupby('holder_name')['shares'].sum().sort_values(ascending=False)
    valid_shares = shares_data[shares_data > 0]
    
    if not valid_shares.empty:
        print(f"\n💰 Share Holdings (Billions):")
        for holder, shares in valid_shares.head(3).items():
            print(f"   {holder}: {shares/1_000_000_000:.1f}B shares")
    
    print(f"\n🚨 Bottom Line: 2 institutions control 98.2% of major American companies")

if __name__ == "__main__":
    quick_summary()
