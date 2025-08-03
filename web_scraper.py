import requests
import re
import json
from typing import Dict, List, Optional, Union
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """Universal web scraper for YouTube and other websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.driver = None
    
    def is_configured(self) -> bool:
        """Always returns True since no API key is needed"""
        return True
    
    def get_page_content(self, url: str, use_selenium: bool = False) -> Optional[str]:
        """Get page content using requests or selenium"""
        try:
            if use_selenium:
                return self._get_content_selenium(url)
            else:
                return self._get_content_requests(url)
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return None
    
    def _get_content_requests(self, url: str) -> Optional[str]:
        """Get content using requests library"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Requests error: {e}")
            return None
    
    def _get_content_selenium(self, url: str) -> Optional[str]:
        """Get content using selenium for dynamic content"""
        try:
            if not self.driver:
                self._setup_selenium()
            
            self.driver.get(url)
            time.sleep(3)  # Wait for dynamic content to load
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Selenium error: {e}")
            return None
    
    def _setup_selenium(self):
        """Setup selenium webdriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.error(f"Failed to setup selenium: {e}")
            self.driver = None
    
    def analyze_url(self, url: str) -> Dict:
        """Analyze any URL and extract relevant information"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return self._analyze_youtube_url(url)
        else:
            return self._analyze_generic_website(url)
    
    def _analyze_youtube_url(self, url: str) -> Dict:
        """Analyze YouTube URL (channel or video)"""
        try:
            if '/watch?v=' in url or 'youtu.be/' in url:
                return self._analyze_youtube_video(url)
            else:
                return self._analyze_youtube_channel(url)
        except Exception as e:
            logger.error(f"Error analyzing YouTube URL: {e}")
            return {"error": str(e)}
    
    def _analyze_youtube_video(self, url: str) -> Dict:
        """Analyze a single YouTube video"""
        try:
            # Use yt-dlp to extract video information
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                video_data = {
                    'type': 'video',
                    'id': info.get('id', ''),
                    'title': info.get('title', ''),
                    'description': info.get('description', ''),
                    'uploader': info.get('uploader', ''),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'comment_count': info.get('comment_count', 0),
                    'duration': info.get('duration', 0),
                    'tags': info.get('tags', []),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url),
                    'channel_id': info.get('channel_id', ''),
                    'channel_url': info.get('channel_url', ''),
                }
                
                return video_data
                
        except Exception as e:
            logger.error(f"Error extracting video info: {e}")
            # Fallback to web scraping
            return self._scrape_youtube_video(url)
    
    def _analyze_youtube_channel(self, url: str) -> Dict:
        """Analyze YouTube channel"""
        try:
            # Extract channel info and recent videos
            channel_info = self._scrape_youtube_channel(url)
            return channel_info
        except Exception as e:
            logger.error(f"Error analyzing YouTube channel: {e}")
            return {"error": str(e)}
    
    def _scrape_youtube_video(self, url: str) -> Dict:
        """Scrape YouTube video page"""
        try:
            content = self.get_page_content(url, use_selenium=True)
            if not content:
                return {"error": "Could not fetch video content"}
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract basic information
            title = self._extract_youtube_title(soup)
            description = self._extract_youtube_description(soup)
            views = self._extract_youtube_views(soup)
            likes = self._extract_youtube_likes(soup)
            
            return {
                'type': 'video',
                'title': title,
                'description': description,
                'view_count': views,
                'like_count': likes,
                'comment_count': 0,  # Difficult to scrape accurately
                'tags': self._extract_youtube_tags(soup),
                'webpage_url': url,
                'scraping_method': 'beautifulsoup'
            }
            
        except Exception as e:
            logger.error(f"Error scraping YouTube video: {e}")
            return {"error": str(e)}
    
    def _scrape_youtube_channel(self, url: str) -> Dict:
        """Scrape YouTube channel page"""
        try:
            content = self.get_page_content(url, use_selenium=True)
            if not content:
                return {"error": "Could not fetch channel content"}
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract channel info
            channel_name = self._extract_channel_name(soup)
            subscriber_count = self._extract_subscriber_count(soup)
            
            # Extract recent videos
            videos = self._extract_channel_videos(soup, url)
            
            return {
                'type': 'channel',
                'channel_name': channel_name,
                'subscriber_count': subscriber_count,
                'videos': videos,
                'total_videos': len(videos),
                'webpage_url': url,
                'scraping_method': 'beautifulsoup'
            }
            
        except Exception as e:
            logger.error(f"Error scraping YouTube channel: {e}")
            return {"error": str(e)}
    
    def _analyze_generic_website(self, url: str) -> Dict:
        """Analyze any website"""
        try:
            content = self.get_page_content(url)
            if not content:
                return {"error": "Could not fetch website content"}
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract basic website information
            title = self._extract_website_title(soup)
            description = self._extract_website_description(soup)
            keywords = self._extract_website_keywords(soup)
            headings = self._extract_headings(soup)
            images = self._extract_images(soup)
            links = self._extract_links(soup)
            
            return {
                'type': 'website',
                'title': title,
                'description': description,
                'keywords': keywords,
                'headings': headings,
                'images': len(images),
                'links': len(links),
                'webpage_url': url,
                'content_analysis': self._analyze_content_structure(soup),
                'seo_analysis': self._analyze_website_seo(soup),
                'scraping_method': 'beautifulsoup'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing website: {e}")
            return {"error": str(e)}
    
    def _extract_youtube_title(self, soup: BeautifulSoup) -> str:
        """Extract YouTube video title"""
        selectors = [
            'meta[property="og:title"]',
            'meta[name="title"]',
            'title',
            'h1.title',
            '.watch-main-col h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get('content', '') or element.get_text(strip=True)
        
        return "Unknown Title"
    
    def _extract_youtube_description(self, soup: BeautifulSoup) -> str:
        """Extract YouTube video description"""
        selectors = [
            'meta[property="og:description"]',
            'meta[name="description"]',
            '.watch-main-col .content',
            '#watch-description-text'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get('content', '') or element.get_text(strip=True)
        
        return ""
    
    def _extract_youtube_views(self, soup: BeautifulSoup) -> int:
        """Extract view count from YouTube video"""
        # Look for view count in various places
        view_patterns = [
            r'(\d+(?:,\d+)*)\s*views?',
            r'viewCount.*?(\d+)',
            r'"viewCount":"(\d+)"'
        ]
        
        content = str(soup)
        for pattern in view_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1).replace(',', ''))
                except:
                    continue
        
        return 0
    
    def _extract_youtube_likes(self, soup: BeautifulSoup) -> int:
        """Extract like count from YouTube video"""
        like_patterns = [
            r'"likeCount":"(\d+)"',
            r'likeCount.*?(\d+)',
            r'(\d+(?:,\d+)*)\s*likes?'
        ]
        
        content = str(soup)
        for pattern in like_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1).replace(',', ''))
                except:
                    continue
        
        return 0
    
    def _extract_youtube_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract tags from YouTube video"""
        tags = []
        
        # Look for keywords meta tag
        keywords_meta = soup.find('meta', {'name': 'keywords'})
        if keywords_meta:
            content = keywords_meta.get('content', '')
            tags = [tag.strip() for tag in content.split(',') if tag.strip()]
        
        return tags
    
    def _extract_channel_name(self, soup: BeautifulSoup) -> str:
        """Extract YouTube channel name"""
        selectors = [
            'meta[property="og:title"]',
            '.channel-header-profile-image-container + .branded-page-header-title-link',
            '.ytd-channel-name a',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get('content', '') or element.get_text(strip=True)
                if text and 'YouTube' not in text:
                    return text
        
        return "Unknown Channel"
    
    def _extract_subscriber_count(self, soup: BeautifulSoup) -> int:
        """Extract subscriber count from YouTube channel"""
        patterns = [
            r'(\d+(?:\.\d+)?[KMB]?)\s*subscribers?',
            r'"subscriberCountText".*?"(\d+(?:\.\d+)?[KMB]?)"',
        ]
        
        content = str(soup)
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                count_str = match.group(1)
                return self._parse_count(count_str)
        
        return 0
    
    def _extract_channel_videos(self, soup: BeautifulSoup, channel_url: str) -> List[Dict]:
        """Extract recent videos from channel page"""
        videos = []
        
        # Look for video links
        video_links = soup.find_all('a', {'href': re.compile(r'/watch\?v=')})
        
        for link in video_links[:20]:  # Limit to first 20 videos
            href = link.get('href', '')
            if href.startswith('/watch'):
                video_url = 'https://www.youtube.com' + href
                title = link.get('title', '') or link.get_text(strip=True)
                
                if title and len(title) > 5:  # Filter out empty or very short titles
                    videos.append({
                        'title': title,
                        'url': video_url,
                        'id': self._extract_video_id_from_url(video_url)
                    })
        
        return videos
    
    def _extract_website_title(self, soup: BeautifulSoup) -> str:
        """Extract website title"""
        selectors = [
            'meta[property="og:title"]',
            'meta[name="title"]',
            'title',
            'h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get('content', '') or element.get_text(strip=True)
        
        return "Unknown Title"
    
    def _extract_website_description(self, soup: BeautifulSoup) -> str:
        """Extract website description"""
        selectors = [
            'meta[property="og:description"]',
            'meta[name="description"]',
            'meta[name="Description"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get('content', '')
        
        return ""
    
    def _extract_website_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract website keywords"""
        keywords_meta = soup.find('meta', {'name': 'keywords'})
        if keywords_meta:
            content = keywords_meta.get('content', '')
            return [kw.strip() for kw in content.split(',') if kw.strip()]
        
        return []
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract all headings"""
        headings = {}
        for i in range(1, 7):
            tag = f'h{i}'
            elements = soup.find_all(tag)
            headings[tag] = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
        
        return headings
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract image URLs"""
        images = soup.find_all('img')
        return [img.get('src', '') for img in images if img.get('src')]
    
    def _extract_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract all links"""
        links = soup.find_all('a')
        return [link.get('href', '') for link in links if link.get('href')]
    
    def _analyze_content_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze website content structure"""
        return {
            'paragraphs': len(soup.find_all('p')),
            'lists': len(soup.find_all(['ul', 'ol'])),
            'tables': len(soup.find_all('table')),
            'forms': len(soup.find_all('form')),
            'scripts': len(soup.find_all('script')),
            'stylesheets': len(soup.find_all('link', {'rel': 'stylesheet'}))
        }
    
    def _analyze_website_seo(self, soup: BeautifulSoup) -> Dict:
        """Basic SEO analysis of website"""
        title = soup.find('title')
        description = soup.find('meta', {'name': 'description'})
        h1_tags = soup.find_all('h1')
        
        return {
            'has_title': bool(title),
            'title_length': len(title.get_text()) if title else 0,
            'has_meta_description': bool(description),
            'meta_description_length': len(description.get('content', '')) if description else 0,
            'h1_count': len(h1_tags),
            'has_og_tags': bool(soup.find('meta', {'property': re.compile(r'^og:')})),
            'has_twitter_cards': bool(soup.find('meta', {'name': re.compile(r'^twitter:')}))
        }
    
    def _parse_count(self, count_str: str) -> int:
        """Parse count string like '1.2M' to integer"""
        count_str = count_str.upper().strip()
        
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        for suffix, multiplier in multipliers.items():
            if count_str.endswith(suffix):
                number = float(count_str[:-1])
                return int(number * multiplier)
        
        try:
            return int(float(count_str))
        except:
            return 0
    
    def _extract_video_id_from_url(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'watch\?v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'embed/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ""
    
    def get_channel_videos_detailed(self, videos: List[Dict], max_videos: int = 20) -> List[Dict]:
        """Get detailed information for channel videos"""
        detailed_videos = []
        
        for i, video in enumerate(videos[:max_videos]):
            if 'url' in video:
                try:
                    detailed_info = self._analyze_youtube_video(video['url'])
                    if 'error' not in detailed_info:
                        detailed_videos.append(detailed_info)
                    else:
                        # Add basic info if detailed extraction fails
                        detailed_videos.append({
                            'title': video.get('title', ''),
                            'id': video.get('id', ''),
                            'webpage_url': video.get('url', ''),
                            'view_count': 0,
                            'like_count': 0,
                            'comment_count': 0,
                            'description': '',
                            'tags': []
                        })
                except Exception as e:
                    logger.error(f"Error getting detailed info for video {i+1}: {e}")
                    continue
        
        return detailed_videos
    
    def __del__(self):
        """Cleanup selenium driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
