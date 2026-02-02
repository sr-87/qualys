# Qualys Tag Report Generator

This Python script generates a comprehensive report of all tags in your Qualys subscription. It retrieves detailed information for each tag including hierarchy, asset counts, tag type (Static, Dynamic, Tag Set), rule definitions, and timestamps.

The script connects to the Qualys API using both JWT and Basic authentication, retrieves all tags with pagination, and generates both an **Excel spreadsheet** and an **interactive HTML report** for easy review and sharing.

---

## How It Works

1. **Platform Selection** - Choose from all public Qualys platforms (US1-4, UK, EU1-3, IN, CA, AE, AU, KSA)
2. **Authentication** - Secure login using JWT token (Gateway API) and Basic Auth (QPS API)
3. **Tag Retrieval** - Fetches all tags with pagination support (100 per page)
4. **Detail Fetching** - Retrieves detailed information for each tag including asset counts
5. **Tag Set Resolution** - Two-pass processing to resolve tag set references to human-readable names
6. **Progress Tracking** - Auto-saves progress every 10 tags, resume on interruption (Ctrl+C)
7. **Report Generation** - Creates Excel and HTML reports with timestamped filenames
8. **Session Cleanup** - Invalidates JWT token upon completion

---

## Requirements

- Python 3.6 or higher
- Dependencies: `requests`, `openpyxl`

**Installation:**
```
pip install requests openpyxl
```

Or if using `pip3`:
```
pip3 install requests openpyxl
```

**Account Requirements:**
- API access enabled
- MFA disabled
- Permission to read Tags from Global AssetView (GAV) or CyberSecurity Asset Management (CSAM)

---

## Usage

### Basic Usage (Interactive Mode)
```
python3 tag_report_generator.py
```

Follow the prompts to:
1. Select your Qualys platform (US1, EU2, UK, IN, etc.)
2. Enter username and password

### Command-Line Arguments
```
python3 tag_report_generator.py --platform US1 --username user_name

python3 tag_report_generator.py --platform EU1 --username user_name --password my_password
```

**Available Arguments:**
- `--help` - Show help message and exit
- `--platform <PLATFORM>` - Qualys platform (US1, US2, US3, US4, UK, EU1, EU2, EU3, IN, CA, AE, AU, KSA)
- `--username <USERNAME>` - Qualys username
- `--password <PASSWORD>` - Qualys password (will prompt if not provided)

### Progress Saving & Resume

**Interrupt at any time:** Press `Ctrl+C` during tag processing to pause and save progress.

**Resume session:** Run the script again with the same platform and username, then choose "yes" when prompted to resume.

**Auto-save:** Progress automatically saved every 10 tags.

**Stale detection:** Progress files older than 24 hours are automatically discarded.

---

## Output

### **Excel Report** (`tag_report_<PLATFORM>_<USERNAME>_YYYYMMDD_HHMMSS.xlsx`)

### **HTML Report** (`tag_report_<PLATFORM>_<USERNAME>_YYYYMMDD_HHMMSS.html`)

### **Progress File** (`tag_report_progress_<PLATFORM>_<USERNAME>.json`)
- Provides resume capability for interrupted sessions
- Automatically created during processing
- Deleted upon successful completion

---

## Tag Types

The script identifies and reports three types of tags:

| Tag Type | Description | Rule Text |
|----------|-------------|-----------|
| **Static** | Manually assigned tags with no automatic rules | N/A |
| **Dynamic** | Auto-assigned based on rules (GROOVY, ASSET_SEARCH, etc.) | Shows the rule definition |
| **Tag Set** | Combination of other tags using include/exclude logic | Shows resolved tag names |

### Tag Set Resolution

Tag Sets reference other tags by ID internally. The script performs a **two-pass resolution**:
1. First pass: Collects all tag IDs and names
2. Second pass: Resolves Tag Set references to human-readable tag names

Example output:
```
INCLUDE (ANY):
  - Cloud Agent
  - PA - OS: Windows
  - PA - OS: RPM

EXCLUDE (ANY):
  (none)
```

---

## Error Handling & Recovery

### Rate Limiting (HTTP 429)
When Qualys API rate limit is reached (300 calls/hour):
1. Script automatically saves progress
2. Displays instructions to resume after rate limit resets
3. Run script again and choose "yes" to resume

### Network Timeouts
- 60-second timeout on tag detail requests
- 30-second timeout on asset count requests
- Automatic progress save on timeout
- Resume from last successful tag

### Interrupted Sessions (Ctrl+C)
- Graceful shutdown with progress save
- Run script again to resume from last checkpoint
- No data loss

### Tag Set Resolution on Resume
- Unresolved tag sets are automatically detected on resume
- Re-fetched and properly resolved in the second pass

---

## Troubleshooting

**Authentication failed**
- Verify username/password and platform selection
- Confirm API access enabled and MFA disabled

**No tags retrieved**
- Check that accounts has permission to read Tags from Global AssetView (GAV) or CyberSecurity Asset Management (CSAM)
- Verify tags exist in subscription

**Module not found**
```
pip install requests openpyxl
```
Or:
```
pip3 install requests openpyxl
```

**Rate limit reached**
- Wait for rate limit window to reset (typically 1 hour)
- Resume using saved progress file

**Tag Set shows [TAGSET_PLACEHOLDER]**
- This indicates the second pass didn't run (likely due to interruption)
- Resume the script to re-fetch and resolve tag sets

---

## Security Notes

- Credentials entered at runtime are not stored
- JWT tokens expire after 4 hours
- Report files may contain sensitive tag configurations - handle securely
- Progress files contain tag data - secure appropriately
- Script is read-only and does not modify tags
- HTTPS connections are enforced for all API calls

---

## Notes

- Zero-asset tags may indicate unused or orphaned tags
- Tag hierarchy is preserved in the HTML report
- Created/Modified timestamps help identify stale or recently changed tags

---

## Version History

### **v1.2** (Current)
- Added Tag Set support with two-pass resolution
- Added tag set re-processing on resume (fixes placeholder issue)
- Added configurable constants for timeouts and intervals
- Added `handle_rate_limit()` helper function
- Improved exception handling (specific exceptions instead of bare except)
- Enhanced HTML report with tag type filtering
- Added column visibility toggle in HTML report

### **v1.0**
- Initial release
- Basic tag reporting with pagination
- Progress saving and resume capability
- Excel and HTML report generation
- Hierarchical display in HTML report
- Search, sort, and filter functionality

---

## Disclaimer

This script is provided as a utility for generating tag reports from your Qualys environment.
Use at your own discretion. The script is read-only and does not modify any tags in your subscription.

---

## Support

For issues, questions, or feature requests, please open an issue in the repository.
