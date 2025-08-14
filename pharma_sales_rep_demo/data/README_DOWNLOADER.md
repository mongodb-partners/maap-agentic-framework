# URL to PDF Downloader

This directory contains scripts to download URLs and convert them to PDF files, specifically designed for downloading product information from Dr. Reddy's website.

## Available Scripts

There are three different implementations available, with increasing levels of sophistication:

1. `download_urls_to_fld.sh` - Basic bash script using curl and wkhtmltopdf
2. `download_urls_chrome.sh` - Advanced bash script using Chrome headless
3. `download_urls.py` - Python implementation with multiple conversion methods

## Prerequisites

### For Bash Scripts

- For `download_urls_to_fld.sh`:
  - `curl` for downloading files
  - `wkhtmltopdf` for HTML to PDF conversion (optional)

- For `download_urls_chrome.sh`:
  - `curl` for downloading files
  - Google Chrome or Chromium for headless PDF conversion

### For Python Script

- Python 3.6+
- Required Python packages:
  ```
  pip install requests pdfkit selenium webdriver-manager
  ```
- External dependencies:
  - wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
  - Chrome or Chromium browser (for Selenium)

## Usage

### Bash Scripts

```bash
# Basic script
./download_urls_to_fld.sh

# Chrome-based script
./download_urls_chrome.sh
```

### Python Script

```bash
# Basic usage
./download_urls.py

# Advanced options
./download_urls.py --input your_urls.txt --output-dir ./your_pdfs --concurrent 5 --retries 3 --delay 2 --verbose
```

## Options for Python Script

- `-i, --input`: Input file with URLs (one per line)
- `-o, --output-dir`: Output directory for PDF files
- `-r, --retries`: Maximum number of retry attempts
- `-d, --delay`: Delay between retry attempts (seconds)
- `-c, --concurrent`: Number of concurrent downloads
- `-t, --timeout`: Download timeout in seconds
- `-v, --verbose`: Enable verbose logging

## URL File Format

The input file should contain one URL per line. Lines starting with `#` are treated as comments:

```
# Product information URLs
https://example.com/product1.pdf
https://example.com/product2.html
```

## Output

All scripts will:
1. Create a directory for the downloaded PDFs
2. Download or convert each URL to PDF
3. Save the PDFs with appropriate filenames
4. Provide a summary of successful and failed downloads

## Troubleshooting

- If PDF conversion fails, try the Chrome-based or Python script for better JavaScript support
- For SSL certificate errors, ensure your CA certificates are up-to-date
- If the scripts don't have permission to execute, run: `chmod +x script_name.sh`
- For the Python script, install the required dependencies: `pip install requests pdfkit selenium webdriver-manager`
