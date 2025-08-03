#!/usr/bin/env python3
"""
Demo script to showcase the YouTube Marketing Expert Agent functionality
"""

from web_scraper import WebScraper
from ai_analyzer import AIAnalyzer
import json

def demo_web_scraper():
    """Demonstrate web scraping functionality"""
    print("🎬 YouTube Marketing Expert Agent - Demo")
    print("="*50)
    
    scraper = WebScraper()
    ai_analyzer = AIAnalyzer()
    
    # Test URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Famous Rick Roll video
        "https://www.example.com",  # Simple website
        "https://www.youtube.com/@Google"  # Google's YouTube channel
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing URL: {url}")
        print("-" * 40)
        
        try:
            result = scraper.analyze_url(url)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            content_type = result.get('type', 'unknown')
            print(f"✅ Content Type: {content_type}")
            
            if content_type == 'video':
                print(f"📹 Title: {result.get('title', 'N/A')}")
                print(f"👁️ Views: {result.get('view_count', 0):,}")
                print(f"👍 Likes: {result.get('like_count', 0):,}")
                
            elif content_type == 'channel':
                print(f"📺 Channel: {result.get('channel_name', 'N/A')}")
                print(f"👥 Subscribers: {result.get('subscriber_count', 0):,}")
                print(f"🎥 Videos Found: {len(result.get('videos', []))}")
                
            elif content_type == 'website':
                print(f"🌐 Title: {result.get('title', 'N/A')}")
                print(f"📝 Description Length: {len(result.get('description', ''))}")
                print(f"🏷️ Keywords: {len(result.get('keywords', []))}")
            
            # Test AI analysis in mock mode
            if content_type in ['video', 'channel']:
                print("🤖 Testing AI Analysis (Mock Mode)...")
                
                if content_type == 'video':
                    suggestions = ai_analyzer.analyze_video(result)
                else:
                    # Test with first video if it's a channel
                    videos = result.get('videos', [])
                    if videos:
                        first_video_url = videos[0].get('url', '')
                        if first_video_url:
                            video_data = scraper.analyze_url(first_video_url)
                            if 'error' not in video_data:
                                suggestions = ai_analyzer.analyze_video(video_data)
                            else:
                                suggestions = None
                        else:
                            suggestions = None
                    else:
                        suggestions = None
                
                if suggestions:
                    print("✅ AI Analysis Complete:")
                    if suggestions.get('improved_title'):
                        print(f"   💡 Better Title: {suggestions['improved_title'][:100]}...")
                    if suggestions.get('content_ideas'):
                        print(f"   💭 Content Ideas: {len(suggestions['content_ideas'])} generated")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("\n" + "="*50)
    print("🎉 Demo Complete!")
    print("The application is ready to use. Open http://localhost:8502 in your browser.")

if __name__ == "__main__":
    demo_web_scraper()
