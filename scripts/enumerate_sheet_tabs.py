#!/usr/bin/env python3
"""
Enumerate all tabs in a Google Sheet and search for penalty data.

This script attempts to find all accessible tabs in the deprecated NIKKE sheet
and extract any CP deficit/stat penalty data.
"""

import requests
import csv
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

DEPRECATED_SHEET_ID = "1cbMB9KQeAvL_PDT8t29ipRWB5UnfkKguVElad_DUB4s"


def extract_tab_data(sheet_id: str, gid: int) -> Optional[Tuple[List[List[str]], str]]:
    """
    Extract data from a specific tab.
    
    Returns:
        Tuple of (rows, preview_text) or None if failed
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text.strip()
            if content and len(content) > 50:
                reader = csv.reader(content.splitlines())
                rows = list(reader)
                if rows:
                    # Create preview from first few rows
                    preview = ' | '.join(str(cell)[:20] for cell in rows[0][:5])
                    return (rows, preview)
    except Exception as e:
        pass
    
    return None


def search_for_keywords(rows: List[List[str]], keywords: List[str]) -> bool:
    """Check if any row contains the keywords."""
    for row in rows[:20]:  # Check first 20 rows
        row_text = ' '.join(str(cell).lower() for cell in row)
        if any(keyword.lower() in row_text for keyword in keywords):
            return True
    return False


def extract_penalty_data(rows: List[List[str]]) -> Optional[List[Dict[str, float]]]:
    """Extract CP deficit and stat penalty data from rows."""
    if not rows or len(rows) < 2:
        return None
    
    # Find header row
    header_idx = None
    deficit_col = None
    penalty_col = None
    
    for i, row in enumerate(rows[:15]):
        row_lower = [str(cell).lower() for cell in row]
        row_text = ' '.join(row_lower)
        
        # Look for header with both deficit and penalty
        if 'deficit' in row_text or 'penalty' in row_text:
            # Find column indices
            for j, cell in enumerate(row):
                cell_lower = str(cell).lower()
                if ('deficit' in cell_lower or ('cp' in cell_lower and 'deficit' in cell_lower)) and deficit_col is None:
                    deficit_col = j
                if ('penalty' in cell_lower or ('stat' in cell_lower and 'penalty' in cell_lower)) and penalty_col is None:
                    penalty_col = j
            
            if deficit_col is not None and penalty_col is not None:
                header_idx = i
                break
    
    if header_idx is None or deficit_col is None or penalty_col is None:
        return None
    
    # Extract data
    data = []
    for row in rows[header_idx + 1:]:
        if len(row) > max(deficit_col, penalty_col):
            try:
                # Clean and parse deficit
                deficit_str = str(row[deficit_col]).replace('%', '').replace(',', '').strip()
                penalty_str = str(row[penalty_col]).replace('%', '').replace(',', '').strip()
                
                if deficit_str and penalty_str:
                    deficit = float(deficit_str)
                    penalty = float(penalty_str)
                    
                    # Validate ranges
                    if 0 <= deficit <= 100 and 0 <= penalty <= 100:
                        data.append({
                            'cp_deficit_percent': deficit,
                            'stat_penalty_percent': penalty
                        })
            except (ValueError, IndexError):
                continue
    
    return data if data else None


def main():
    """Enumerate tabs and search for penalty data."""
    print("=" * 70)
    print("NIKKE Sheet Tab Enumeration & Penalty Data Search")
    print("=" * 70)
    print()
    print(f"Sheet ID: {DEPRECATED_SHEET_ID}")
    print()
    
    # Try a wide range of gid values
    # Google Sheets gids are often sequential or follow patterns
    gids_to_try = list(range(0, 50))  # Sequential
    gids_to_try.extend([100, 200, 300, 500, 1000])  # Common patterns
    gids_to_try.extend([1021372150, 1167646947])  # Known gids
    
    found_tabs = []
    penalty_data_found = []
    
    print("Scanning for accessible tabs...")
    print()
    
    for gid in gids_to_try:
        result = extract_tab_data(DEPRECATED_SHEET_ID, gid)
        if result:
            rows, preview = result
            
            # Check if it might be penalty-related
            is_penalty_related = search_for_keywords(rows, [
                'penalty', 'deficit', 'stage', 'cp', 'stat', 'combat power'
            ])
            
            status = "⚠️  Penalty-related" if is_penalty_related else "✓"
            print(f"{status} gid={gid:10d} | Rows: {len(rows):3d} | Preview: {preview[:60]}...")
            
            found_tabs.append((gid, rows, is_penalty_related))
            
            # Try to extract penalty data
            if is_penalty_related:
                penalty_data = extract_penalty_data(rows)
                if penalty_data:
                    print(f"  → Found {len(penalty_data)} penalty data points!")
                    penalty_data_found.extend(penalty_data)
    
    print()
    print("=" * 70)
    print(f"Summary: Found {len(found_tabs)} accessible tabs")
    print(f"         Found {len(penalty_data_found)} penalty data points")
    print("=" * 70)
    print()
    
    # Save results
    if penalty_data_found:
        output_dir = Path(__file__).parent.parent / "data"
        output_dir.mkdir(exist_ok=True)
        
        # Remove duplicates
        unique_data = []
        seen = set()
        for item in penalty_data_found:
            key = (item['cp_deficit_percent'], item['stat_penalty_percent'])
            if key not in seen:
                seen.add(key)
                unique_data.append(item)
        
        # Sort by deficit
        unique_data.sort(key=lambda x: x['cp_deficit_percent'])
        
        # Save CSV
        csv_file = output_dir / "cp_deficit_stat_penalty_raw.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['cp_deficit_percent', 'stat_penalty_percent'])
            writer.writeheader()
            writer.writerows(unique_data)
        
        print(f"✓ Saved {len(unique_data)} unique data points to:")
        print(f"  {csv_file}")
        print()
        
        # Save JSON
        json_file = output_dir / "cp_deficit_stat_penalty_raw.json"
        with open(json_file, 'w') as f:
            json.dump(unique_data, f, indent=2)
        
        print(f"✓ Also saved as JSON to:")
        print(f"  {json_file}")
    else:
        print("✗ No penalty data found in accessible tabs")
        print()
        print("The penalty data may be in:")
        print("1. A tab with a different gid (not in scanned range)")
        print("2. The deleted sheet (1PaPU07AAZvECsSQeOhzMxue3q-sYXiKWclT3geaDJAM)")
        print("3. A private/restricted tab")
        print()
        print("Next steps:")
        print("- Check Google Drive Trash for the deleted sheet")
        print("- Try Wayback Machine: https://web.archive.org/web/*/docs.google.com/spreadsheets/d/1PaPU07AAZvECsSQeOhzMxue3q-sYXiKWclT3geaDJAM")
        print("- Contact collaborators or community for data")
        print("- Reconstruct through in-game testing")
    
    print()


if __name__ == "__main__":
    main()

