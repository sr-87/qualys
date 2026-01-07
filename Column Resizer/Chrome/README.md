# Qualys Column Resizer

**Version 1.2**

A Chrome browser extension that adds draggable column resizers and visibility controls to Qualys VMDR and Asset Management (GAV/CASM) tables, making it easier to customize your view and work with data.

---

## Features

**Drag to Resize Columns** - Adjust column widths by dragging the resize handles between columns

**Show/Hide Columns** - Toggle column visibility via the "Columns Shown" menu in table settings

**Persistent Settings** - Your column widths and visibility preferences are saved and restored automatically

**Global Support** - Works on all Qualys platforms worldwide (US, EU, UK, India, Canada, Australia, UAE, Italy, KSA)

---

## Supported Pages

The extension works on these Qualys modules/pages:

**VMDR**
    VMDR > Vulnerabilities
**Global AssetView (GAV) or CyberSecurity Asset Management (CSAM)**
    GAV/CSAM > Inventory
    GAV/CSAM > Responses
    GAV/CSAM > Rules
    GAV/CSAM > Reports

The extension is **disabled** on pages where it's not needed (reports, traffic analyzer, patch management, etc.)

---

## Installation Instructions

### Step 1: Download the Extension
Download and extract the `qualys-column-resizer-v1.2.zip` file to a folder on your computer.

### Step 2: Open Chrome Extensions Page
1. Open Google Chrome
2. Navigate to: `chrome://extensions/`
3. Or click the three-dot menu → **Extensions** → **Manage Extensions**

### Step 3: Enable Developer Mode
In the top-right corner of the Extensions page, toggle **"Developer mode"** to ON.

### Step 4: Load the Extension
1. Click the **"Load unpacked"** button (appears after enabling Developer mode)
2. Browse to and select the extracted folder: `qualys-column-resizer-v1.2`
3. Click **"Select Folder"** (or "Select" on Mac)

### Step 5: Confirm Installation
The extension should now appear in your extensions list with the blue column icon.

---

## How to Use

### Resizing Columns
1. Navigate to:
    VMDR > Vulnerabilities or
    GAV/CSAM > Inventory
    GAV/CSAM > Responses
    GAV/CSAM > Rules
    GAV/CSAM > Reports
2. Hover between any two column headers
3. A resize handle will appear
4. Click and drag to adjust the column width
5. Your changes are saved automatically

### Hiding/Showing Columns
1. Click the **settings icon** (⚙️) in the table header under VMDR > Vulnerabilities
2. Select **"Columns Shown"** from the dropdown menu
3. Check/uncheck columns to show or hide them
4. Your preferences are saved automatically

---

## Troubleshooting

### Extension Not Working?
- **Refresh the page** after installing the extension
- Check that you're on a supported page (Vulnerabilities or Assets)
- Open Chrome DevTools (F12) and check the Console for any `[QCR]` messages

### Extension Disappeared After Chrome Update?
Chrome sometimes disables extensions after major updates. To re-enable:
1. Go to `chrome://extensions/`
2. Find "Qualys Column Resizer"
3. Toggle it back ON

### Resizers Not Appearing?
- Wait a few seconds for the page to fully load
- The extension uses progressive loading (up to 8 seconds for slow connections)
- Try refreshing the page

---

## Privacy & Security

- This extension only runs on Qualys domains
- No data is sent to external servers
- Settings are stored locally in your browser
- No tracking or analytics
- Open source code - you can review all files

---

## Supported Qualys Platforms

The extension works on all global Qualys platforms:
- United States (qualys.com)
- Europe (qualys.eu)
- United Kingdom (qualys.co.uk)
- India (qualys.in)
- Canada (qualys.ca)
- Australia (qualys.com.au)
- Italy (qualys.it)
- UAE (qualys.ae)
- Saudi Arabia (qualysksa.com)

---

## Uninstalling

To remove the extension:
1. Go to `chrome://extensions/`
2. Find "Qualys Column Resizer"
3. Click **"Remove"**
4. Confirm deletion

Your saved column preferences will be cleared from browser storage.

---

## Version History

**v1.2** (Current)
- Added support for all global Qualys platforms
- Fixed first-load activation issues
- Improved column resize handle visibility
- Added column show/hide functionality
- Better handling of narrow/checkbox columns

---

## Support

If you encounter issues or have questions, please open an Issue on GitHub.

---

**Note:** This is an unofficial browser extension and is not affiliated with or supported by Qualys, Inc.