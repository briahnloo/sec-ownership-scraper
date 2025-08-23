#!/usr/bin/env python3
import time
import re
import json
import pathlib
import random
from typing import List, Dict, Optional, Tuple
import requests
import pandas as pd
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import warnings
import sys
import os

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="bs4")
warnings.filterwarnings("ignore", category=pd.errors.ParserWarning)

# ----------------------------
# Enhanced Config
# ----------------------------
DATA_DIR = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)

SEC_API_BASE = "https://data.sec.gov"
SEC_FILES_BASE = "https://www.sec.gov"

HEADERS = {
    "User-Agent": "OwnershipResearch/1.0 (your_email@example.com)",
    "Accept-Encoding": "gzip, deflate",
}

DEBUG = True
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5
TIMEOUT = 60

def _sleep(min_s=0.7, max_s=1.5):
    time.sleep(random.uniform(min_s, max_s))

def get_response(
    url: str, 
    headers: Optional[dict] = None, 
    retries: int = MAX_RETRIES, 
    backoff: float = BACKOFF_FACTOR, 
    timeout: int = TIMEOUT
) -> requests.Response:
    headers = headers or HEADERS
    for i in range(retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except (requests.RequestException, requests.HTTPError) as e:
            if i < retries:
                sleep_time = backoff * (2 ** i)
                if DEBUG: 
                    print(f"[retry] {url} - attempt {i+1}/{retries} in {sleep_time:.1f}s")
                time.sleep(sleep_time)
            else:
                if DEBUG:
                    print(f"[error] Failed after {retries} retries: {str(e)[:100]}")
                raise
    raise RuntimeError(f"Unexpected error with {url}")

def get_json(url: str, headers: Optional[dict] = None, retries: int = 3, backoff: float = 1.0, timeout: int = 30):
    r = get_response(url, headers, retries, backoff, timeout)
    try:
        return r.json()
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON response from {url}")

# ----------------------------
# 1) Universe: S&P 500 tickers
# ----------------------------
def get_sp500_tickers() -> pd.DataFrame:
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    
    try:
        tables = pd.read_html(r.text, flavor="lxml")
    except Exception:
        tables = pd.read_html(r.text)

    df = tables[0]
    df.rename(columns={"Symbol": "ticker"}, inplace=True)
    df["ticker"] = df["ticker"].str.replace(".", "-", regex=False).str.strip()
    return df[["ticker", "Security", "GICS Sector"]]

# ---------------------------------------
# 2) Map tickers -> CIK via SEC JSON
# ---------------------------------------
def get_ticker_cik_map() -> Dict[str, str]:
    primary = f"{SEC_FILES_BASE}/files/company_tickers.json"
    try:
        data = get_json(primary, retries=2)
        out = {}
        for _, rec in data.items():
            t = rec["ticker"].upper().strip()
            cik10 = str(rec["cik_str"]).zfill(10)
            out[t] = cik10
        if out:
            return out
    except Exception as e:
        if DEBUG: print(f"[warn] Primary CIK map failed: {e}")

    fallback = f"{SEC_FILES_BASE}/files/company_tickers_exchange.json"
    try:
        data = get_json(fallback, retries=2)
        out = {}
        for rec in data:
            t = rec["ticker"].upper().strip()
            cik10 = str(rec.get("cik") or rec.get("cik_str")).zfill(10)
            out[t] = cik10
        return out
    except Exception as e:
        if DEBUG: print(f"[warn] Fallback CIK map failed: {e}")
        return {}

# --------------------------------------------------
# 3) SEC submissions: find latest DEF 14A per CIK
# --------------------------------------------------
def get_company_submissions(cik10: str) -> dict:
    url = f"{SEC_API_BASE}/submissions/CIK{cik10}.json"
    return get_json(url, retries=2, backoff=1.5)

def get_primary_document_from_submissions(subs: dict, accession_nodash: str) -> str:
    filings = subs.get("filings", {}).get("recent", {})
    accessions = filings.get("accessionNumber", [])
    primary_docs = filings.get("primaryDocument", [])
    
    for i, acc in enumerate(accessions):
        if acc.replace("-", "") == accession_nodash:
            return primary_docs[i] if i < len(primary_docs) else ""
    return ""

def find_latest_def14a(subs: dict) -> Optional[Tuple[str, str, str]]:
    filings = subs.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])
    filing_dates = filings.get("filingDate", [])
    accessions = filings.get("accessionNumber", [])
    primary_docs = filings.get("primaryDocument", [])

    latest_idx = None
    latest_date = None
    for i, form in enumerate(forms):
        if str(form).strip().upper() in ["DEF 14A", "DEF 14"]:
            d = filing_dates[i]
            if (latest_date is None) or (d > latest_date):
                latest_date = d
                latest_idx = i

    if latest_idx is None:
        return None

    acc_no_dash = accessions[latest_idx].replace("-", "")
    primary_doc = primary_docs[latest_idx] if latest_idx < len(primary_docs) else ""
    return filing_dates[latest_idx], acc_no_dash, primary_doc

