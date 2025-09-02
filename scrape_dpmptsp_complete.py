"""
Comprehensive DPMPTSP Jawa Tengah Website Scraper
Crawls the entire website to extract all text content and downloadable files
"""
import requests
from bs4 import BeautifulSoup
import os
import time
import urllib.parse
from urllib.parse import urljoin, urlparse
import re
from pathlib import Path
import json
from typing import Set, List, Dict, Any
import mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DPMPTSPScraper:
    def __init__(self, base_url: str = "https://web.dpmptsp.jatengprov.go.id/"):
        self.base_url = base_url.rstrip('/')
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.downloaded_files: Set[str] = set()
        self.scraped_pages: List[Dict[str, Any]] = []
        
        # Create output directories
        self.data_dir = Path("data/scraped_dpmptsp")
        self.text_dir = self.data_dir / "pages"
        self.files_dir = self.data_dir / "files"
        self.images_dir = self.data_dir / "images"
        
        for dir_path in [self.data_dir, self.text_dir, self.files_dir, self.images_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # File extensions to download
        self.download_extensions = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.rtf', '.csv', '.json', '.xml', '.zip', '.rar'
        }
        
        # Image extensions
        self.image_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'
        }

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and belongs to the target domain"""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ['http', 'https'] and
                'dpmptsp.jatengprov.go.id' in parsed.netloc and
                url not in self.visited_urls and
                url not in self.failed_urls
            )
        except:
            return False

    def clean_filename(self, filename: str) -> str:
        """Clean filename for safe saving"""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', '_', filename)
        return filename[:100]  # Limit length

    def extract_text_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract meaningful text content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No Title"
        
        # Extract main content areas
        content_selectors = [
            'main', '.content', '.main-content', '#content',
            '.post-content', '.entry-content', '.page-content',
            'article', '.article', '.news-content'
        ]
        
        main_content = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                main_content = content_elem.get_text(separator='\n', strip=True)
                break
        
        # If no main content found, extract from body
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body.get_text(separator='\n', strip=True)
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        # Extract headings
        headings = []
        for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            heading_text = h.get_text().strip()
            if heading_text:
                headings.append({
                    'level': h.name,
                    'text': heading_text
                })
        
        return {
            'title': title_text,
            'description': description,
            'content': main_content,
            'headings': headings,
            'word_count': len(main_content.split()) if main_content else 0
        }

    def download_file(self, url: str, local_path: Path) -> bool:
        """Download a file from URL"""
        try:
            logger.info(f"📥 Downloading: {url}")
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"✅ Downloaded: {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download {url}: {e}")
            return False

    def extract_links(self, soup: BeautifulSoup, current_url: str) -> Set[str]:
        """Extract all links from the page"""
        links = set()
        
        # Extract regular links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            if self.is_valid_url(full_url):
                links.add(full_url)
        
        return links

    def extract_downloadable_files(self, soup: BeautifulSoup, current_url: str) -> List[Dict[str, str]]:
        """Extract downloadable files from the page"""
        files = []
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            
            # Check if it's a downloadable file
            parsed_url = urlparse(full_url)
            file_extension = Path(parsed_url.path).suffix.lower()
            
            if file_extension in self.download_extensions:
                link_text = link.get_text().strip()
                files.append({
                    'url': full_url,
                    'text': link_text,
                    'extension': file_extension,
                    'filename': Path(parsed_url.path).name or f"file_{len(files)}{file_extension}"
                })
        
        # Also check for direct file references in attributes
        for elem in soup.find_all(attrs={'src': True}):
            src = elem['src']
            full_url = urljoin(current_url, src)
            parsed_url = urlparse(full_url)
            file_extension = Path(parsed_url.path).suffix.lower()
            
            if file_extension in self.download_extensions:
                files.append({
                    'url': full_url,
                    'text': elem.get('alt', '') or elem.get('title', ''),
                    'extension': file_extension,
                    'filename': Path(parsed_url.path).name or f"file_{len(files)}{file_extension}"
                })
        
        return files

    def scrape_page(self, url: str) -> Dict[str, Any]:
        """Scrape a single page"""
        logger.info(f"🔍 Scraping: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Try to decode with different encodings
            response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text content
            content_data = self.extract_text_content(soup)
            
            # Extract links for further crawling
            links = self.extract_links(soup, url)
            
            # Extract downloadable files
            downloadable_files = self.extract_downloadable_files(soup, url)
            
            # Save page content
            if content_data['content'] and content_data['word_count'] > 10:
                # Create safe filename from URL
                url_path = urlparse(url).path
                if url_path == '/' or not url_path:
                    filename = 'homepage.txt'
                else:
                    filename = self.clean_filename(url_path.replace('/', '_')) + '.txt'
                
                page_file = self.text_dir / filename
                counter = 1
                while page_file.exists():
                    name = filename.rsplit('.', 1)[0]
                    ext = filename.rsplit('.', 1)[1] if '.' in filename else 'txt'
                    page_file = self.text_dir / f"{name}_{counter}.{ext}"
                    counter += 1
                
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(f"URL: {url}\n")
                    f.write(f"Title: {content_data['title']}\n")
                    f.write(f"Description: {content_data['description']}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(content_data['content'])
                
                logger.info(f"💾 Saved page content: {page_file}")
            
            # Download files
            for file_info in downloadable_files:
                file_url = file_info['url']
                if file_url not in self.downloaded_files:
                    safe_filename = self.clean_filename(file_info['filename'])
                    file_path = self.files_dir / safe_filename
                    
                    # Add counter if file exists
                    counter = 1
                    while file_path.exists():
                        name = safe_filename.rsplit('.', 1)[0]
                        ext = safe_filename.rsplit('.', 1)[1] if '.' in safe_filename else ''
                        file_path = self.files_dir / f"{name}_{counter}.{ext}"
                        counter += 1
                    
                    if self.download_file(file_url, file_path):
                        self.downloaded_files.add(file_url)
            
            self.visited_urls.add(url)
            
            return {
                'url': url,
                'status': 'success',
                'title': content_data['title'],
                'word_count': content_data['word_count'],
                'links_found': len(links),
                'files_found': len(downloadable_files),
                'new_links': [link for link in links if link not in self.visited_urls]
            }
            
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            self.failed_urls.add(url)
            return {
                'url': url,
                'status': 'failed',
                'error': str(e)
            }

    def crawl_website(self, max_pages: int = 500, max_workers: int = 3):
        """Crawl the entire website"""
        logger.info(f"🚀 Starting comprehensive crawl of {self.base_url}")
        logger.info(f"📁 Data will be saved to: {self.data_dir}")
        
        # Start with homepage
        urls_to_visit = [self.base_url]
        pages_scraped = 0
        
        while urls_to_visit and pages_scraped < max_pages:
            # Process URLs in batches
            current_batch = urls_to_visit[:max_workers]
            urls_to_visit = urls_to_visit[max_workers:]
            
            # Use ThreadPoolExecutor for concurrent scraping
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(self.scrape_page, url): url for url in current_batch}
                
                for future in as_completed(futures):
                    result = future.result()
                    self.scraped_pages.append(result)
                    pages_scraped += 1
                    
                    if result['status'] == 'success':
                        # Add new links to queue
                        new_links = result.get('new_links', [])
                        for link in new_links:
                            if link not in urls_to_visit and self.is_valid_url(link):
                                urls_to_visit.append(link)
                        
                        logger.info(f"📊 Progress: {pages_scraped}/{max_pages} pages | "
                                  f"Queue: {len(urls_to_visit)} | "
                                  f"Files: {len(self.downloaded_files)}")
                    
                    # Add delay to be respectful
                    time.sleep(1)
        
        # Save crawl summary
        summary = {
            'total_pages_scraped': pages_scraped,
            'successful_pages': len([p for p in self.scraped_pages if p['status'] == 'success']),
            'failed_pages': len(self.failed_urls),
            'total_files_downloaded': len(self.downloaded_files),
            'scraped_pages': self.scraped_pages,
            'failed_urls': list(self.failed_urls)
        }
        
        with open(self.data_dir / 'crawl_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"🎉 Crawl completed!")
        logger.info(f"📄 Total pages: {summary['successful_pages']}")
        logger.info(f"📁 Total files: {summary['total_files_downloaded']}")
        logger.info(f"❌ Failed URLs: {summary['failed_pages']}")
        logger.info(f"📊 Summary saved to: {self.data_dir / 'crawl_summary.json'}")

def main():
    """Main function to run the scraper"""
    scraper = DPMPTSPScraper()
    
    try:
        scraper.crawl_website(max_pages=1000, max_workers=3)
    except KeyboardInterrupt:
        print("\n🛑 Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
    finally:
        # Save progress even if interrupted
        if scraper.scraped_pages:
            summary = {
                'total_pages_scraped': len(scraper.scraped_pages),
                'successful_pages': len([p for p in scraper.scraped_pages if p['status'] == 'success']),
                'failed_pages': len(scraper.failed_urls),
                'total_files_downloaded': len(scraper.downloaded_files),
                'scraped_pages': scraper.scraped_pages,
                'failed_urls': list(scraper.failed_urls)
            }
            
            with open(scraper.data_dir / 'crawl_summary_partial.json', 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Progress saved to: {scraper.data_dir}")

if __name__ == "__main__":
    main()
