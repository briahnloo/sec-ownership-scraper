#!/usr/bin/env python3
"""
Calculate actual market cap percentage controlled by institutional investors.
Combines ownership data with market capitalization to show true economic control.
"""

import pandas as pd
import requests
import time
from typing import Dict, Optional

class MarketCapAnalyzer:
    """Analyze actual market cap control by institutions"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.market_cap_cache = {}
    
    def get_market_cap_estimates(self, tickers: list) -> Dict[str, float]:
        """Get market cap estimates for tickers (simplified approach)"""
        
        print(f"📊 Getting market cap data for {len(tickers)} companies...")
        
        # For demonstration, I'll use approximate market caps for major companies
        # In a real implementation, you'd use a financial API like Alpha Vantage, Yahoo Finance, etc.
        
        approximate_market_caps = {
            # Technology Giants (in billions)
            'AAPL': 3000, 'MSFT': 2800, 'GOOGL': 1700, 'GOOG': 1700, 'AMZN': 1500,
            'NVDA': 1100, 'META': 800, 'TSLA': 700, 'NFLX': 200, 'ADBE': 180,
            'CRM': 200, 'ORCL': 300, 'IBM': 120, 'CSCO': 200, 'INTC': 150,
            'AMD': 200, 'QCOM': 180, 'AVGO': 600, 'TXN': 150,
            
            # Financial Services
            'BRK-A': 800, 'BRK-B': 800, 'JPM': 450, 'BAC': 250, 'WFC': 180,
            'GS': 120, 'MS': 100, 'C': 90, 'BLK': 100, 'V': 500, 'MA': 350,
            
            # Healthcare
            'UNH': 500, 'JNJ': 450, 'PFE': 200, 'ABBV': 250, 'LLY': 600,
            'MRK': 250, 'TMO': 200, 'ABT': 180, 'DHR': 150,
            
            # Consumer/Retail
            'WMT': 500, 'HD': 350, 'COST': 250, 'LOW': 150, 'TGT': 80,
            'DIS': 200, 'NKE': 150, 'SBUX': 100, 'MCD': 200, 'KO': 250, 'PEP': 230,
            
            # Energy
            'XOM': 400, 'CVX': 300, 'COP': 150,
            
            # Industrial
            'BA': 150, 'CAT': 150, 'GE': 120, 'HON': 140, 'RTX': 150, 'DE': 120, 'MMM': 80,
            
            # Default for others
        }
        
        # Add default market caps for companies not in our list
        for ticker in tickers:
            if ticker not in approximate_market_caps:
                # Estimate based on S&P 500 average (~15B)
                approximate_market_caps[ticker] = 15.0
        
        print(f"✅ Market cap data prepared for {len(tickers)} companies")
        return approximate_market_caps
    
    def calculate_market_cap_control(self):
        """Calculate actual market cap percentage controlled"""
        
        print("💰 MARKET CAPITALIZATION CONTROL ANALYSIS")
        print("=" * 60)
        
        # Load ownership data
        df = pd.read_csv("../results/comprehensive_market_ownership_20250918_195445.csv")
        
        # Get unique companies and their market caps
        companies = df['ticker'].unique()
        market_caps = self.get_market_cap_estimates(companies)
        
        # Calculate total market cap of analyzed companies
        total_market_cap = sum(market_caps.values())
        print(f"📊 Total market cap of analyzed companies: ${total_market_cap:.1f} billion")
        
        # Calculate market cap control by institution
        institution_control = {}
        
        for institution in df['holder_name'].unique():
            inst_df = df[df['holder_name'] == institution]
            inst_companies = inst_df['ticker'].unique()
            
            # Calculate market cap of companies where this institution has presence
            inst_market_cap = sum(market_caps.get(ticker, 0) for ticker in inst_companies)
            control_percentage = (inst_market_cap / total_market_cap) * 100
            
            institution_control[institution] = {
                'market_cap_billions': inst_market_cap,
                'control_percentage': control_percentage,
                'companies_count': len(inst_companies)
            }
        
        # Sort by market cap control
        sorted_institutions = sorted(institution_control.items(), 
                                   key=lambda x: x[1]['market_cap_billions'], 
                                   reverse=True)
        
        print(f"\n🏛️  MARKET CAP CONTROL BY INSTITUTION:")
        print(f"{'Institution':<25} {'Market Cap ($B)':<15} {'Control %':<10} {'Companies'}")
        print("-" * 65)
        
        for inst, data in sorted_institutions:
            print(f"{inst:<25} ${data['market_cap_billions']:<14.1f} {data['control_percentage']:<9.1f}% {data['companies_count']}")
        
        # Big 2 analysis
        vanguard_control = institution_control.get('Vanguard Group', {})
        blackrock_control = institution_control.get('BlackRock', {})
        
        # Calculate combined control (avoiding double counting)
        vanguard_companies = set(df[df['holder_name'] == 'Vanguard Group']['ticker'])
        blackrock_companies = set(df[df['holder_name'] == 'BlackRock']['ticker'])
        combined_companies = vanguard_companies | blackrock_companies
        
        combined_market_cap = sum(market_caps.get(ticker, 0) for ticker in combined_companies)
        combined_control_pct = (combined_market_cap / total_market_cap) * 100
        
        print(f"\n🎯 BIG 2 COMBINED MARKET CAP CONTROL:")
        print(f"   Vanguard market cap exposure: ${vanguard_control.get('market_cap_billions', 0):.1f}B ({vanguard_control.get('control_percentage', 0):.1f}%)")
        print(f"   BlackRock market cap exposure: ${blackrock_control.get('market_cap_billions', 0):.1f}B ({blackrock_control.get('control_percentage', 0):.1f}%)")
        print(f"   Combined market cap exposure: ${combined_market_cap:.1f}B ({combined_control_pct:.1f}%)")
        
        # Calculate weighted ownership (if we had exact percentages)
        print(f"\n📈 ESTIMATED ACTUAL OWNERSHIP:")
        print(f"   Note: This assumes average 5-8% institutional ownership per position")
        
        # Estimate actual ownership assuming average institutional stake
        avg_institutional_stake = 0.06  # 6% average per position
        
        vanguard_estimated_value = vanguard_control.get('market_cap_billions', 0) * avg_institutional_stake
        blackrock_estimated_value = blackrock_control.get('market_cap_billions', 0) * avg_institutional_stake
        combined_estimated_value = vanguard_estimated_value + blackrock_estimated_value
        
        print(f"   Vanguard estimated actual control: ${vanguard_estimated_value:.1f}B")
        print(f"   BlackRock estimated actual control: ${blackrock_estimated_value:.1f}B")
        print(f"   Combined estimated actual control: ${combined_estimated_value:.1f}B")
        print(f"   Combined % of total market: {(combined_estimated_value / total_market_cap) * 100:.1f}%")
        
        return {
            'total_market_cap': total_market_cap,
            'institution_control': institution_control,
            'combined_control_pct': combined_control_pct,
            'estimated_actual_control_pct': (combined_estimated_value / total_market_cap) * 100
        }

def main():
    """Main analysis execution"""
    
    analyzer = MarketCapAnalyzer()
    results = analyzer.calculate_market_cap_control()
    
    print(f"\n🚨 KEY FINDINGS:")
    print(f"   Market Cap Exposure: Vanguard + BlackRock have positions in companies worth ${results['total_market_cap']:.1f}B")
    print(f"   Combined Exposure: {results['combined_control_pct']:.1f}% of analyzed market cap")
    print(f"   Estimated Actual Control: ~{results['estimated_actual_control_pct']:.1f}% of total market value")
    
    print(f"\n⚠️  IMPORTANT NOTES:")
    print(f"   • Market cap data is estimated (would need real-time financial API)")
    print(f"   • Actual ownership percentages vary by company")
    print(f"   • This analysis shows EXPOSURE, not exact ownership")
    print(f"   • Real ownership likely 5-15% of each company on average")

if __name__ == "__main__":
    main()