# -----------------------------------------------------
# 4) Enhanced Proxy Parsing
# -----------------------------------------------------
def clean_holder_name(name: str) -> str:
    if not isinstance(name, str):
        return name
    n = re.sub(r"\s+", " ", name).strip()
    aliases = {
        r"\bthe vanguard group.*": "Vanguard Group",
        r"\bblackrock,? inc\.?": "BlackRock",
        r"\bstate street.*": "State Street",
        r"\bfidelity(?: management .*?)?": "Fidelity",
        r"\bt\.? rowe price.*": "T. Rowe Price",
        r"\bberkshire hathaway.*": "Berkshire Hathaway",
    }
    lower = n.lower()
    for pat, repl in aliases.items():
        if re.search(pat, lower):
            return repl
    return n

def extract_percent(value):
    if pd.isna(value):
        return None
    s = str(value)
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", s)
    if m:
        return float(m.group(1))
    try:
        return float(s)
    except Exception:
        return None

def detect_content_type(content: str) -> str:
    """Detect actual content format regardless of headers"""
    if re.search(r"<!DOCTYPE html|</html>", content, re.I):
        return "html"
    elif re.search(r"<\?xml|</[a-zA-Z]+>", content):
        return "xml"
    return "text"

def detect_ownership_columns(df: pd.DataFrame) -> dict:
    """Robust column identification using multiple heuristics"""
    col_mapping = {}
    for i, col in enumerate(df.columns):
        col_text = str(col).lower()
        
        # Name detection
        if not col_mapping.get('name') and any(k in col_text for k in ["name", "beneficial", "holder", "shareholder"]):
            col_mapping['name'] = i
        
        # Percent detection
        if not col_mapping.get('percent') and any(k in col_text for k in ["%", "percent", "percentage"]):
            col_mapping['percent'] = i
            
        # Shares detection
        if not col_mapping.get('shares') and any(k in col_text for k in ["share", "security", "amount", "number"]):
            col_mapping['shares'] = i
            
    return col_mapping

def process_ownership_table(df: pd.DataFrame) -> pd.DataFrame:
    """Process detected ownership table"""
    # Normalize columns
    df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]
    
    # Detect columns
    col_map = detect_ownership_columns(df)
    
    out = pd.DataFrame()
    out["holder_raw"] = df.iloc[:, col_map['name']].astype(str) if 'name' in col_map else df.iloc[:, 0].astype(str)
    out["holder"] = out["holder_raw"].map(clean_holder_name)

    # Process percentage column
    if 'percent' in col_map:
        out["percent_class"] = df.iloc[:, col_map['percent']].map(extract_percent)
    else:
        out["percent_class"] = None

    # Process shares column
    if 'shares' in col_map:
        def to_int(x):
            if pd.isna(x): return None
            s = re.sub(r"[^\d]", "", str(x))
            return int(s) if s.isdigit() else None
        out["shares"] = df.iloc[:, col_map['shares']].map(to_int)
    else:
        out["shares"] = None

    # Clean rows
    out = out[~out["holder"].str.contains("total", case=False, na=False)]
    out = out[out["holder"].str.len() > 1].reset_index(drop=True)
    return out

