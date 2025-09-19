# Comprehensive SEC Ownership Data Scraper

A comprehensive system for collecting, analyzing, and monitoring ownership concentration in publicly traded companies using SEC filings.

## Overview

This project scrapes ownership data from various SEC filings to analyze market concentration and institutional investor influence across public companies. It provides insights into how much of the available stock market is owned by major institutional investors.

## Features

### 🏢 **Multi-Filing Type Support**
- **DEF 14A** (Proxy Statements): Board and executive ownership
- **13F-HR** (Institutional Holdings): Quarterly institutional positions 
- **SC 13D/13G** (Beneficial Ownership): >5% ownership disclosures
- **10-K/10-Q** (Annual/Quarterly Reports): Ownership sections

### 📊 **Market Coverage**
- S&P 500 companies (expandable to other indices)
- Russell 1000/2000 support (configurable)
- NASDAQ 100 support (configurable)

### 🔍 **Advanced Analytics**
- **Concentration Metrics**: Herfindahl-Hirschman Index (HHI)
- **Top N Analysis**: Top 1, 3, 5, 10 shareholder concentration
- **Big 4 Tracking**: Vanguard, BlackRock, State Street, Fidelity
- **Cross-ownership Networks**: Identify interconnected holdings

### ⚖️ **SEC Compliance**
- Built-in rate limiting (10 req/sec, 100k/day)
- Request logging and monitoring
- Proper User-Agent headers
- Compliance reporting dashboard

### 🛡️ **Data Quality**
- Comprehensive validation rules
- Entity name normalization
- Outlier detection
- Data completeness scoring

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd sec_scraper_project
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure settings:**
Edit `config.py` and update the User-Agent header with your contact information:
```python
HEADERS = {
    "User-Agent": "YourApp/1.0 (your_email@yourcompany.com)",
    # ...
}
```

## Quick Start

### 1. Collect Data
```bash
# Collect proxy statement data for 10 S&P 500 companies
python main_runner.py collect --max-companies 10 --export

# Collect multiple filing types
python main_runner.py collect --filing-types "DEF 14A,13F-HR" --max-companies 5
```

### 2. Validate Data Quality
```bash
# Run comprehensive data validation
python main_runner.py validate --export
```

### 3. Analyze Ownership
```bash
# Generate ownership concentration analysis
python main_runner.py analyze --export
```

### 4. Monitor Compliance
```bash
# Check SEC API compliance status
python main_runner.py compliance --days 7
```

## Usage Examples

### Basic Collection
```python
from comprehensive_scraper import ComprehensiveOwnershipScraper

scraper = ComprehensiveOwnershipScraper()
scraper.run_comprehensive_collection(
    indices=['SP500'],
    filing_types=['DEF 14A'],
    max_companies=20,
    max_workers=2
)
```

### Advanced Analysis
```python
from database import OwnershipDatabase

db = OwnershipDatabase()

# Get Big 4 ownership analysis
big4_data = db.get_big4_analysis()
print(f"Big 4 control {big4_data['total_percent'].sum():.1f}% of analyzed companies")

# Calculate concentration metrics
metrics = db.calculate_concentration_metrics('AAPL')
print(f"AAPL HHI: {metrics['hhi']}")
```

### Custom Validation
```python
from data_validator import OwnershipDataValidator

validator = OwnershipDataValidator()
ownership_data = db.get_ownership_summary()

report = validator.generate_data_quality_report(ownership_data)
print(f"Data completeness: {report['validation_results']['market']['metrics']['overall_data_completeness']:.1f}%")
```

## Database Schema

The system uses SQLite with the following key tables:

- **companies**: Company information (ticker, CIK, sector)
- **holders**: Institutional investor details with normalized names
- **filings**: SEC filing metadata and processing status
- **ownership**: Ownership positions with shares/percentages
- **concentration_metrics**: Calculated concentration measures
- **request_log**: API compliance monitoring

## Configuration

Key configuration options in `config.py`:

```python
# Rate limiting
MAX_REQUESTS_PER_SECOND = 10
MAX_REQUESTS_PER_DAY = 100000

# Filing types to process
FILING_TYPES = {
    'DEF 14A': {'priority': 1, 'frequency': 'annual'},
    '13F-HR': {'priority': 2, 'frequency': 'quarterly'},
    # ...
}

# Institutional investor aliases
INSTITUTIONAL_ALIASES = {
    'Vanguard Group': ['The Vanguard Group, Inc.', ...],
    'BlackRock': ['BlackRock, Inc.', ...],
    # ...
}
```

## Legal Compliance

