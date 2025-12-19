# Qualys Asset Duplicate Detection

This Python script analyzes all host assets in your Qualys subscription and identifies **potential duplicate assets** based on several common fields such as asset name, DNS name, MAC address, NetBIOS name, and IPv4 address.

It connects to the Qualys Gateway API using JWT authentication, retrieves all assets using paginated API calls, and analyzes them for duplicates. The script generates both an **Excel spreadsheet** and an **interactive HTML report** for easy review and sharing.

---

## How It Works

1. **Platform Selection** - Choose from all public Qualys platforms (US1-4, UK, EU1-3, IN, CA, AE, AU, KSA)
2. **Authentication** - Secure login using JWT token
3. **Asset Retrieval** - Fetches all assets with pagination support (300 per page)
4. **Progress Tracking** - Auto-saves progress every page, resume on interruption (Ctrl+C)
5. **Duplicate Detection** - Analyzes Asset Name, DNS Name, NetBIOS Name, MAC Address, and IPv4 Address
6. **Report Generation** - Creates Excel and HTML reports with timestamped filenames
7. **Session Cleanup** - Invalidates JWT token upon completion

---

## Requirements

- Python 3.6 or higher
- Dependencies: `requests`, `openpyxl`

**Installation:**
```bash
pip install requests openpyxl
```

Or if using `pip3`:
```bash
pip3 install requests openpyxl
```

**Account Requirements:**
- API access enabled
- MFA disabled
- Asset Management read permissions

---

## Usage

### Basic Usage (Interactive Mode)
```bash
python3 duplicate_finder-v1.7.py
```

Follow the prompts to:
1. Select your Qualys platform (US1, EU2, UK, IN, etc.)
2. Enter username and password

### Command-Line Arguments
```bash
python3 duplicate_finder-v1.7.py --platform US1 --username user@example.com
python3 duplicate_finder-v1.7.py --platform EU1 --username admin --password mypassword
python3 duplicate_finder-v1.7.py --platform US1 --username user@example.com --include-easm --save-json
```

**Available Arguments:**
- `--help` - Show help message and exit
- `--platform <PLATFORM>` - Qualys platform (US1, US2, US3, US4, UK, EU1, EU2, EU3, IN, CA, AE, AU, KSA)
- `--username <USERNAME>` - Qualys username
- `--password <PASSWORD>` - Qualys password (will prompt if not provided)
- `--include-easm` - Include EASM assets in duplicate checking (default: excluded)
- `--save-json` - Save filtered asset data to JSON file (default: disabled)

### Progress Saving & Resume

**Interrupt at any time:** Press `Ctrl+C` during asset fetch to pause and save progress.

**Resume session:** Run the script again with the same platform and username, then choose "yes" when prompted to resume.

**Auto-save:** Progress automatically saved after every API call (every 300 assets).

**Stale detection:** Progress files older than 24 hours are automatically discarded.

---

## Output

### **Excel Report** (`duplicate_assets_<PLATFORM>_<USERNAME>_YYYYMMDD_HHMMSS.xlsx`)
- [View sample Excel report](sample_duplicate_assets_20250101_120000.xlsx)
- Frozen headers
- Color-coded duplicate groups (alternating blue/peach)
- Columns: Asset ID, Address, DNS Name, Asset Name, Source, Last Activity
- Auto-sized columns with 50-character cap
- Sanitized cell values (illegal character removal)

### **HTML Report** (`duplicate_assets_<PLATFORM>_<USERNAME>_YYYYMMDD_HHMMSS.html`)
- [View sample HTML report](sample_duplicate_assets_20250101_120000.html)
- Summary dashboard with metrics (total assets, duplicates, percentage)
- Real-time search across all columns
- Sortable columns (click headers to sort)
- Resizable columns (drag column edges)
- Reset sort button
- Print-friendly layout
- Color-coded duplicate groups

### **Progress File** (`duplicate_finder_progress_<PLATFORM>_<USERNAME>.json`)
- Automatically created during fetch
- Deleted upon successful completion
- Lightweight format (essential fields only)
- Resume capability for interrupted sessions

### **Optional JSON Export** (`asset_data_<PLATFORM>_<USERNAME>_YYYYMMDD_HHMMSS.json`)
- Raw asset data in JSON format
- Enabled via `--save-json` argument or `SAVE_JSON_OUTPUT = True` in script
- Contains essential fields only (assetId, assetName, dnsName, netbiosName, macAddress, address, inventoryListData)

---

## Duplicate Detection Logic

Assets sharing the same normalized value in any field are grouped as duplicates:
- Asset Name, DNS Name, NetBIOS Name, MAC Address (case-insensitive, trimmed)
- IPv4 Address (case-sensitive, trimmed)

**Tracking:** Duplicate pairs are only reported once across all fields to prevent redundant alerts.

**Coloring:** Each duplicate group gets alternating colors (blue/peach) for easy visual identification.

**EASM Filtering:** By default, EASM (External Attack Surface Management) assets are excluded from duplicate detection. Use `--include-easm` to include them.

**Read-Only:** The script does not modify any assets.

---

## Configuration Options

