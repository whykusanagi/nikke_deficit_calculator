# Data Extraction Scripts

This directory contains scripts for extracting CP deficit and stat penalty data from Google Sheets.

## Scripts

### `extract_sheet_data.py`

Attempts to extract CP deficit and stat penalty data from the deprecated NIKKE Data Tables sheet.

**Usage**:
```bash
python3 scripts/extract_sheet_data.py
```

**What it does**:
1. Tries to extract from known gid values in the deprecated sheet
2. Searches extracted rows for penalty data format
3. Saves found data to `data/cp_deficit_stat_penalty_raw.csv`

**Dependencies**:
- `requests` (for HTTP requests)
- `csv` (standard library)
- `json` (standard library)

### `enumerate_sheet_tabs.py`

Enumerates all accessible tabs in the deprecated sheet and searches for penalty-related data.

**Usage**:
```bash
python3 scripts/enumerate_sheet_tabs.py
```

**What it does**:
1. Scans a wide range of gid values (0-50 + common patterns)
2. Extracts data from each accessible tab
3. Searches for penalty-related keywords
4. Attempts to extract penalty data if found
5. Saves results to `data/cp_deficit_stat_penalty_raw.csv`

**Dependencies**:
- `requests` (for HTTP requests)
- `csv` (standard library)
- `json` (standard library)

## Installation

Install required dependencies:

```bash
pip install requests
```

Or if using a requirements file:

```bash
pip install -r requirements.txt
```

## Output

Both scripts save extracted data to:
- `data/cp_deficit_stat_penalty_raw.csv` (CSV format)
- `data/cp_deficit_stat_penalty_raw.json` (JSON format)

## Notes

- These scripts can only access publicly accessible Google Sheets
- Private or restricted tabs will not be accessible
- The original data source (`1PaPU07AAZvECsSQeOhzMxue3q-sYXiKWclT3geaDJAM`) has been deleted and cannot be accessed
- The deprecated sheet may not contain the same data as the deleted sheet

## Troubleshooting

**No data found**:
- The penalty data may be in a tab with a different gid (not in scanned range)
- The tab may be private/restricted
- The data may only exist in the deleted sheet

**Connection errors**:
- Check internet connection
- Google Sheets may be rate-limiting requests
- Try again after a few minutes

## See Also

- [RECOVERY.md](../RECOVERY.md) - Comprehensive recovery guide
- [data/README.md](../data/README.md) - Data format specifications

