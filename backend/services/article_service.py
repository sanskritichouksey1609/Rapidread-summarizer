import requests
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from datetime import datetime
import time

try:
    from newspaper import Article, fulltext
    import newspaper
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

if NEWSPAPER_AVAILABLE:
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
    except Exception:
        pass


def get_article_info(url: str) -> Dict[str, Any]:
    try:
        # Validate URL first
        if not validate_article_url(url):
            return {
                "success": False,
                "error": "Invalid URL provided",
                "content": "",
                "title": "",
                "url": url
            }
        
        if NEWSPAPER_AVAILABLE:
            result = try_newspaper_extraction(url)
            if result["success"]:
                return result
        
        if BEAUTIFULSOUP_AVAILABLE:
            result = try_beautifulsoup_extraction(url)
            if result["success"]:
                return result
        
        result = try_basic_extraction(url)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to extract article: {str(e)}",
            "content": "",
            "title": "",
            "url": url
        }


def try_newspaper_extraction(url: str) -> Dict[str, Any]:
    try:
        config = newspaper.Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        config.request_timeout = 15
        config.number_threads = 1
        config.fetch_images = False
        config.memoize_articles = False
        
        article = Article(url, config=config)
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                article.download()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1)
        
        if not article.html or len(article.html) < 100:
            return {"success": False, "error": "No content downloaded"}
        
        article.parse()
        
        article_text = article.text
        article_title = article.title
        
        # Validate content
        if not article_text or len(article_text.strip()) < 50:
            return {"success": False, "error": "Content too short"}
        
        keywords = []
        summary = ""
        try:
            article.nlp()
            keywords = article.keywords[:10] if hasattr(article, 'keywords') and article.keywords else []
            summary = article.summary[:500] + "..." if hasattr(article, 'summary') and len(article.summary) > 500 else getattr(article, 'summary', '')
        except Exception:
            pass
        
        authors = getattr(article, 'authors', [])
        publish_date = getattr(article, 'publish_date', None)
        top_image = getattr(article, 'top_image', '')
        
        publish_date_str = ""
        if publish_date:
            try:
                if isinstance(publish_date, datetime):
                    publish_date_str = publish_date.strftime("%Y-%m-%d")
                else:
                    publish_date_str = str(publish_date)
            except:
                publish_date_str = ""
        
        if len(article_text) > 15000:
            article_text = article_text[:15000] + "..."
        
        return {
            "success": True,
            "content": article_text,
            "title": article_title or extract_title_from_url(url),
            "url": url,
            "domain": urlparse(url).netloc,
            "authors": authors,
            "publish_date": publish_date_str,
            "keywords": keywords,
            "summary": summary,
            "top_image": top_image,
            "extraction_method": "newspaper3k"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def try_beautifulsoup_extraction(url: str) -> Dict[str, Any]:
    try:
        # Make request with enhanced headers
        headers = get_enhanced_headers()
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(url, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        html_content = response.text
        
        if len(html_content) < 100:
            return {"success": False, "error": "HTML content too short"}
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        title = extract_title_from_soup(soup) or extract_title_from_url(url)
        
        content = extract_content_from_soup(soup)
        
        if not content or len(content.strip()) < 50:
            return {"success": False, "error": "No meaningful content found"}
        
        if len(content) > 15000:
            content = content[:15000] + "..."
        
        return {
            "success": True,
            "content": content,
            "title": title,
            "url": url,
            "domain": urlparse(url).netloc,
            "authors": [],
            "publish_date": "",
            "keywords": [],
            "summary": "",
            "top_image": "",
            "extraction_method": "beautifulsoup"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def try_basic_extraction(url: str) -> Dict[str, Any]:
    try:
        # Make request
        headers = get_enhanced_headers()
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        html_content = response.text
        
        if len(html_content) < 100:
            return {"success": False, "error": "HTML content too short"}
        
        title = extract_title_from_html(html_content) or extract_title_from_url(url)
        
        content = extract_text_from_html_regex(html_content)
        
        if not content or len(content.strip()) < 50:
            return {"success": False, "error": "No meaningful content found"}
        
        return {
            "success": True,
            "content": content,
            "title": title,
            "url": url,
            "domain": urlparse(url).netloc,
            "authors": [],
            "publish_date": "",
            "keywords": [],
            "summary": "",
            "top_image": "",
            "extraction_method": "basic"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"All extraction methods failed. Last error: {str(e)}",
            "content": "",
            "title": "",
            "url": url
        }


def get_enhanced_headers() -> Dict[str, str]:
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Sec-GPC': '1'
    }

def extract_title_from_soup(soup) -> str:
    try:
        title_sources = [
            soup.find('title'),
            soup.find('h1'),
            soup.find('meta', property='og:title'),
            soup.find('meta', attrs={'name': 'title'}),
            soup.find('meta', attrs={'name': 'twitter:title'})
        ]
        
        for source in title_sources:
            if source:
                if source.name == 'meta':
                    title = source.get('content', '')
                else:
                    title = source.get_text(strip=True)
                
                if title and len(title.strip()) > 3:
                    # Clean title
                    title = re.sub(r'\s+', ' ', title).strip()
                    return title[:200]  # Limit length
        
        return "Article"
    except:
        return "Article"


def extract_content_from_soup(soup) -> str:
    try:
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header', 'menu', 'noscript']):
            element.decompose()
        
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.story-body',
            '.post-body',
            '#content',
            '.main-content',
            '.article-body',
            '.entry-body'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content and main_content.get_text(strip=True):
                break
        
        if not main_content:
            main_content = soup.find('body') or soup
        
        text = main_content.get_text(strip=True, separator=' ')
        
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
        
    except Exception:
        return ""


def extract_title_from_html(html_content: str) -> str:
    try:
        # Try different title patterns
        patterns = [
            r'<title[^>]*>(.*?)</title>',
            r'<h1[^>]*>(.*?)</h1>',
            r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']',
            r'<meta[^>]*name=["\']title["\'][^>]*content=["\']([^"\']*)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                title = match.group(1).strip()
                # Clean up title
                title = re.sub(r'<[^>]+>', '', title)  # Remove any HTML tags
                title = re.sub(r'\s+', ' ', title)
                if title and len(title) > 3:
                    return title[:200]
        
        return "Article"
    except:
        return "Article"


def extract_title_from_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        path = parsed.path.strip('/')
        
        if path:
            title_part = path.split('/')[-1]
            title_part = re.sub(r'[_-]', ' ', title_part)
            title_part = re.sub(r'\.[^.]*$', '', title_part)  # Remove file extension
            title_part = title_part.title()
            return f"{title_part} - {domain}"
        else:
            return f"Article from {domain}"
    except:
        return "Article"


def extract_text_from_html_regex(html_content: str) -> str:
    try:
      
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        
        text_content = re.sub(r'<[^>]+>', ' ', html_content)
        
        try:
            import html
            text_content = html.unescape(text_content)
        except:
            pass
        
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        if len(text_content) > 15000:
            text_content = text_content[:15000] + "..."
        
        return text_content
        
    except Exception:
        return ""


def validate_article_url(url: str) -> bool:
    
    try:
        if not url or not isinstance(url, str):
            return False
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed = urlparse(url)
        
        if not (parsed.scheme and parsed.netloc):
            return False
        
        if parsed.scheme not in ['http', 'https']:
            return False
        
        excluded_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.jpg', '.png', '.gif', '.mp4', '.mp3']
        if any(url.lower().endswith(ext) for ext in excluded_extensions):
            return False
        
        return True
        
    except:
        return False


def fetch_article_text(url: str) -> str:
    result = get_article_info(url)
    return result.get("content", "") if result.get("success") else ""


def get_article_metadata(url: str) -> Dict[str, Any]:
    result = get_article_info(url)
    if result.get("success"):
        return {
            "title": result.get("title", ""),
            "authors": result.get("authors", []),
            "publish_date": result.get("publish_date", ""),
            "top_image": result.get("top_image", ""),
            "url": url,
            "domain": result.get("domain", "")
        }
    else:
        return {"error": result.get("error", "Failed to get metadata")}


def extract_text_from_html(html_content: str) -> str:
    
    return extract_text_from_html_regex(html_content)