Edit these variables at the top of the script (lines 36-38) to change defaults:

```python
INCLUDE_EASM_ASSETS = False  # Change to True to include EASM assets by default
SAVE_JSON_OUTPUT = False     # Change to True to save asset data to JSON file
```

Alternatively, use the command-line arguments shown above to override these defaults.

---

## Supported Qualys Platforms

| Platform Code | Region | Gateway URL |
|---------------|--------|-------------|
| US1 | United States | gateway.qg1.apps.qualys.com |
| US2 | United States | gateway.qg2.apps.qualys.com |
| US3 | United States | gateway.qg3.apps.qualys.com |
| US4 | United States | gateway.qg4.apps.qualys.com |
| UK | United Kingdom | gateway.qg1.apps.qualys.co.uk |
| EU1 | Europe | gateway.qg1.apps.qualys.eu |
| EU2 | Europe | gateway.qg2.apps.qualys.eu |
| EU3 | Europe (Italy) | gateway.qg3.apps.qualys.it |
| IN | India | gateway.qg1.apps.qualys.in |
| CA | Canada | gateway.qg1.apps.qualys.ca |
| AE | United Arab Emirates | gateway.qg1.apps.qualys.ae |
| AU | Australia | gateway.qg1.apps.qualys.com.au |
| KSA | Kingdom of Saudi Arabia | gateway.qg1.apps.qualysksa.com |

---

## Error Handling & Recovery

### Rate Limiting (HTTP 429)
When Qualys API rate limit is reached (300 calls/hour):
1. Script automatically saves progress
2. Displays instructions to resume after rate limit resets
3. Run script again and choose "yes" to resume

### Network Timeouts
- 60-second timeout on all API calls
- Automatic progress save on timeout
- Resume from last successful page

### Interrupted Sessions (Ctrl+C)
- Graceful shutdown with progress save
- Run script again to resume from last checkpoint
- No data loss

### Invalid Asset IDs
- Automatic validation and filtering
- Skips assets with non-numeric or empty IDs
- Continues processing valid assets

### Excel Export Errors
- Permission denied detection (file open in Excel)
- Disk full or filesystem error handling
- Clear error messages with resolution steps

---

## Troubleshooting

**Authentication failed**
- Verify username/password and platform selection
- Confirm API access enabled and MFA disabled

**No assets retrieved**
- Check Asset Management read permissions
- Verify assets exist in subscription

**Module not found**
```bash
pip install requests openpyxl
```
Or:
```bash
pip3 install requests openpyxl
```

**Rate limit reached**
- Wait for rate limit window to reset (typically 1 hour)
- Resume using saved progress file

**Large datasets**
- Script handles unlimited assets via pagination
- Progress saved every 300 assets
- Can resume if interrupted
- Progress updates displayed during fetch

---

**Estimated Runtime:**
- 1,000 assets: ~1-2 minutes
- 5,000 assets: ~5-7 minutes
- 10,000 assets: ~10-15 minutes

---

## Security Notes

- Credentials entered at runtime are not stored
- JWT tokens expire after 4 hours
- Report files may contain sensitive data - handle securely
- Progress files contain asset data - secure appropriately
- Script is read-only and does not modify assets
- HTTPS connections enforced for all API calls

---

## Notes

- Manual review of duplicates recommended before taking action
- Last Activity timestamp helps identify stale assets
- EASM assets excluded by default (external-facing assets)
- Source tracking shows how assets were discovered (EC2, VMware, Agent, etc.)
- HTML report includes print-friendly CSS for documentation

---

## Version History

### **v1.7** (Current)
- Added progress saving and session resume capability
- Added command-line argument support (--platform, --username, --password, --include-easm, --save-json)
- Added EASM asset filtering (default: excluded)
- Added Last Activity timestamp tracking
- Added rate limit detection and auto-recovery (HTTP 429)
- Added graceful shutdown handling (Ctrl+C)
- Added stale progress file detection (24-hour threshold)
- Added network timeout handling (60s timeout)
- Added Excel cell value sanitization (illegal character removal)
- Added platform/username in output filenames
- Added auto-save during fetch (every page)
- Added comprehensive error handling (permissions, disk space, invalid data)
- Added asset ID validation and filtering
- Added resizable columns in HTML report
- Added reset sort functionality in HTML report
- Added print-friendly CSS styling
- Improved progress file format (lightweight, essential fields only)
- Improved column width calculation (pre-calculated from data)
- Enhanced logging and status messages throughout

### **v1.5**
- Added interactive HTML report generation
- Added Excel export with color-coded groups
- Added summary metrics (total assets, duplicates, percentage)
- Added source tracking for assets
- Enhanced terminal output formatting
- Improved duplicate pair tracking algorithm
- Added session logout functionality

### **v1.0**
- JSON export only
- Basic duplicate detection across 5 fields
- Terminal-only output

---

## Disclaimer

This script is provided as a utility for detecting potential duplicate assets within your Qualys environment.
Use at your own discretion. Always review identified duplicates manually before taking action in your Qualys subscription.

---

## Support

For issues, questions, or feature requests, please open an issue in the repository.