def find_ownership_table_in_html(html: str) -> Optional[pd.DataFrame]:
    """Find ownership table by section headers in HTML"""
    soup = BeautifulSoup(html, "lxml")
    
    # Find ownership sections by header text
    ownership_headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'div', 'span'], 
        string=re.compile(r'security own|beneficial own|stock own|ownership|shareholdings', re.I))
    
    # Also look for specific section IDs
    section_ids = ["securityOwnership", "beneficialOwnership", "stockOwnership"]
    for section_id in section_ids:
        section = soup.find(id=section_id)
        if section:
            ownership_headers.append(section)
    
    for header in ownership_headers:
        # Expand search area
        section = header
        for _ in range(3):  # Look through parent elements
            section = section.parent if section else None
            if not section:
                break
            
            tables = section.find_all('table')
            for table in tables:
                try:
                    df = pd.read_html(str(table))[0]
                    processed = process_ownership_table(df)
                    if not processed.empty:
                        return processed
                except Exception as e:
                    if DEBUG: print(f"[parse] Table parse error: {str(e)[:50]}")
                    continue
    return None

def find_ownership_table_in_xml(xml: str) -> Optional[pd.DataFrame]:
    """Find ownership table in XML filings"""
    try:
        soup = BeautifulSoup(xml, "lxml-xml")
        
        # Look for specific XML sections
        section_tags = ["ownship", "securityOwnership", "beneficialOwnership"]
        for tag in section_tags:
            section = soup.find(tag)
            if section:
                tables = section.find_all('table')
                for table in tables:
                    try:
                        df = pd.read_html(str(table))[0]
                        processed = process_ownership_table(df)
                        if not processed.empty:
                            return processed
                    except Exception:
                        pass
        
        # Look for table with ownership keywords
        tables = soup.find_all('table')
        for table in tables:
            table_text = table.get_text().lower()
            if any(k in table_text for k in ["security own", "beneficial own", "stock own", "ownership"]):
                try:
                    df = pd.read_html(str(table))[0]
                    processed = process_ownership_table(df)
                    if not processed.empty:
                        return processed
                except Exception:
                    pass
                    
        return None
    except Exception as e:
        if DEBUG: print(f"[parse] XML parse error: {str(e)[:100]}")
        return None

def extract_from_text(content: str) -> Optional[pd.DataFrame]:
    """Manual extraction for text-based ownership sections"""
    # Look for ownership section
    section_pattern = r"(Security Ownership|Beneficial Ownership).*?\n(.*?)\n\n"
    match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)
    if not match:
        return None
        
    section_text = match.group(0)
    
    # Find table-like data
    rows = []
    row_pattern = r"(\w[\w\s,.]+?)\s+(\d{1,3}(?:,\d{3})*\s+)?(\d+\.\d+%|\d+%)"
    matches = re.findall(row_pattern, section_text)
    
    for match in matches:
        holder = match[0].strip()
        shares = match[1].replace(",", "").strip() if match[1] else None
        percent = match[2].replace("%", "").strip()
        
        if not holder or "total" in holder.lower():
            continue
            
        rows.append({
            "holder_raw": holder,
            "holder": clean_holder_name(holder),
            "shares": int(shares) if shares else None,
            "percent_class": float(percent)
        })
    
    if not rows:
        return None
        
    return pd.DataFrame(rows)

def parse_proxy_content(content: str) -> Optional[pd.DataFrame]:
    """Master parser that tries multiple strategies"""
    # Strategy 1: Try direct table parsing
    try:
        tables = pd.read_html(content)
        for table in tables:
            processed = process_ownership_table(table)
            if not processed.empty:
                return processed
    except Exception:
        pass
        
    # Detect actual content type
    content_type = detect_content_type(content)
    
    # Strategy 2: Format-specific parsing
    if content_type == "html":
        result = find_ownership_table_in_html(content)
        if result is not None:
            return result
    elif content_type == "xml":
        result = find_ownership_table_in_xml(content)
        if result is not None:
            return result
    
    # Strategy 3: Text-based extraction
    return extract_from_text(content)

