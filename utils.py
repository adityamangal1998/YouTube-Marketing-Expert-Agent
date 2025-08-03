import re
from typing import Optional
from urllib.parse import urlparse, parse_qs

def format_number(num: int) -> str:
    """Format large numbers with K, M, B suffixes"""
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)

def validate_url(url: str) -> bool:
    """Validate if URL is a valid URL"""
    if not url:
        return False
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def extract_channel_id(url: str) -> Optional[str]:
    """Extract channel ID from various YouTube URL formats"""
    if not url:
        return None
    
    # Parse URL
    parsed = urlparse(url)
    
    # Handle different URL formats
    if 'youtube.com' in parsed.netloc:
        path = parsed.path
        
        # Format: /channel/UCxxxx
        if path.startswith('/channel/'):
            return path.split('/channel/')[1].split('/')[0]
        
        # Format: /c/channelname or /user/username
        elif path.startswith('/c/') or path.startswith('/user/'):
            # These need to be resolved via API
            return None  # Will be handled by username lookup
        
        # Format: /@handle
        elif path.startswith('/@'):
            # This needs to be resolved via API search
            return None  # Will be handled by handle search
        
        # Format: /channelname (old format)
        elif path and len(path) > 1:
            # This might be a custom URL, needs API resolution
            return None
    
    # If we can't extract directly, return None and let API handle it
    return None

def extract_username_or_handle(url: str) -> Optional[str]:
    """Extract username or handle from YouTube URL"""
    if not url:
        return None
    
    parsed = urlparse(url)
    
    if 'youtube.com' in parsed.netloc:
        path = parsed.path
        
        # Format: /c/channelname
        if path.startswith('/c/'):
            return path.split('/c/')[1].split('/')[0]
        
        # Format: /user/username
        elif path.startswith('/user/'):
            return path.split('/user/')[1].split('/')[0]
        
        # Format: /@handle
        elif path.startswith('/@'):
            return path.split('/@')[1].split('/')[0]
        
        # Format: /channelname (old custom URL)
        elif path and len(path) > 1 and not path.startswith('/channel/'):
            return path.split('/')[1].split('/')[0]
    
    return None

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    return text

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_hashtags(text: str) -> list:
    """Extract hashtags from text"""
    if not text:
        return []
    
    hashtags = re.findall(r'#\w+', text)
    return [tag.lower() for tag in hashtags]

def extract_mentions(text: str) -> list:
    """Extract @mentions from text"""
    if not text:
        return []
    
    mentions = re.findall(r'@\w+', text)
    return [mention.lower() for mention in mentions]

def extract_urls(text: str) -> list:
    """Extract URLs from text"""
    if not text:
        return []
    
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes"""
    if not text:
        return 0
    
    word_count = len(text.split())
    reading_time = max(1, round(word_count / words_per_minute))
    return reading_time

def extract_video_id_from_url(url: str) -> Optional[str]:
    """Extract video ID from YouTube video URL"""
    if not url:
        return None
    
    # Various YouTube URL patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if secs > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{hours}h"

def parse_duration_to_seconds(duration_str: str) -> int:
    """Parse duration string (like '1:30' or '1h 30m') to seconds"""
    if not duration_str:
        return 0
    
    # Handle format like "1:30" or "1:30:45"
    if ':' in duration_str:
        parts = duration_str.split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    
    # Handle format like "1h 30m 45s"
    total_seconds = 0
    
    # Extract hours
    hours_match = re.search(r'(\d+)h', duration_str)
    if hours_match:
        total_seconds += int(hours_match.group(1)) * 3600
    
    # Extract minutes
    minutes_match = re.search(r'(\d+)m', duration_str)
    if minutes_match:
        total_seconds += int(minutes_match.group(1)) * 60
    
    # Extract seconds
    seconds_match = re.search(r'(\d+)s', duration_str)
    if seconds_match:
        total_seconds += int(seconds_match.group(1))
    
    return total_seconds

def get_engagement_category(engagement_rate: float) -> str:
    """Categorize engagement rate"""
    if engagement_rate >= 10:
        return "Excellent"
    elif engagement_rate >= 5:
        return "Good"
    elif engagement_rate >= 2:
        return "Average"
    elif engagement_rate >= 1:
        return "Below Average"
    else:
        return "Poor"

def get_optimization_category(score: float) -> str:
    """Categorize optimization score"""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Needs Improvement"
    else:
        return "Poor"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file creation"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove extra whitespace and dots
    filename = re.sub(r'\s+', '_', filename.strip())
    filename = re.sub(r'\.+', '.', filename)
    
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:195] + ('.' + ext if ext else '')
    
    return filename

def is_valid_email(email: str) -> bool:
    """Validate email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_report_filename(channel_name: str) -> str:
    """Generate a safe filename for reports"""
    from datetime import datetime
    
    # Clean channel name
    clean_name = re.sub(r'[^\w\s-]', '', channel_name)
    clean_name = re.sub(r'[-\s]+', '_', clean_name)
    
    # Add timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"youtube_analysis_{clean_name}_{timestamp}"
