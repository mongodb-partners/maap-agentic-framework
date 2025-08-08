#!/usr/bin/env python3
"""
URL to PDF Downloader

This script downloads a list of URLs and converts them to PDF format,
saving them in a specified directory.
"""

import argparse
import os
import re
import sys
import time
import hashlib
import logging
from pathlib import Path
from urllib.parse import urlparse
import requests
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("url_downloader.log")
    ]
)
logger = logging.getLogger(__name__)

class PDFDownloader:
    """Class to handle downloading URLs as PDFs"""
    
    def __init__(self, output_dir="./pdf_downloads", max_retries=3, delay=2, 
                 concurrent_downloads=5, timeout=30):
        """Initialize the downloader with configuration options"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.max_retries = max_retries
        self.delay = delay
        self.concurrent_downloads = concurrent_downloads
        self.timeout = timeout
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        
        # Check for PDF conversion capabilities
        try:
            import pdfkit
            self.pdfkit_available = True
            logger.info("pdfkit is available for HTML to PDF conversion")
        except ImportError:
            self.pdfkit_available = False
            logger.warning("pdfkit not available. Install with: pip install pdfkit")
            logger.warning("Also install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
        
        try:
            from selenium import webdriver
            self.selenium_available = True
            logger.info("Selenium is available for advanced HTML to PDF conversion")
        except ImportError:
            self.selenium_available = False
            logger.warning("Selenium not available. For better results with JavaScript-heavy sites:")
            logger.warning("pip install selenium webdriver-manager")

    def generate_filename(self, url):
        """Generate a clean, safe filename from a URL"""
        # Try to get a meaningful name from the URL
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if path.endswith('.pdf'):
            # Use the PDF filename if it's already a PDF
            filename = os.path.basename(path)
        else:
            # Create a name from path or use domain + hash if path is empty
            if path:
                # Use last part of path
                parts = path.split('/')
                filename = parts[-1] or parts[-2] if len(parts) > 1 else parsed.netloc
                
                # Clean up the name
                filename = re.sub(r'\.\w+$', '', filename)  # Remove extension
                filename += '.pdf'  # Add PDF extension
            else:
                # Create a hash-based name if path is empty
                domain = parsed.netloc.replace('www.', '')
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"{domain}_{url_hash}.pdf"
        
        # Clean up the filename
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return filename

    def download_pdf(self, url):
        """Download a direct PDF URL"""
        for attempt in range(1, self.max_retries + 1):
            try:
                headers = {"User-Agent": self.user_agent}
                response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
                response.raise_for_status()
                
                if response.headers.get('content-type', '').lower() == 'application/pdf':
                    return response.content
                else:
                    logger.warning(f"URL does not return PDF content: {url}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.delay)
                else:
                    logger.error(f"Failed to download after {self.max_retries} attempts: {url}")
                    return None
        return None

    def html_to_pdf_pdfkit(self, url):
        """Convert HTML to PDF using pdfkit"""
        if not self.pdfkit_available:
            return None
        
        import pdfkit
        try:
            options = {
                'javascript-delay': 2000,
                'no-stop-slow-scripts': None,
                'user-agent': self.user_agent,
                'quiet': '',
                'encoding': 'UTF-8',
            }
            return pdfkit.from_url(url, False, options=options)
        except Exception as e:
            logger.error(f"pdfkit conversion failed: {e}")
            return None

    def html_to_pdf_selenium(self, url):
        """Convert HTML to PDF using Selenium with Chrome"""
        if not self.selenium_available:
            return None
        
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options
        import base64
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument(f"user-agent={self.user_agent}")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            driver.get(url)
            # Wait for JavaScript to execute
            time.sleep(3)
            
            # Execute Chrome's Print to PDF
            print_options = {
                'landscape': False,
                'displayHeaderFooter': False,
                'printBackground': True,
                'preferCSSPageSize': True,
            }
            result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
            driver.quit()
            
            # Convert base64 to PDF content
            return base64.b64decode(result['data'])
        except Exception as e:
            logger.error(f"Selenium conversion failed: {e}")
            return None

    def process_url(self, url):
        """Process a single URL to download or convert to PDF"""
        url = url.strip()
        if not url or url.startswith('#'):
            return None
            
        filename = self.generate_filename(url)
        output_path = self.output_dir / filename
        
        logger.info(f"Processing: {url}")
        logger.info(f"Output file: {output_path}")
        
        # Determine if it's a direct PDF or needs conversion
        if url.lower().endswith('.pdf'):
            content = self.download_pdf(url)
        else:
            # Try HTML to PDF conversion methods
            content = None
            if self.selenium_available:
                logger.info("Attempting conversion with Selenium...")
                content = self.html_to_pdf_selenium(url)
            
            if content is None and self.pdfkit_available:
                logger.info("Attempting conversion with pdfkit...")
                content = self.html_to_pdf_pdfkit(url)
            
            if content is None:
                logger.info("Attempting direct download...")
                content = self.download_pdf(url)
                
        if content:
            with open(output_path, 'wb') as f:
                f.write(content)
            
            # Verify file size
            size = os.path.getsize(output_path)
            if size > 0:
                logger.info(f"✅ Successfully saved: {filename} ({size/1024:.1f} KB)")
                return True
            else:
                logger.warning(f"⚠️ File is empty: {filename}")
                return False
        else:
            logger.error(f"❌ Failed to process URL: {url}")
            return False

    def download_all(self, url_file):
        """Download all URLs from a file"""
        # Check if URL file exists
        if not os.path.isfile(url_file):
            logger.error(f"URL file not found: {url_file}")
            return False
            
        # Read URLs from file
        with open(url_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
        logger.info(f"Found {len(urls)} URLs to process")
        
        # Process URLs concurrently
        results = []
        with ThreadPoolExecutor(max_workers=self.concurrent_downloads) as executor:
            for i, url in enumerate(urls):
                # Add a small delay between submissions to avoid hammering the server
                if i > 0:
                    time.sleep(0.5)
                results.append(executor.submit(self.process_url, url))
        
        # Count successes and failures
        successes = sum(1 for future in results if future.result())
        failures = len(urls) - successes
        
        logger.info(f"Download process complete: {successes} successful, {failures} failed")
        logger.info(f"Files saved to: {self.output_dir}")
        
        return successes, failures

def main():
    """Main function to parse arguments and start download process"""
    parser = argparse.ArgumentParser(description="Download URLs as PDF files")
    parser.add_argument("-i", "--input", default="dr_reddys_prd_info_urls.txt",
                        help="Input file with URLs (one URL per line)")
    parser.add_argument("-o", "--output-dir", default="./pdf_downloads",
                        help="Output directory for PDF files")
    parser.add_argument("-r", "--retries", type=int, default=3,
                        help="Maximum number of retry attempts")
    parser.add_argument("-d", "--delay", type=int, default=2,
                        help="Delay between retry attempts (seconds)")
    parser.add_argument("-c", "--concurrent", type=int, default=3,
                        help="Number of concurrent downloads")
    parser.add_argument("-t", "--timeout", type=int, default=30,
                        help="Download timeout in seconds")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose logging")
                        
    args = parser.parse_args()
    
    # Set verbose logging if requested
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create downloader and start downloads
    downloader = PDFDownloader(
        output_dir=args.output_dir,
        max_retries=args.retries,
        delay=args.delay,
        concurrent_downloads=args.concurrent,
        timeout=args.timeout
    )
    
    try:
        successes, failures = downloader.download_all(args.input)
        sys.exit(0 if failures == 0 else 1)
    except Exception as e:
        logger.exception(f"Error in download process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