# ------------------------------------------------------------
# 5) Driver: loop S&P 500, pull DEF 14A, parse ownership
# ------------------------------------------------------------
def fetch_ownership_for_sp500(limit: Optional[int] = 5) -> pd.DataFrame:
    spx = get_sp500_tickers()
    tick2cik = get_ticker_cik_map()

    rows = []
    processed = 0
    for _, row in spx.iterrows():
        if processed >= limit:
            break
            
        ticker = row["ticker"].upper()
        security = row["Security"]
        sector = row["GICS Sector"]

        cik = tick2cik.get(ticker)
        if not cik:
            if DEBUG: print(f"[skip] No CIK for {ticker}")
            continue

        try:
            _sleep()
            if DEBUG: print(f"\n[info] Processing {ticker} (CIK: {cik})")
            
            # Get company submissions
            subs = get_company_submissions(cik)
            found = find_latest_def14a(subs)
            if not found:
                if DEBUG: print(f"[skip] No DEF 14A for {ticker}")
                continue

            filing_date, acc_nodash, primary_doc = found
            if not primary_doc:
                if DEBUG: print(f"[skip] No primary doc for {ticker}")
                continue
                
            url = f"{SEC_FILES_BASE}/Archives/edgar/data/{int(cik)}/{acc_nodash}/{primary_doc}"
            if DEBUG: print(f"[doc] Filing URL: {url}")

            # Fetch document
            try:
                response = get_response(url)
                content = response.text
                if DEBUG: 
                    print(f"[downloaded] {len(content)} bytes")
            except Exception as e:
                if DEBUG: print(f"[error] Download failed: {e}")
                continue

            # Parse ownership table
            df = parse_proxy_content(content)
            if df is None or df.empty:
                if DEBUG: print(f"[skip] No ownership table parsed for {ticker}")
                # Save for debugging
                debug_path = DATA_DIR / f"{ticker}_proxy.html"
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(content)
                if DEBUG: print(f"[debug] Saved HTML to {debug_path}")
                continue

            df["ticker"] = ticker
            df["company"] = security
            df["sector"] = sector
            df["filing_date"] = filing_date
            df["filing_url"] = url
            rows.append(df)
            if DEBUG: print(f"[success] Parsed {len(df)} holders for {ticker}")
            processed += 1
            
        except Exception as e:
            print(f"[error] {ticker}: {str(e)[:100]}")
            continue

    if not rows:
        print("[info] No rows parsed; nothing to save.")
        return pd.DataFrame(columns=["ticker","company","holder","percent_class","shares","filing_date","filing_url","sector"])

    combined = pd.concat(rows, ignore_index=True)
    if "percent_class" in combined.columns:
        combined["percent_class"] = combined["percent_class"].apply(
            lambda x: x if (pd.notna(x) and 0 <= x <= 100) else None
        )

    return combined

if __name__ == "__main__":
    print("Starting ownership data collection...")
    try:
        df = fetch_ownership_for_sp500(limit=5)
        if df.empty:
            print("\nNo data collected. Check debug output for issues.")
        else:
            print("\nPreview of collected data:")
            with pd.option_context('display.max_columns', None, 'display.width', 160):
                print(df.head(20))
            print(f"\nTotal rows collected: {len(df)}")
            
            out_path = (DATA_DIR / "ownership_sp500.csv").resolve()
            df.to_csv(out_path, index=False)
            print(f"Saved: {out_path}")
            
            # Big 4 analysis
            big4 = ["Vanguard Group", "BlackRock", "State Street", "Fidelity"]
            big4_df = df[df["holder"].isin(big4)]
            
            if not big4_df.empty:
                print("\nBig 4 Ownership Summary:")
                summary = big4_df.groupby(["ticker", "company", "holder"])["percent_class"].sum().unstack()
                print(summary.head(10))
            else:
                print("\nNo Big 4 ownership data found in collected sample.")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting gracefully.")
        sys.exit(0)
    except Exception as e:
        print(f"\nCritical error: {str(e)}")
        print("Script terminated unexpectedly. Check debug logs.")
        sys.exit(1)