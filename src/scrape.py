import os
import re
import sys
import time
import json
import mimetypes
from urllib.parse import urljoin, urldefrag
from pathlib import Path
from typing import Set, List, Dict, Optional

import requests
from bs4 import BeautifulSoup
import urllib3
from tqdm import tqdm

# Simple webpage scraper focused on collecting downloadable dataset-like files.
# Inspired by https://github.com/mishushakov/llm-scraper but trimmed down and adapted to this project.
# Usage (single page):
#   python src/scrape.py https://example.com/data/ out_dir
# Crawl same-origin (optional depth >1):
#   python src/scrape.py https://example.com/data/ out_dir --max-pages 50 --max-depth 2
# Only dataset file types (xlsx,pdf,docx,csv) are saved. A manifest JSON is produced.

DATA_EXTS = {'.xlsx', '.xls', '.pdf', '.docx', '.csv'}
DEFAULT_TIMEOUT = 20
USER_AGENT = 'ptspRagScraper/0.1 (+https://localhost)'

# Global session - will be configured in main()
session = None

class ScrapeStats:
    def __init__(self):
        self.pages_visited = 0
        self.files_downloaded = 0
        self.errors: List[str] = []


def is_dataset_url(url: str) -> bool:
    path = url.split('?', 1)[0].split('#', 1)[0]
    ext = Path(path).suffix.lower()
    if ext in DATA_EXTS:
        return True
    return False


def filename_from_url(url: str) -> str:
    # Remove query/fragment, keep basename
    base = url.split('?', 1)[0].split('#', 1)[0]
    name = os.path.basename(base)
    if not name:
        # fallback generic name
        name = re.sub(r'\W+', '_', base) or 'file'
    return name


def save_file(url: str, out_dir: Path, stats: ScrapeStats) -> Optional[Dict]:
    try:
        r = session.get(url, timeout=DEFAULT_TIMEOUT, stream=True)
        r.raise_for_status()
        # Try to guess extension via Content-Type if missing
        fname = filename_from_url(url)
        if '.' not in fname:
            ctype = r.headers.get('Content-Type', '')
            ext = mimetypes.guess_extension(ctype.split(';')[0].strip()) or ''
            if ext and ext.lower() in DATA_EXTS:
                fname += ext
        ext = Path(fname).suffix.lower()
        if ext not in DATA_EXTS:
            return None
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / fname
        with open(target, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        stats.files_downloaded += 1
        return {
            'url': url,
            'filename': fname,
            'size_bytes': target.stat().st_size,
            'content_type': r.headers.get('Content-Type'),
            'retrieved_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }
    except Exception as e:
        stats.errors.append(f'FILE {url} -> {e}')
        return None


def extract_links(base_url: str, html: str) -> List[str]:
    soup = BeautifulSoup(html, 'lxml')
    links = []
    for tag in soup.find_all(['a']):
        href = tag.get('href')
        if not href:
            continue
        href, _ = urldefrag(href)
        full = urljoin(base_url, href)
        links.append(full)
    return links


def same_origin(url_a: str, url_b: str) -> bool:
    try:
        from urllib.parse import urlparse
        pa = urlparse(url_a)
        pb = urlparse(url_b)
        return (pa.scheme, pa.netloc) == (pb.scheme, pb.netloc)
    except Exception:
        return False


def crawl(start_url: str, out_dir: Path, max_pages: int, max_depth: int, collect_html: bool=False, insecure: bool=False, retries: int=3):
    global session
    
    # Initialize session here with SSL settings
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})
    
    if insecure:
        # Disable SSL verification and suppress warnings
        session.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Configure retries
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    retry_strategy = Retry(
        total=retries,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    stats = ScrapeStats()
    visited: Set[str] = set()
    to_visit: List[tuple[str,int]] = [(start_url, 0)]
    manifest: Dict[str, List[Dict]] = {'files': [], 'start_url': start_url}

    # Initialize progress bar
    pbar = tqdm(total=max_pages, desc="Scraping pages", unit="page", 
                bar_format='{desc}: {n_fmt}/{total_fmt} pages | {postfix}')
    
    try:
        while to_visit and stats.pages_visited < max_pages:
            url, depth = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)
            
            # Update progress bar description with current URL
            current_url_short = url[:50] + "..." if len(url) > 50 else url
            pbar.set_postfix_str(f"Files: {stats.files_downloaded} | Current: {current_url_short}")
            
            try:
                resp = session.get(url, timeout=DEFAULT_TIMEOUT)
                ctype = resp.headers.get('Content-Type', '')
                # If it's a direct file link
                if is_dataset_url(url) or any(t in ctype for t in ['application/pdf','application/vnd','text/csv']):
                    meta = save_file(url, out_dir, stats)
                    if meta:
                        manifest['files'].append(meta)
                        pbar.set_postfix_str(f"Files: {stats.files_downloaded} | Downloaded: {meta['filename']}")
                    continue
                # Otherwise treat as HTML
                if 'text/html' in ctype.lower():
                    stats.pages_visited += 1
                    pbar.update(1)  # Update progress bar
                    html = resp.text
                    if collect_html:
                        (out_dir / 'pages').mkdir(parents=True, exist_ok=True)
                        safe_name = re.sub(r'[^a-zA-Z0-9]+', '_', url)[:80]
                        with open(out_dir / 'pages' / f'{safe_name}.html', 'w', encoding='utf-8') as f:
                            f.write(html)
                    links = extract_links(url, html)
                    for link in links:
                        if link not in visited:
                            if is_dataset_url(link):
                                meta = save_file(link, out_dir, stats)
                                if meta:
                                    manifest['files'].append(meta)
                                    pbar.set_postfix_str(f"Files: {stats.files_downloaded} | Downloaded: {meta['filename']}")
                            elif depth + 1 <= max_depth and same_origin(start_url, link):
                                to_visit.append((link, depth+1))
                else:
                    # Non-html, attempt save if dataset
                    meta = save_file(url, out_dir, stats)
                    if meta:
                        manifest['files'].append(meta)
                        pbar.set_postfix_str(f"Files: {stats.files_downloaded} | Downloaded: {meta['filename']}")
            except Exception as e:
                stats.errors.append(f'PAGE {url} -> {e}')
                pbar.set_postfix_str(f"Files: {stats.files_downloaded} | Error on: {current_url_short}")
    
    finally:
        pbar.close()

    manifest['stats'] = {
        'pages_visited': stats.pages_visited,
        'files_downloaded': stats.files_downloaded,
        'errors': stats.errors,
    }
    with open(out_dir / 'manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    return manifest


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Scrape dataset files from a webpage (and optional crawl).')
    parser.add_argument('url', help='Start URL')
    parser.add_argument('out_dir', help='Output directory')
    parser.add_argument('--max-pages', type=int, default=30, help='Max HTML pages to fetch')
    parser.add_argument('--max-depth', type=int, default=0, help='Crawl depth (0 = only start page)')
    parser.add_argument('--collect-html', action='store_true', help='Save HTML pages as well')
    parser.add_argument('--insecure', action='store_true', help='Disable SSL certificate verification')
    parser.add_argument('--retries', type=int, default=3, help='Number of retry attempts for failed requests')
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    manifest = crawl(args.url, out_dir, args.max_pages, args.max_depth, args.collect_html, args.insecure, args.retries)
    print(f"Done. Pages: {manifest['stats']['pages_visited']} Files: {manifest['stats']['files_downloaded']} Errors: {len(manifest['stats']['errors'])}")
    if manifest['stats']['errors']:
        print('Some errors occurred (see manifest.json).')

if __name__ == '__main__':
    main()
