#!/usr/bin/env python3
"""
Extract data from Google Sheets for CP Deficit Calculator

This script attempts to extract CP deficit and stat penalty data from:
1. The deprecated NIKKE Data Tables sheet
2. Any cached/archived versions
3. Alternative community sources
"""

import requests
import csv
import json
from pathlib import Path
from typing import List, Dict, Optional

# Deprecated sheet ID
DEPRECATED_SHEET_ID = "1cbMB9KQeAvL_PDT8t29ipRWB5UnfkKguVElad_DUB4s"

# Known sheet tab names to try
KNOWN_TABS = [
    "New Stage Penalty",
    "OLD Stage Penalty Chart",
    "Stage Penalty",
    "CP Deficit",
    "Stat Penalty",
    "Penalty Data",
]

# Common gid values (Google Sheets tab IDs)
# These are often sequential or have specific patterns
COMMON_GIDS = [
    0,  # First tab
    1021372150,  # From the URL
    1167646947,  # From the deleted sheet URL
    1000000000,  # Common pattern
    2000000000,  # Common pattern
]


def try_extract_sheet_tab(sheet_id: str, gid: int, tab_name: str = None) -> Optional[List[List[str]]]:
    """
    Try to extract data from a specific Google Sheets tab.
    
    Args:
        sheet_id: Google Sheets document ID
        gid: Tab ID (gid parameter)
        tab_name: Optional tab name for logging
        
    Returns:
        List of rows (each row is a list of strings) or None if failed
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text
            if content and len(content) > 100:  # Meaningful data
                # Parse CSV
                reader = csv.reader(content.splitlines())
                rows = list(reader)
                if len(rows) > 1:  # Has header + data
                    print(f"✓ Successfully extracted from gid={gid} ({tab_name or 'unknown tab'})")
                    print(f"  Rows: {len(rows)}, Columns: {len(rows[0]) if rows else 0}")
                    return rows
    except Exception as e:
        print(f"✗ Failed to extract gid={gid}: {e}")
    
    return None


def search_for_penalty_data(rows: List[List[str]]) -> Optional[List[Dict[str, float]]]:
    """
    Search extracted rows for CP deficit and stat penalty data.
    
    Args:
        rows: List of CSV rows
        
    Returns:
        List of dictionaries with cp_deficit_percent and stat_penalty_percent, or None
    """
    if not rows or len(rows) < 2:
        return None
    
    # Look for header row with relevant column names
    header_row = None
    header_idx = 0
    
    for i, row in enumerate(rows[:10]):  # Check first 10 rows for header
        row_lower = [str(cell).lower() for cell in row]
        if any(keyword in ' '.join(row_lower) for keyword in ['deficit', 'penalty', 'cp', 'stat']):
            header_row = row
            header_idx = i
            break
    
    if not header_row:
        return None
    
    # Find relevant columns
    deficit_col = None
    penalty_col = None
    
    for i, cell in enumerate(header_row):
        cell_lower = str(cell).lower()
        if 'deficit' in cell_lower or ('cp' in cell_lower and 'deficit' in cell_lower):
            deficit_col = i
        if 'penalty' in cell_lower or ('stat' in cell_lower and 'penalty' in cell_lower):
            penalty_col = i
    
    if deficit_col is None or penalty_col is None:
        return None
    
    # Extract data rows
    data = []
    for row in rows[header_idx + 1:]:
        if len(row) > max(deficit_col, penalty_col):
            try:
                deficit = float(str(row[deficit_col]).replace('%', '').strip())
                penalty = float(str(row[penalty_col]).replace('%', '').strip())
                data.append({
                    'cp_deficit_percent': deficit,
                    'stat_penalty_percent': penalty
                })
            except (ValueError, IndexError):
                continue
    
    return data if data else None


def main():
    """Main extraction function"""
    print("=" * 60)
    print("NIKKE CP Deficit Data Extraction")
    print("=" * 60)
    print()
    
    # Try to extract from deprecated sheet
    print("Attempting to extract from deprecated sheet...")
    print(f"Sheet ID: {DEPRECATED_SHEET_ID}")
    print()
    
    all_extracted_data = []
    
    # Try common gid values
    for gid in COMMON_GIDS:
        rows = try_extract_sheet_tab(DEPRECATED_SHEET_ID, gid)
        if rows:
            penalty_data = search_for_penalty_data(rows)
            if penalty_data:
                print(f"  Found {len(penalty_data)} data points!")
                all_extracted_data.extend(penalty_data)
            else:
                print(f"  Data found but doesn't match penalty format")
        print()
    
    # Try to find tab by name (would need Google Sheets API for this)
    print("Note: Tab name search requires Google Sheets API authentication")
    print()
    
    # Save extracted data
    if all_extracted_data:
        output_dir = Path(__file__).parent.parent / "data"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "cp_deficit_stat_penalty_raw.csv"
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['cp_deficit_percent', 'stat_penalty_percent'])
            writer.writeheader()
            writer.writerows(all_extracted_data)
        
        print(f"✓ Saved {len(all_extracted_data)} data points to:")
        print(f"  {output_file}")
        print()
        
        # Also save as JSON for easy inspection
        json_file = output_dir / "cp_deficit_stat_penalty_raw.json"
        with open(json_file, 'w') as f:
            json.dump(all_extracted_data, f, indent=2)
        
        print(f"✓ Also saved as JSON to:")
        print(f"  {json_file}")
    else:
        print("✗ No penalty data found in deprecated sheet")
        print()
        print("Next steps:")
        print("1. Check Google Drive Trash for the deleted sheet")
        print("2. Contact collaborators who may have a copy")
        print("3. Search Reddit/community for alternative sources")
        print("4. Reconstruct from game testing data")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()

