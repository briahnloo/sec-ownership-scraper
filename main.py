#!/usr/bin/env python3
"""
SEC Ownership Scraper - Main Entry Point
Comprehensive analysis of institutional ownership in American stock markets.
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'analysis'))

def main():
    """Main entry point with user menu"""
    
    print("🏛️  SEC OWNERSHIP SCRAPER")
    print("=" * 50)
    print("Comprehensive Institutional Ownership Analysis")
    print("=" * 50)
    
    print("\nChoose an option:")
    print("1. Run comprehensive market scraper (500 companies)")
    print("2. Run quick analysis (50 companies)")
    print("3. Generate visualizations from existing data")
    print("4. Show quick summary of results")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        print("\n🚀 Running comprehensive market scraper...")
        from comprehensive_market_scraper import main as run_comprehensive
        run_comprehensive()
        
    elif choice == "2":
        print("\n⚡ Running quick analysis...")
        from simple_scraper import main as run_simple
        # Modify to run 50 companies
        import simple_scraper
        scraper = simple_scraper.SimpleOwnershipScraper()
        df = scraper.scrape_top_companies(num_companies=50)
        if not df.empty:
            filename = f"quick_ownership_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(f"results/{filename}", index=False)
            print(f"💾 Results saved to: results/{filename}")
        
    elif choice == "3":
        print("\n📊 Generating visualizations...")
        try:
            from simple_charts import create_simple_visualizations
            create_simple_visualizations()
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Make sure you have data in the results/ directory")
        
    elif choice == "4":
        print("\n📋 Quick summary...")
        try:
            from quick_summary import quick_summary
            quick_summary()
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Make sure you have data in the results/ directory")
        
    elif choice == "5":
        print("👋 Goodbye!")
        return
        
    else:
        print("❌ Invalid choice. Please try again.")
        main()

if __name__ == "__main__":
    main()
