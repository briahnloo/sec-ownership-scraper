#!/usr/bin/env python3
"""
Simple, fast SEC ownership scraper - gets the job done in minutes, not hours.
Focus: Extract top institutional holders quickly with minimal complexity.
"""

import time
import requests
import pandas as pd
import re
from typing import Dict, List, Optional
from datetime import datetime

class SimpleOwnershipScraper:
    """Simple, fast scraper focused on results"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def scrape_top_companies(self, num_companies: int = 5) -> pd.DataFrame:
        """Scrape ownership data from top companies quickly"""
        
        print(f"🚀 Simple SEC Ownership Scraper - SCALED UP")
        print(f"📊 Target: {num_companies} companies")
        print(f"⏱️  Expected time: {num_companies * 30} seconds ({num_companies * 0.5:.1f} minutes)\n")
        
        start_time = time.time()
        
        # Step 1: Get top companies (hardcoded for speed)
        companies = self._get_top_companies()[:num_companies]
        print(f"✅ Got {len(companies)} companies to process\n")
        
        # Step 2: Process each company
        all_data = []
        
        for i, (ticker, company_name) in enumerate(companies, 1):
            print(f"--- {i}/{len(companies)}: {ticker} ({company_name}) ---")
            
            company_start = time.time()
            holders = self._get_company_holders(ticker, company_name)
            company_time = time.time() - company_start
            
            if holders:
                all_data.extend(holders)
                print(f"✅ Found {len(holders)} holders in {company_time:.1f}s")
            else:
                print(f"⚠️  No data found in {company_time:.1f}s")
            
            # Progress indicator
            if i % 10 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                remaining = (len(companies) - i) / rate if rate > 0 else 0
                print(f"📊 Progress: {i}/{len(companies)} companies ({i/len(companies)*100:.1f}%) - ETA: {remaining/60:.1f} min\n")
            else:
                print()  # Empty line for readability
        
        # Step 3: Create results
        total_time = time.time() - start_time
        
        if all_data:
            df = pd.DataFrame(all_data)
            print(f"🎉 COMPLETE! Total time: {total_time:.1f}s")
            print(f"📊 Collected {len(df)} records from {df['ticker'].nunique()} companies")
            return df
        else:
            print(f"❌ No data collected in {total_time:.1f}s")
            return pd.DataFrame()
    
    def _get_top_companies(self) -> List[tuple]:
        """Get top companies list (expanded for comprehensive analysis)"""
        # Top 60 S&P 500 companies by market cap
        return [
            ('AAPL', 'Apple Inc.'),
            ('MSFT', 'Microsoft Corporation'),
            ('GOOGL', 'Alphabet Inc.'),
            ('AMZN', 'Amazon.com Inc.'),
            ('NVDA', 'NVIDIA Corporation'),
            ('TSLA', 'Tesla Inc.'),
            ('META', 'Meta Platforms Inc.'),
            ('BRK-B', 'Berkshire Hathaway Inc.'),
            ('UNH', 'UnitedHealth Group Inc.'),
            ('JNJ', 'Johnson & Johnson'),
            ('XOM', 'Exxon Mobil Corporation'),
            ('JPM', 'JPMorgan Chase & Co.'),
            ('V', 'Visa Inc.'),
            ('PG', 'Procter & Gamble Company'),
            ('MA', 'Mastercard Incorporated'),
            ('HD', 'Home Depot Inc.'),
            ('CVX', 'Chevron Corporation'),
            ('ABBV', 'AbbVie Inc.'),
            ('PFE', 'Pfizer Inc.'),
            ('KO', 'Coca-Cola Company'),
            ('LLY', 'Eli Lilly and Company'),
            ('AVGO', 'Broadcom Inc.'),
            ('WMT', 'Walmart Inc.'),
            ('BAC', 'Bank of America Corporation'),
            ('ORCL', 'Oracle Corporation'),
            ('CRM', 'Salesforce Inc.'),
            ('COST', 'Costco Wholesale Corporation'),
            ('NFLX', 'Netflix Inc.'),
            ('AMD', 'Advanced Micro Devices Inc.'),
            ('ADBE', 'Adobe Inc.'),
            ('TMO', 'Thermo Fisher Scientific Inc.'),
            ('ACN', 'Accenture plc'),
            ('MRK', 'Merck & Co. Inc.'),
            ('TXN', 'Texas Instruments Incorporated'),
            ('LIN', 'Linde plc'),
            ('CSCO', 'Cisco Systems Inc.'),
            ('ABT', 'Abbott Laboratories'),
            ('WFC', 'Wells Fargo & Company'),
            ('DHR', 'Danaher Corporation'),
            ('VZ', 'Verizon Communications Inc.'),
            ('QCOM', 'QUALCOMM Incorporated'),
            ('INTC', 'Intel Corporation'),
            ('CMCSA', 'Comcast Corporation'),
            ('IBM', 'International Business Machines Corporation'),
            ('T', 'AT&T Inc.'),
            ('CAT', 'Caterpillar Inc.'),
            ('GE', 'General Electric Company'),
            ('NEE', 'NextEra Energy Inc.'),
            ('RTX', 'Raytheon Technologies Corporation'),
            ('HON', 'Honeywell International Inc.'),
            ('SPGI', 'S&P Global Inc.'),
            ('LOW', 'Lowe\'s Companies Inc.'),
            ('INTU', 'Intuit Inc.'),
            ('UPS', 'United Parcel Service Inc.'),
            ('MS', 'Morgan Stanley'),
            ('GS', 'Goldman Sachs Group Inc.'),
            ('AMGN', 'Amgen Inc.'),
            ('DE', 'Deere & Company'),
            ('BKNG', 'Booking Holdings Inc.'),
            ('BLK', 'BlackRock Inc.')
        ]
    
    def _get_company_holders(self, ticker: str, company_name: str) -> List[Dict]:
        """Get institutional holders for a company"""
        
        try:
            # Step 1: Get CIK
            print(f"  🔍 Getting CIK for {ticker}...")
            cik = self._get_cik(ticker)
            if not cik:
                print(f"  ❌ No CIK found")
                return []
            print(f"  ✅ CIK: {cik}")
            
            # Step 2: Get latest filing
            print(f"  📥 Getting latest DEF 14A...")
            filing_url = self._get_latest_filing_url(cik)
            if not filing_url:
                print(f"  ❌ No DEF 14A found")
                return []
            print(f"  ✅ Filing found")
            
            # Step 3: Download and parse
            print(f"  📄 Downloading filing...")
            content = self._download_filing(filing_url)
            if not content:
                print(f"  ❌ Download failed")
                return []
            print(f"  ✅ Downloaded {len(content):,} bytes")
            
            # Step 4: Extract holders
            print(f"  🔍 Extracting holders...")
            holders = self._extract_holders_simple(content, ticker, company_name)
            print(f"  ✅ Found {len(holders)} institutional holders")
            
            return holders
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}")
            return []
    
    def _get_cik(self, ticker: str) -> Optional[str]:
        """Get CIK for ticker"""
        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            for record in data.values():
                if record['ticker'].upper() == ticker.upper():
                    return str(record['cik_str']).zfill(10)
            
            return None
        except:
            return None
    
    def _get_latest_filing_url(self, cik: str) -> Optional[str]:
        """Get latest DEF 14A filing URL"""
        try:
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = self.session.get(url, timeout=15)
            data = response.json()
            
            filings = data.get('filings', {}).get('recent', {})
            forms = filings.get('form', [])
            accessions = filings.get('accessionNumber', [])
            primary_docs = filings.get('primaryDocument', [])
            
            # Find latest DEF 14A
            for i, form in enumerate(forms):
                if str(form).strip().upper() in ['DEF 14A']:
                    acc_no = accessions[i].replace('-', '')
                    primary_doc = primary_docs[i] if i < len(primary_docs) else ""
                    
                    if primary_doc:
                        return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no}/{primary_doc}"
            
            return None
        except:
            return None
    
    def _download_filing(self, url: str) -> Optional[str]:
        """Download filing content"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except:
            return None
    
    def _extract_holders_simple(self, content: str, ticker: str, company_name: str) -> List[Dict]:
        """Simple pattern-based holder extraction"""
        
        # Known institutional investors with their patterns
        institutions = {
            'Vanguard Group': [
                r'vanguard\s+group',
                r'the\s+vanguard\s+group',
                r'vanguard\s+fiduciary'
            ],
            'BlackRock': [
                r'blackrock,?\s+inc',
                r'blackrock\s+fund',
                r'blackrock\s+institutional'
            ],
            'State Street': [
                r'state\s+street\s+corp',
                r'state\s+street\s+corporation',
                r'state\s+street\s+global'
            ],
            'Fidelity': [
                r'fidelity\s+management',
                r'fmr\s+llc',
                r'fidelity\s+investments'
            ],
            'T. Rowe Price': [
                r't\.?\s*rowe\s+price',
                r't\.\s*rowe\s+price\s+associates'
            ],
            'Berkshire Hathaway': [
                r'berkshire\s+hathaway'
            ],
            'JPMorgan': [
                r'jpmorgan\s+chase',
                r'jp\s+morgan'
            ],
            'Capital Group': [
                r'capital\s+group',
                r'capital\s+research'
            ]
        }
        
        holders = []
        content_lower = content.lower()
        
        for institution_name, patterns in institutions.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, content_lower))
                
                if matches:
                    # Look around the first match for numbers
                    match = matches[0]
                    start = max(0, match.start() - 1000)
                    end = min(len(content), match.end() + 1000)
                    context = content[start:end]
                    
                    # Extract shares (large numbers with commas)
                    shares_match = re.search(r'(\d{1,3}(?:,\d{3}){1,3})', context)
                    shares = None
                    if shares_match:
                        try:
                            shares = int(shares_match.group(1).replace(',', ''))
                        except:
                            pass
                    
                    # Extract percentage
                    percent_match = re.search(r'(\d+\.?\d*)\s*%', context)
                    percent = None
                    if percent_match:
                        try:
                            percent = float(percent_match.group(1))
                        except:
                            pass
                    
                    # Only include if we found meaningful data
                    if shares or percent:
                        holder = {
                            'ticker': ticker,
                            'company_name': company_name,
                            'holder_name': institution_name,
                            'shares': shares,
                            'percent_owned': percent,
                            'filing_date': datetime.now().strftime('%Y-%m-%d')
                        }
                        holders.append(holder)
                        break  # Only take first match per institution
        
        return holders

def main():
    """Main execution"""
    scraper = SimpleOwnershipScraper()
    
    # Scale up to 50 companies
    df = scraper.scrape_top_companies(num_companies=50)
    
    if not df.empty:
        # Save results
        filename = f"ownership_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"\n💾 Saved to: {filename}")
        
        # Show results
        print(f"\n📊 Results:")
        print(df.to_string(index=False))
        
        # Quick analysis
        print(f"\n🔍 Quick Analysis:")
        print(f"Most active holders:")
        holder_counts = df.groupby('holder_name').size().sort_values(ascending=False)
        for holder, count in holder_counts.items():
            print(f"  {holder}: {count} positions")
    
    else:
        print("❌ No data collected")

if __name__ == "__main__":
    main()
