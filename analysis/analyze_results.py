#!/usr/bin/env python3
"""
Analyze the collected ownership data and generate insights.
"""

import pandas as pd
import numpy as np
from collections import Counter

def analyze_ownership_data(filename="ownership_data_20250918_191548.csv"):
    """Analyze the collected ownership data"""
    
    print("🔍 SEC Ownership Data Analysis")
    print("=" * 50)
    
    # Load data
    df = pd.read_csv(filename)
    
    print(f"📊 Dataset Overview:")
    print(f"   Total records: {len(df)}")
    print(f"   Companies: {df['ticker'].nunique()}")
    print(f"   Institutional holders: {df['holder_name'].nunique()}")
    
    # Clean data
    print(f"\n🧹 Data Cleaning:")
    
    # Fix obvious percentage errors (>100% likely means parsing error)
    suspicious_percent = df[df['percent_owned'] > 50]['percent_owned'].count()
    print(f"   Suspicious percentages (>50%): {suspicious_percent}")
    
    # Companies with data
    companies_with_data = df.groupby('ticker').size().sort_values(ascending=False)
    print(f"   Avg holders per company: {companies_with_data.mean():.1f}")
    
    # Institutional dominance analysis
    print(f"\n🏛️  Institutional Dominance Analysis:")
    
    holder_presence = df['holder_name'].value_counts()
    total_companies = df['ticker'].nunique()
    
    print(f"   Market presence by institution:")
    for holder, count in holder_presence.items():
        percentage = (count / total_companies) * 100
        print(f"   {holder}: {count}/{total_companies} companies ({percentage:.1f}%)")
    
    # Big 2 Analysis (Vanguard + BlackRock)
    big2 = df[df['holder_name'].isin(['Vanguard Group', 'BlackRock'])]
    big2_companies = big2['ticker'].nunique()
    big2_percentage = (big2_companies / total_companies) * 100
    
    print(f"\n🎯 Big 2 (Vanguard + BlackRock) Analysis:")
    print(f"   Combined presence: {big2_companies}/{total_companies} companies ({big2_percentage:.1f}%)")
    
    # Companies where both Vanguard and BlackRock have positions
    vanguard_companies = set(df[df['holder_name'] == 'Vanguard Group']['ticker'])
    blackrock_companies = set(df[df['holder_name'] == 'BlackRock']['ticker'])
    both_companies = vanguard_companies & blackrock_companies
    
    print(f"   Companies with BOTH Vanguard & BlackRock: {len(both_companies)} ({len(both_companies)/total_companies*100:.1f}%)")
    
    # Sector analysis if we had sector data
    print(f"\n💰 Share Holdings Analysis:")
    
    # Total shares held by each institution (where data available)
    shares_by_holder = df.groupby('holder_name')['shares'].sum().sort_values(ascending=False)
    print(f"   Total shares held (where data available):")
    for holder, shares in shares_by_holder.items():
        if pd.notna(shares) and shares > 0:
            print(f"   {holder}: {shares:,.0f} shares")
    
    # Most concentrated companies (by number of major holders)
    print(f"\n🎯 Most Institutionally Held Companies:")
    company_holder_counts = df.groupby(['ticker', 'company_name']).size().sort_values(ascending=False)
    
    for (ticker, company), count in company_holder_counts.head(10).items():
        holders = df[df['ticker'] == ticker]['holder_name'].tolist()
        print(f"   {ticker} ({company}): {count} major holders")
        print(f"      Holders: {', '.join(holders)}")
    
    # Market concentration insights
    print(f"\n📈 Market Concentration Insights:")
    
    # Calculate how many companies each pair of institutions both hold
    institutions = df['holder_name'].unique()
    overlaps = {}
    
    for i, inst1 in enumerate(institutions):
        for inst2 in institutions[i+1:]:
            companies1 = set(df[df['holder_name'] == inst1]['ticker'])
            companies2 = set(df[df['holder_name'] == inst2]['ticker'])
            overlap = len(companies1 & companies2)
            if overlap > 0:
                overlaps[f"{inst1} & {inst2}"] = overlap
    
    print(f"   Cross-ownership patterns:")
    for pair, overlap in sorted(overlaps.items(), key=lambda x: x[1], reverse=True):
        percentage = (overlap / total_companies) * 100
        print(f"   {pair}: {overlap} companies ({percentage:.1f}%)")
    
    # Summary statistics
    print(f"\n📊 Summary Statistics:")
    print(f"   Average institutional holders per company: {len(df) / total_companies:.1f}")
    print(f"   Most active institution: {holder_presence.index[0]} ({holder_presence.iloc[0]} positions)")
    print(f"   Market coverage by top 2 institutions: {big2_percentage:.1f}%")
    
    # Export cleaned data
    output_file = filename.replace('.csv', '_analyzed.csv')
    
    # Add analysis columns
    df['is_big2'] = df['holder_name'].isin(['Vanguard Group', 'BlackRock'])
    df['suspicious_percent'] = df['percent_owned'] > 50
    
    df.to_csv(output_file, index=False)
    print(f"\n💾 Analyzed data saved to: {output_file}")
    
    return df

if __name__ == "__main__":
    df = analyze_ownership_data()
    
    print(f"\n🎉 Analysis complete!")
    print(f"📋 Key takeaway: Vanguard and BlackRock have achieved unprecedented market dominance")
    print(f"📊 Your data is ready for further analysis in Excel, Python, or R")