### SEC Guidelines
- ✅ **Public Data Only**: All data sourced from public SEC filings
- ✅ **Rate Limiting**: Respects SEC API guidelines (10 req/sec)
- ✅ **Proper Attribution**: Includes contact information in User-Agent
- ✅ **Request Logging**: Maintains audit trail of all API calls

### Data Usage
- **Research/Educational Use**: Designed for academic and analytical purposes
- **No Market Manipulation**: Does not provide trading signals or advice
- **Attribution Required**: Proper citation of SEC data sources
- **Privacy Compliant**: Only processes publicly available information

### Regulatory Considerations
- **Fair Disclosure (Reg FD)**: Only uses public information
- **Section 13(f)**: Processes institutional holdings reports
- **Beneficial Ownership Rules**: Handles 13D/13G disclosures appropriately

## Output Data

### CSV Exports
- `ownership_summary.csv`: Complete ownership dataset
- `big4_analysis.csv`: Big 4 institutional investor positions
- `concentration_metrics.csv`: Market concentration measures
- `companies.csv`: Company master list
- `holders.csv`: Institutional investor directory

### JSON Reports
- `validation_report_YYYYMMDD.json`: Data quality assessment
- `analysis_YYYYMMDD.json`: Ownership concentration analysis
- `compliance_YYYYMMDD.json`: SEC compliance monitoring

## Key Insights Available

### Market Structure Analysis
- **Institutional Dominance**: How much of each company is owned by institutions
- **Cross-Holdings**: Which institutions hold similar portfolios
- **Concentration Trends**: Are markets becoming more or less concentrated?

### Big 4 Analysis
- **Market Share**: Percentage of total market controlled by Vanguard, BlackRock, State Street, Fidelity
- **Voting Power**: Potential influence on corporate governance
- **Sector Concentration**: Which sectors have highest institutional ownership

### Risk Assessment
- **Systemic Risk**: Identify companies with extremely concentrated ownership
- **Liquidity Risk**: Companies with low free float due to institutional holdings
- **Governance Risk**: Excessive concentration that might limit shareholder democracy

## Performance & Scalability

### Current Capacity
- **S&P 500**: ~2-3 hours for complete proxy statement collection
- **Database Size**: ~100MB for full S&P 500 dataset
- **Rate Limits**: 10 requests/second, 100k requests/day

### Optimization Features
- **Multi-threading**: Parallel processing of multiple companies
- **Caching**: Avoids re-downloading processed filings
- **Incremental Updates**: Only processes new/updated filings
- **Data Validation**: Identifies and flags quality issues

## Troubleshooting

### Common Issues

1. **Rate Limiting Errors**
```bash
# Check compliance status
python main_runner.py compliance

# Wait for rate limit reset or reduce workers
python main_runner.py collect --workers 1
```

2. **Parsing Failures**
```bash
# Run validation to identify issues
python main_runner.py validate

# Check debug files in data/ directory
ls data/*_proxy.html
```

3. **Database Errors**
```bash
# Check database integrity
sqlite3 data/ownership.db "PRAGMA integrity_check;"

# Reset database if corrupted
rm data/ownership.db
python main_runner.py collect --max-companies 1
```

### Debug Mode
```bash
# Enable verbose logging
python main_runner.py collect --verbose

# Check log files
tail -f logs/scraper.log
```

## Contributing

1. **Entity Resolution**: Add new institutional investor aliases
2. **Filing Parsers**: Improve parsing for specific filing formats  
3. **Analysis Metrics**: Add new concentration/risk measures
4. **Market Coverage**: Extend to international markets
5. **Visualization**: Create dashboards and charts

## Roadmap

### Phase 1 (Current)
- [x] Multi-filing type support
- [x] Database architecture
- [x] SEC compliance monitoring
- [x] Data validation framework

### Phase 2 (Next 3 months)
- [ ] Real-time ownership change alerts
- [ ] Web dashboard interface
- [ ] International market expansion
- [ ] Advanced network analysis

### Phase 3 (6+ months)
- [ ] Machine learning for entity resolution
- [ ] Predictive ownership modeling
- [ ] Academic research partnerships
- [ ] Public API for researchers

## License

This project is intended for educational and research purposes. Users must comply with SEC terms of service and applicable securities regulations.

## Disclaimer

This software is provided for informational and educational purposes only. It does not constitute investment advice, and users should not make investment decisions based solely on this data. Always consult with qualified financial professionals before making investment decisions.

---

**Contact**: Update the User-Agent in `config.py` with your contact information before use.
**SEC Data**: All data sourced from public SEC filings via EDGAR database.
**Last Updated**: September 2025
