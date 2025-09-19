#!/usr/bin/env python3
"""
Comprehensive American Market Ownership Scraper
Dynamically fetches full S&P 500 and processes 500+ companies for complete market analysis.
"""

import time
import requests
import pandas as pd
import re
from typing import Dict, List, Optional
from datetime import datetime

class ComprehensiveMarketScraper:
    """Comprehensive scraper for full American market analysis"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def scrape_full_market(self, target_companies: int = 500) -> pd.DataFrame:
        """Scrape ownership data from comprehensive market coverage"""
        
        print(f"🚀 COMPREHENSIVE AMERICAN MARKET OWNERSHIP SCRAPER")
        print(f"📊 Target: {target_companies} companies (Full S&P 500 + Major Companies)")
        print(f"⏱️  Expected time: {target_companies * 15} seconds ({target_companies * 0.25:.1f} minutes)")
        print(f"🎯 This will provide complete institutional ownership analysis across American markets\n")
        
        start_time = time.time()
        
        # Step 1: Get comprehensive company list
        print("📋 Loading comprehensive American market companies...")
        companies = self._get_comprehensive_companies()
        
        if target_companies > 0 and target_companies < len(companies):
            companies = companies[:target_companies]
        
        print(f"✅ Loaded {len(companies)} companies for processing\n")
        
        # Step 2: Process all companies with optimized progress tracking
        all_ownership_data = []
        successful_companies = 0
        failed_companies = 0
        
        for i, (ticker, company_name) in enumerate(companies, 1):
            print(f"--- {i}/{len(companies)}: {ticker} ({company_name}) ---")
            
            company_start = time.time()
            holders = self._get_company_institutional_holders(ticker, company_name)
            company_time = time.time() - company_start
            
            if holders:
                all_ownership_data.extend(holders)
                successful_companies += 1
                print(f"✅ Found {len(holders)} institutional holders in {company_time:.1f}s")
            else:
                failed_companies += 1
                print(f"⚠️  No institutional data found in {company_time:.1f}s")
            
            # Enhanced progress tracking for large scale
            if i % 50 == 0 or i <= 10:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                remaining_time = (len(companies) - i) / rate if rate > 0 else 0
                
                print(f"\n📊 MAJOR PROGRESS CHECKPOINT:")
                print(f"   Processed: {i}/{len(companies)} companies ({i/len(companies)*100:.1f}%)")
                print(f"   Success rate: {successful_companies}/{i} ({successful_companies/i*100:.1f}%)")
                print(f"   Current rate: {rate*60:.1f} companies/min")
                print(f"   Time elapsed: {elapsed/60:.1f} minutes")
                print(f"   ETA: {remaining_time/60:.1f} minutes remaining")
                print(f"   Records collected so far: {len(all_ownership_data)}")
                print("="*60 + "\n")
            elif i % 10 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                remaining_time = (len(companies) - i) / rate if rate > 0 else 0
                print(f"📈 Progress: {i}/{len(companies)} ({i/len(companies)*100:.1f}%) - ETA: {remaining_time/60:.1f} min\n")
            
            # Rate limiting to respect SEC guidelines
            time.sleep(0.1)  # Faster rate for large scale
        
        # Step 3: Generate comprehensive results
        total_time = time.time() - start_time
        
        if all_ownership_data:
            df = pd.DataFrame(all_ownership_data)
            
            print(f"\n🎉 COMPREHENSIVE MARKET ANALYSIS COMPLETE!")
            print(f"⏱️  Total processing time: {total_time/60:.1f} minutes ({total_time/3600:.1f} hours)")
            print(f"📊 Final Results:")
            print(f"   Total ownership records: {len(df)}")
            print(f"   Companies successfully processed: {successful_companies}")
            print(f"   Companies with no data: {failed_companies}")
            print(f"   Unique institutional holders: {df['holder_name'].nunique()}")
            print(f"   Average processing rate: {len(companies)/(total_time/60):.1f} companies/minute")
            
            return df
        else:
            print(f"❌ No ownership data collected in {total_time/60:.1f} minutes")
            return pd.DataFrame()
    
    def _get_comprehensive_companies(self) -> List[tuple]:
        """Get comprehensive list of American public companies"""
        
        # Try to fetch live S&P 500 list
        try:
            print("📡 Fetching live S&P 500 companies from Wikipedia...")
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            # Parse the Wikipedia table
            tables = pd.read_html(response.text)
            sp500_df = tables[0]
            
            # Clean the data
            companies = []
            for _, row in sp500_df.iterrows():
                try:
                    ticker = str(row.iloc[0]).replace('.', '-').strip().upper()
                    name = str(row.iloc[1]).strip()
                    
                    # Validate ticker format
                    if ticker and name and len(ticker) <= 6 and ticker.isalnum() or '-' in ticker:
                        companies.append((ticker, name))
                except Exception:
                    continue
            
            print(f"✅ Successfully loaded {len(companies)} S&P 500 companies dynamically!")
            
            # Add additional major companies for broader coverage
            additional_companies = self._get_additional_major_companies()
            companies.extend(additional_companies)
            
            print(f"✅ Total companies for comprehensive analysis: {len(companies)}")
            return companies
            
        except Exception as e:
            print(f"⚠️  Failed to fetch live S&P 500: {e}")
            print("📋 Using comprehensive backup company list...")
            return self._get_backup_comprehensive_list()
    
    def _get_additional_major_companies(self) -> List[tuple]:
        """Additional major companies beyond S&P 500"""
        return [
            # Major tech companies
            ('UBER', 'Uber Technologies Inc.'),
            ('SNAP', 'Snap Inc.'),
            ('SPOT', 'Spotify Technology S.A.'),
            ('ZM', 'Zoom Video Communications Inc.'),
            ('PLTR', 'Palantir Technologies Inc.'),
            ('RBLX', 'Roblox Corporation'),
            ('COIN', 'Coinbase Global Inc.'),
            ('RIVN', 'Rivian Automotive Inc.'),
            
            # Major financial services
            ('SOFI', 'SoFi Technologies Inc.'),
            ('UPST', 'Upstart Holdings Inc.'),
            ('AFRM', 'Affirm Holdings Inc.'),
            
            # Major retail/consumer
            ('CHWY', 'Chewy Inc.'),
            ('ETSY', 'Etsy Inc.'),
            ('W', 'Wayfair Inc.'),
            
            # Major healthcare/biotech
            ('MRNA', 'Moderna Inc.'),
            ('BNTX', 'BioNTech SE'),
            ('NVAX', 'Novavax Inc.'),
        ]
    
    def _get_backup_comprehensive_list(self) -> List[tuple]:
        """Comprehensive backup list of major American companies"""
        return [
            # Technology Giants
            ('AAPL', 'Apple Inc.'),
            ('MSFT', 'Microsoft Corporation'),
            ('GOOGL', 'Alphabet Inc.'),
            ('GOOG', 'Alphabet Inc. Class C'),
            ('AMZN', 'Amazon.com Inc.'),
            ('NVDA', 'NVIDIA Corporation'),
            ('TSLA', 'Tesla Inc.'),
            ('META', 'Meta Platforms Inc.'),
            ('NFLX', 'Netflix Inc.'),
            ('ADBE', 'Adobe Inc.'),
            ('CRM', 'Salesforce Inc.'),
            ('ORCL', 'Oracle Corporation'),
            ('IBM', 'International Business Machines Corporation'),
            ('CSCO', 'Cisco Systems Inc.'),
            ('INTC', 'Intel Corporation'),
            ('AMD', 'Advanced Micro Devices Inc.'),
            ('QCOM', 'QUALCOMM Incorporated'),
            ('AVGO', 'Broadcom Inc.'),
            ('TXN', 'Texas Instruments Incorporated'),
            
            # Financial Services
            ('BRK-A', 'Berkshire Hathaway Inc. Class A'),
            ('BRK-B', 'Berkshire Hathaway Inc. Class B'),
            ('JPM', 'JPMorgan Chase & Co.'),
            ('BAC', 'Bank of America Corporation'),
            ('WFC', 'Wells Fargo & Company'),
            ('GS', 'Goldman Sachs Group Inc.'),
            ('MS', 'Morgan Stanley'),
            ('C', 'Citigroup Inc.'),
            ('BLK', 'BlackRock Inc.'),
            ('SPGI', 'S&P Global Inc.'),
            ('CME', 'CME Group Inc.'),
            ('ICE', 'Intercontinental Exchange Inc.'),
            ('V', 'Visa Inc.'),
            ('MA', 'Mastercard Incorporated'),
            ('PYPL', 'PayPal Holdings Inc.'),
            ('AXP', 'American Express Company'),
            
            # Healthcare & Pharmaceuticals
            ('UNH', 'UnitedHealth Group Inc.'),
            ('JNJ', 'Johnson & Johnson'),
            ('PFE', 'Pfizer Inc.'),
            ('ABBV', 'AbbVie Inc.'),
            ('LLY', 'Eli Lilly and Company'),
            ('MRK', 'Merck & Co. Inc.'),
            ('TMO', 'Thermo Fisher Scientific Inc.'),
            ('ABT', 'Abbott Laboratories'),
            ('DHR', 'Danaher Corporation'),
            ('BMY', 'Bristol-Myers Squibb Company'),
            ('AMGN', 'Amgen Inc.'),
            ('GILD', 'Gilead Sciences Inc.'),
            ('CVS', 'CVS Health Corporation'),
            ('CI', 'Cigna Corporation'),
            ('ANTM', 'Anthem Inc.'),
            ('HUM', 'Humana Inc.'),
            
            # Consumer & Retail
            ('WMT', 'Walmart Inc.'),
            ('HD', 'Home Depot Inc.'),
            ('COST', 'Costco Wholesale Corporation'),
            ('LOW', 'Lowe\'s Companies Inc.'),
            ('TGT', 'Target Corporation'),
            ('DIS', 'Walt Disney Company'),
            ('NKE', 'Nike Inc.'),
            ('SBUX', 'Starbucks Corporation'),
            ('MCD', 'McDonald\'s Corporation'),
            ('KO', 'Coca-Cola Company'),
            ('PEP', 'PepsiCo Inc.'),
            ('PG', 'Procter & Gamble Company'),
            ('UL', 'Unilever PLC'),
            ('CL', 'Colgate-Palmolive Company'),
            ('KMB', 'Kimberly-Clark Corporation'),
            
            # Energy
            ('XOM', 'Exxon Mobil Corporation'),
            ('CVX', 'Chevron Corporation'),
            ('COP', 'ConocoPhillips'),
            ('EOG', 'EOG Resources Inc.'),
            ('SLB', 'Schlumberger Limited'),
            ('PSX', 'Phillips 66'),
            ('VLO', 'Valero Energy Corporation'),
            ('MPC', 'Marathon Petroleum Corporation'),
            ('OXY', 'Occidental Petroleum Corporation'),
            ('HAL', 'Halliburton Company'),
            
            # Industrials
            ('BA', 'Boeing Company'),
            ('CAT', 'Caterpillar Inc.'),
            ('GE', 'General Electric Company'),
            ('HON', 'Honeywell International Inc.'),
            ('RTX', 'Raytheon Technologies Corporation'),
            ('LMT', 'Lockheed Martin Corporation'),
            ('NOC', 'Northrop Grumman Corporation'),
            ('GD', 'General Dynamics Corporation'),
            ('DE', 'Deere & Company'),
            ('EMR', 'Emerson Electric Co.'),
            ('ETN', 'Eaton Corporation plc'),
            ('PH', 'Parker-Hannifin Corporation'),
            ('ITW', 'Illinois Tool Works Inc.'),
            ('MMM', '3M Company'),
            
            # Telecommunications & Media
            ('VZ', 'Verizon Communications Inc.'),
            ('T', 'AT&T Inc.'),
            ('TMUS', 'T-Mobile US Inc.'),
            ('CHTR', 'Charter Communications Inc.'),
            ('CMCSA', 'Comcast Corporation'),
            ('DISH', 'DISH Network Corporation'),
            
            # Utilities
            ('NEE', 'NextEra Energy Inc.'),
            ('DUK', 'Duke Energy Corporation'),
            ('SO', 'Southern Company'),
            ('D', 'Dominion Energy Inc.'),
            ('EXC', 'Exelon Corporation'),
            ('AEP', 'American Electric Power Company Inc.'),
            ('XEL', 'Xcel Energy Inc.'),
            ('SRE', 'Sempra Energy'),
            ('PEG', 'Public Service Enterprise Group Inc.'),
            ('ED', 'Consolidated Edison Inc.'),
            
            # Transportation & Logistics
            ('UPS', 'United Parcel Service Inc.'),
            ('FDX', 'FedEx Corporation'),
            ('AAL', 'American Airlines Group Inc.'),
            ('DAL', 'Delta Air Lines Inc.'),
            ('UAL', 'United Airlines Holdings Inc.'),
            ('LUV', 'Southwest Airlines Co.'),
            ('JBLU', 'JetBlue Airways Corporation'),
            ('CSX', 'CSX Corporation'),
            ('UNP', 'Union Pacific Corporation'),
            ('NSC', 'Norfolk Southern Corporation'),
            
            # Real Estate
            ('AMT', 'American Tower Corporation'),
            ('PLD', 'Prologis Inc.'),
            ('CCI', 'Crown Castle International Corp.'),
            ('EQIX', 'Equinix Inc.'),
            ('SPG', 'Simon Property Group Inc.'),
            ('O', 'Realty Income Corporation'),
            ('WELL', 'Welltower Inc.'),
            ('AVB', 'AvalonBay Communities Inc.'),
            ('EQR', 'Equity Residential'),
            ('ESS', 'Essex Property Trust Inc.'),
            
            # Materials & Chemicals
            ('LIN', 'Linde plc'),
            ('APD', 'Air Products and Chemicals Inc.'),
            ('SHW', 'Sherwin-Williams Company'),
            ('DD', 'DuPont de Nemours Inc.'),
            ('DOW', 'Dow Inc.'),
            ('PPG', 'PPG Industries Inc.'),
            ('ECL', 'Ecolab Inc.'),
            ('FCX', 'Freeport-McMoRan Inc.'),
            ('NEM', 'Newmont Corporation'),
            ('ALB', 'Albemarle Corporation'),
        ]
    
    def _get_company_institutional_holders(self, ticker: str, company_name: str) -> List[Dict]:
        """Get institutional holders for a company with optimized processing"""
        
        try:
            # Step 1: Get CIK (optimized)
            cik = self._get_cik_fast(ticker)
            if not cik:
                return []
            
            # Step 2: Get latest filing (optimized)
            filing_url = self._get_latest_filing_url_fast(cik)
            if not filing_url:
                return []
            
            # Step 3: Download and parse (optimized)
            content = self._download_filing_fast(filing_url)
            if not content:
                return []
            
            # Step 4: Extract institutional holders (optimized)
            holders = self._extract_institutional_holders_fast(content, ticker, company_name)
            
            return holders
            
        except Exception as e:
            return []
    
    def _get_cik_fast(self, ticker: str) -> Optional[str]:
        """Fast CIK lookup with caching"""
        if not hasattr(self, '_cik_cache'):
            try:
                url = "https://www.sec.gov/files/company_tickers.json"
                response = self.session.get(url, timeout=10)
                data = response.json()
                
                self._cik_cache = {}
                for record in data.values():
                    self._cik_cache[record['ticker'].upper()] = str(record['cik_str']).zfill(10)
            except:
                self._cik_cache = {}
        
        return self._cik_cache.get(ticker.upper())
    
    def _get_latest_filing_url_fast(self, cik: str) -> Optional[str]:
        """Fast filing URL lookup"""
        try:
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            filings = data.get('filings', {}).get('recent', {})
            forms = filings.get('form', [])
            accessions = filings.get('accessionNumber', [])
            primary_docs = filings.get('primaryDocument', [])
            
            # Find latest DEF 14A
            for i, form in enumerate(forms):
                if str(form).strip().upper() == 'DEF 14A':
                    acc_no = accessions[i].replace('-', '')
                    primary_doc = primary_docs[i] if i < len(primary_docs) else ""
                    
                    if primary_doc:
                        return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no}/{primary_doc}"
            
            return None
        except:
            return None
    
    def _download_filing_fast(self, url: str) -> Optional[str]:
        """Fast filing download with timeout optimization"""
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            return response.text
        except:
            return None
    
    def _extract_institutional_holders_fast(self, content: str, ticker: str, company_name: str) -> List[Dict]:
        """Fast institutional holder extraction optimized for scale"""
        
        # Top institutional investors with optimized patterns
        major_institutions = {
            'Vanguard Group': [r'vanguard\s+group', r'the\s+vanguard\s+group'],
            'BlackRock': [r'blackrock,?\s+inc', r'blackrock\s+fund'],
            'State Street': [r'state\s+street\s+corp', r'state\s+street\s+corporation'],
            'Fidelity': [r'fidelity\s+management', r'fmr\s+llc'],
            'T. Rowe Price': [r't\.?\s*rowe\s+price'],
            'Berkshire Hathaway': [r'berkshire\s+hathaway'],
            'JPMorgan': [r'jpmorgan\s+chase', r'jp\s+morgan'],
            'Capital Group': [r'capital\s+group', r'capital\s+research'],
            'Wellington Management': [r'wellington\s+management'],
            'Invesco': [r'invesco\s+ltd'],
            'Northern Trust': [r'northern\s+trust'],
            'Bank of New York Mellon': [r'bank\s+of\s+new\s+york\s+mellon', r'bny\s+mellon'],
            'Goldman Sachs Asset Management': [r'goldman\s+sachs\s+asset', r'gsam'],
            'Morgan Stanley Investment Management': [r'morgan\s+stanley\s+investment'],
            'Dimensional Fund Advisors': [r'dimensional\s+fund'],
        }
        
        holders = []
        content_lower = content.lower()
        
        for institution_name, patterns in major_institutions.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, content_lower))
                
                if matches:
                    # Look around the match for numerical data
                    match = matches[0]
                    context_start = max(0, match.start() - 800)
                    context_end = min(len(content), match.end() + 800)
                    context = content[context_start:context_end]
                    
                    # Extract shares (optimized pattern)
                    shares_match = re.search(r'(\d{1,3}(?:,\d{3}){1,4})', context)
                    shares = None
                    if shares_match:
                        try:
                            shares = int(shares_match.group(1).replace(',', ''))
                            # Validate reasonable share count (1K to 10B shares)
                            if not (1000 <= shares <= 10_000_000_000):
                                shares = None
                        except:
                            shares = None
                    
                    # Extract percentage (optimized pattern)
                    percent_match = re.search(r'(\d{1,2}\.?\d*)\s*%', context)
                    percent = None
                    if percent_match:
                        try:
                            percent = float(percent_match.group(1))
                            # Validate reasonable percentage (0.1% to 50%)
                            if not (0.1 <= percent <= 50.0):
                                percent = None
                        except:
                            percent = None
                    
                    # Only include if we found valid data
                    if shares or percent:
                        holder_record = {
                            'ticker': ticker,
                            'company_name': company_name,
                            'holder_name': institution_name,
                            'shares': shares,
                            'percent_owned': percent,
                            'filing_date': datetime.now().strftime('%Y-%m-%d')
                        }
                        holders.append(holder_record)
                        break  # Only take first valid match per institution
        
        return holders

def main():
    """Main execution for comprehensive market analysis"""
    scraper = ComprehensiveMarketScraper()
    
    print("="*80)
    print("🏛️  COMPREHENSIVE AMERICAN MARKET INSTITUTIONAL OWNERSHIP ANALYSIS")
    print("="*80)
    
    # Run comprehensive market scraping
    df = scraper.scrape_full_market(target_companies=500)
    
    if not df.empty:
        # Save comprehensive results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"comprehensive_market_ownership_{timestamp}.csv"
        df.to_csv(filename, index=False)
        
        print(f"\n💾 COMPREHENSIVE DATA SAVED TO: {filename}")
        
        # Generate comprehensive analysis
        print(f"\n🔍 COMPREHENSIVE MARKET ANALYSIS:")
        
        # Institutional dominance analysis
        holder_presence = df['holder_name'].value_counts()
        total_companies = df['ticker'].nunique()
        
        print(f"\n🏛️  INSTITUTIONAL MARKET DOMINANCE:")
        for holder, count in holder_presence.head(10).items():
            percentage = (count / total_companies) * 100
            print(f"   {holder}: {count}/{total_companies} companies ({percentage:.1f}%)")
        
        # Market concentration insights
        print(f"\n📊 MARKET CONCENTRATION METRICS:")
        print(f"   Total institutional ownership records: {len(df)}")
        print(f"   Companies with institutional data: {total_companies}")
        print(f"   Unique institutional holders: {df['holder_name'].nunique()}")
        print(f"   Average institutional holders per company: {len(df)/total_companies:.1f}")
        
        # Big 2 analysis (Vanguard + BlackRock)
        big2_companies = df[df['holder_name'].isin(['Vanguard Group', 'BlackRock'])]['ticker'].nunique()
        big2_percentage = (big2_companies / total_companies) * 100
        print(f"   Vanguard + BlackRock combined presence: {big2_companies}/{total_companies} companies ({big2_percentage:.1f}%)")
        
        # Total shares analysis
        shares_by_holder = df.groupby('holder_name')['shares'].sum().sort_values(ascending=False)
        print(f"\n💰 TOTAL SHARES HELD (where data available):")
        for holder, total_shares in shares_by_holder.head(8).items():
            if pd.notna(total_shares) and total_shares > 0:
                print(f"   {holder}: {total_shares:,.0f} shares")
        
        print(f"\n🎉 COMPREHENSIVE AMERICAN MARKET ANALYSIS COMPLETE!")
        print(f"📊 Your data is ready for advanced institutional ownership analysis!")
        
    else:
        print("❌ No comprehensive data collected")

if __name__ == "__main__":
    main()
