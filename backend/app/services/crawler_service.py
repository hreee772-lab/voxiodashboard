import asyncio
import re
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from typing import List, Dict

def clean_text(text: str) -> str:
    """Remove extra whitespace, navigation artifacts, and clean up extracted text."""
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove lines that are just symbols or very short (nav items, footers)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip empty lines, very short lines (likely nav), or lines that are just symbols
        if len(stripped) < 3:
            continue
        if re.match(r'^[\|\-\=\*\#\>\<\/\\]+$', stripped):
            continue
        cleaned_lines.append(stripped)
    text = '\n'.join(cleaned_lines)
    # Remove excessive spaces
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

async def crawl_url(url: str) -> Dict[str, str]:
    """Crawl a single URL and extract clean text content."""
    config = CrawlerRunConfig(
        word_count_threshold=10,
        exclude_external_links=True,
        remove_overlay_elements=True,
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        
        if result.success:
            # Use markdown content (cleaner than raw HTML)
            content = result.markdown or result.cleaned_html or ""
            content = clean_text(content)
            return {"url": url, "content": content, "title": result.metadata.get("title", url) if result.metadata else url}
        else:
            return {"url": url, "content": "", "title": url}

async def crawl_website(base_url: str, max_pages: int = 10) -> List[Dict[str, str]]:
    """Crawl a website starting from base_url, following internal links up to max_pages."""
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc
    
    visited = set()
    to_visit = [base_url]
    results = []
    
    config = CrawlerRunConfig(
        word_count_threshold=10,
        exclude_external_links=True,
        remove_overlay_elements=True,
    )
    
    async with AsyncWebCrawler() as crawler:
        while to_visit and len(results) < max_pages:
            current_url = to_visit.pop(0)
            
            # Normalize URL
            current_url = current_url.rstrip('/')
            if current_url in visited:
                continue
            visited.add(current_url)
            
            try:
                result = await crawler.arun(url=current_url, config=config)
                
                if result.success:
                    content = result.markdown or result.cleaned_html or ""
                    content = clean_text(content)
                    
                    if content and len(content) > 50:
                        title = result.metadata.get("title", current_url) if result.metadata else current_url
                        results.append({
                            "url": current_url,
                            "content": content,
                            "title": title
                        })
                    
                    # Extract internal links to follow
                    if result.links and len(results) < max_pages:
                        internal_links = result.links.get("internal", [])
                        for link_obj in internal_links:
                            href = link_obj.get("href", "") if isinstance(link_obj, dict) else str(link_obj)
                            if not href:
                                continue
                            
                            full_url = urljoin(current_url, href).rstrip('/')
                            parsed = urlparse(full_url)
                            
                            # Only follow internal links, skip anchors, files, etc.
                            if parsed.netloc != base_domain:
                                continue
                            if any(full_url.endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip', '.css', '.js']):
                                continue
                            if '#' in full_url:
                                full_url = full_url.split('#')[0]
                            
                            if full_url not in visited and full_url not in to_visit:
                                to_visit.append(full_url)
                                
            except Exception as e:
                print(f"Error crawling {current_url}: {e}")
                continue
    
    return results
