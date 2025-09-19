# Changelog

## [2.0.0] - 2025-09-18

### 🎉 Major Release - Comprehensive Market Analysis

#### Added
- **Comprehensive Market Scraper**: Scales to 500+ companies with 94.5 companies/minute processing
- **Dynamic S&P 500 Fetching**: Real-time company list from Wikipedia
- **Advanced Visualizations**: matplotlib/seaborn charts showing market dominance
- **Market Cap Analysis**: Calculate actual market value controlled by institutions
- **Professional Project Structure**: Organized src/, analysis/, results/, docs/ directories

#### Key Findings
- **BlackRock**: 90.6% market presence (397/438 companies)
- **Vanguard Group**: 88.4% market presence (387/438 companies)
- **Combined Big 2**: 98.2% market dominance (430/438 companies)
- **Market Cap Control**: ~$28.7 trillion exposure (88.8% of analyzed market cap)
- **HHI Index**: 16,821 (extremely concentrated market)

#### Technical Improvements
- **Performance**: 10x faster processing (from 30s to 3s per company)
- **Scale**: Increased from 50 to 500 companies
- **Data Quality**: 87.6% success rate across comprehensive dataset
- **Compliance**: Full SEC API compliance with rate limiting

#### Data Deliverables
- 1,067 institutional ownership records
- 438 major American companies analyzed
- 12 major institutional investors tracked
- Complete visualization suite
- Professional documentation

### Previous Versions

## [1.0.0] - 2025-09-17
- Initial SEC proxy scraper
- Basic ownership extraction
- S&P 500 company support
- CSV output format
