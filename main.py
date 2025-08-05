import streamlit as st
import pandas as pd
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from web_scraper import WebScraper
from ai_analyzer import AIAnalyzer
from utils import format_number, validate_url, clean_text, truncate_text
import time

# Page configuration
st.set_page_config(
    page_title="YouTube Marketing Expert Agent",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .stExpander {
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    .suggestion-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #0066cc;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.title("📺 YouTube Marketing Expert Agent")
    st.markdown("### Analyze your YouTube channel and get AI-powered optimization suggestions")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Status
        web_scraper = WebScraper()
        ai_analyzer = AIAnalyzer()
        
        scraper_status = "✅ Ready" if web_scraper.is_configured() else "❌ Not available"
        ai_status = "✅ Connected" if ai_analyzer.is_configured() else "❌ Not configured"
        
        st.info(f"**Web Scraper:** {scraper_status}")
        st.info(f"**AWS Bedrock:** {ai_status}")
        
        # Analysis options
        st.subheader("Analysis Options")
        max_videos = st.slider("Max videos to analyze", 1, 50, 1)
        include_shorts = st.checkbox("Include YouTube Shorts", value=True)
        detailed_analysis = st.checkbox("Detailed AI analysis", value=True)
        use_selenium = st.checkbox("Use advanced scraping (slower)", value=False)
        
        # Export options
        st.subheader("Export Options")
        export_json = st.checkbox("Export as JSON", value=False)
        export_pdf = st.checkbox("Export as PDF", value=False)
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # URL input
        st.subheader("🔗 Enter Any URL")
        url_input = st.text_input(
            "Website or YouTube URL",
            placeholder="https://www.youtube.com/@channelname or https://example.com",
            help="Enter any website URL or YouTube channel/video URL for analysis"
        )
        
        analyze_button = st.button("🚀 Analyze Content", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("📊 Quick Stats")
        if 'analysis_results' in st.session_state:
            results = st.session_state.analysis_results
            content_type = results.get('content_type', 'unknown')
            
            if content_type == 'channel':
                channel_info = results.get('channel_info', {})
                st.metric("Total Videos", format_number(results['summary']['total_videos']))
                st.metric("Subscriber Count", format_number(channel_info.get('subscriber_count', 0)))
            elif content_type == 'video':
                video = results['videos'][0] if results['videos'] else {}
                st.metric("Views", format_number(video.get('views', 0)))
                st.metric("Engagement", f"{video.get('engagement_rate', 0):.1f}%")
            elif content_type == 'website':
                st.metric("Title Length", results['summary']['title_length'])
                st.metric("Images", results['summary']['images_count'])
    
    # Analysis section
    if analyze_button and url_input:
        if not validate_url(url_input):
            st.error("❌ Invalid URL. Please enter a valid website URL.")
            return
        
        # Check scraper availability
        if not web_scraper.is_configured():
            st.error("❌ Web scraper is not available.")
            return
        
        # Analyze the URL
        analyze_url(web_scraper, ai_analyzer, url_input, max_videos, include_shorts, detailed_analysis, use_selenium)
    
    # Display results if available
    if 'analysis_results' in st.session_state:
        display_analysis_results(st.session_state.analysis_results, export_json, export_pdf)

def analyze_url(web_scraper: WebScraper, ai_analyzer: AIAnalyzer, url: str, max_videos: int, include_shorts: bool, detailed_analysis: bool, use_selenium: bool):
    """Main analysis function for any URL"""
    
    with st.spinner("🔍 Analyzing URL..."):
        # Analyze the URL
        url_data = web_scraper.analyze_url(url)
        if 'error' in url_data:
            st.error(f"❌ Error analyzing URL: {url_data['error']}")
            return
        
        content_type = url_data.get('type', 'unknown')
        
        if content_type == 'video':
            analyze_single_video(url_data, ai_analyzer, detailed_analysis)
        elif content_type == 'channel':
            analyze_youtube_channel(web_scraper, ai_analyzer, url_data, max_videos, include_shorts, detailed_analysis, use_selenium)
        elif content_type == 'website':
            analyze_website(url_data, ai_analyzer, detailed_analysis)
        else:
            st.error("❌ Unsupported content type or could not determine content type.")

def analyze_single_video(video_data: Dict, ai_analyzer: AIAnalyzer, detailed_analysis: bool):
    """Analyze a single YouTube video"""
    
    st.success(f"✅ Found video: **{video_data.get('title', 'Unknown Title')}**")
    
    # Store results for display
    analysis_results = {
        'content_type': 'video',
        'video_info': video_data,
        'videos': [analyze_video_basic(video_data)],
        'summary': {
            'total_videos': 1,
            'total_views': video_data.get('view_count', 0),
            'optimization_opportunities': 0
        }
    }
    
    # AI analysis if enabled
    if detailed_analysis and ai_analyzer.is_configured():
        with st.spinner("🤖 Generating AI suggestions..."):
            ai_suggestions = ai_analyzer.analyze_video(video_data)
            analysis_results['videos'][0]['ai_suggestions'] = ai_suggestions
    
    # Calculate summary stats
    calculate_summary_stats(analysis_results)
    
    st.session_state.analysis_results = analysis_results

def analyze_youtube_channel(web_scraper: WebScraper, ai_analyzer: AIAnalyzer, channel_data: Dict, max_videos: int, include_shorts: bool, detailed_analysis: bool, use_selenium: bool):
    """Analyze YouTube channel"""
    
    channel_name = channel_data.get('channel_name', 'Unknown Channel')
    st.success(f"✅ Found channel: **{channel_name}**")
    
    videos = channel_data.get('videos', [])
    if not videos:
        st.warning("⚠️ No videos found in channel")
        return
    
    st.success(f"✅ Found {len(videos)} videos")
    
    # Get detailed video information
    with st.spinner("📹 Fetching detailed video information..."):
        detailed_videos = web_scraper.get_channel_videos_detailed(videos, max_videos)
    
    if not detailed_videos:
        st.error("❌ Could not get detailed video information")
        return
    
    # Analyze videos
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    analysis_results = {
        'content_type': 'channel',
        'channel_info': channel_data,
        'videos': [],
        'summary': {
            'total_videos': len(detailed_videos),
            'total_views': 0,
            'avg_engagement': 0,
            'top_performing': None,
            'optimization_opportunities': 0
        }
    }
    
    for i, video in enumerate(detailed_videos):
        progress = (i + 1) / len(detailed_videos)
        progress_bar.progress(progress)
        status_text.text(f"Analyzing video {i+1}/{len(detailed_videos)}: {truncate_text(video.get('title', ''), 50)}")
        
        # Basic analysis
        video_analysis = analyze_video_basic(video)
        
        # AI analysis if enabled
        if detailed_analysis and ai_analyzer.is_configured():
            ai_suggestions = ai_analyzer.analyze_video(video)
            video_analysis['ai_suggestions'] = ai_suggestions
        
        analysis_results['videos'].append(video_analysis)
        analysis_results['summary']['total_views'] += video_analysis['views']
        
        # Small delay to prevent overwhelming the system
        time.sleep(0.1)
    
    # Calculate summary statistics
    calculate_summary_stats(analysis_results)
    
    progress_bar.progress(1.0)
    status_text.text("✅ Analysis complete!")
    
    st.session_state.analysis_results = analysis_results
    
    # Clear progress indicators after a short delay
    time.sleep(1)
    progress_bar.empty()
    status_text.empty()

def analyze_website(website_data: Dict, ai_analyzer: AIAnalyzer, detailed_analysis: bool):
    """Analyze a general website"""
    
    title = website_data.get('title', 'Unknown Website')
    st.success(f"✅ Analyzed website: **{title}**")
    
    # Create analysis results for website
    analysis_results = {
        'content_type': 'website',
        'website_info': website_data,
        'seo_analysis': website_data.get('seo_analysis', {}),
        'content_analysis': website_data.get('content_analysis', {}),
        'summary': {
            'title_length': len(title),
            'description_length': len(website_data.get('description', '')),
            'headings_count': sum(len(h) for h in website_data.get('headings', {}).values()),
            'images_count': website_data.get('images', 0),
            'links_count': website_data.get('links', 0)
        }
    }
    
    # AI analysis for website optimization
    if detailed_analysis and ai_analyzer.is_configured():
        with st.spinner("🤖 Generating website optimization suggestions..."):
            # Create a pseudo-video object for AI analysis
            pseudo_video = {
                'title': title,
                'description': website_data.get('description', ''),
                'tags': website_data.get('keywords', []),
                'viewCount': 0,
                'likeCount': 0,
                'commentCount': 0,
                'duration': '0:00'
            }
            ai_suggestions = ai_analyzer.analyze_video(pseudo_video)
            analysis_results['ai_suggestions'] = ai_suggestions
    
    st.session_state.analysis_results = analysis_results

def analyze_video_basic(video: Dict) -> Dict:
    """Perform basic video analysis"""
    
    title = video.get('title', '')
    description = video.get('description', '')
    tags = video.get('tags', [])
    views = int(video.get('view_count', 0) or video.get('viewCount', 0))
    likes = int(video.get('like_count', 0) or video.get('likeCount', 0))
    comments = int(video.get('comment_count', 0) or video.get('commentCount', 0))
    duration = str(video.get('duration', '0:00'))
    
    # Calculate engagement metrics
    engagement_rate = (likes + comments) / max(views, 1) * 100
    
    # Title analysis
    title_analysis = {
        'length': len(title),
        'word_count': len(title.split()),
        'has_numbers': bool(re.search(r'\d', title)),
        'has_caps': bool(re.search(r'[A-Z]', title)),
        'has_question': '?' in title,
        'has_exclamation': '!' in title,
        'keyword_density': calculate_keyword_density(title)
    }
    
    # Description analysis
    desc_analysis = {
        'length': len(description),
        'word_count': len(description.split()),
        'has_links': bool(re.search(r'http[s]?://', description)),
        'has_timestamps': bool(re.search(r'\d{1,2}:\d{2}', description)),
        'has_hashtags': bool(re.search(r'#\w+', description)),
        'line_count': len(description.split('\n'))
    }
    
    # Tags analysis
    tags_analysis = {
        'count': len(tags),
        'total_characters': sum(len(str(tag)) for tag in tags),
        'avg_length': sum(len(str(tag)) for tag in tags) / max(len(tags), 1),
        'unique_words': len(set(' '.join(str(tag) for tag in tags).lower().split()))
    }
    
    # Basic optimization score
    optimization_score = calculate_optimization_score(title_analysis, desc_analysis, tags_analysis)
    
    return {
        'video_id': video.get('id', ''),
        'title': title,
        'description': description,
        'tags': tags,
        'views': views,
        'likes': likes,
        'comments': comments,
        'engagement_rate': engagement_rate,
        'duration': duration,
        'published_at': video.get('publishedAt', '') or video.get('upload_date', ''),
        'thumbnail': video.get('thumbnail', ''),
        'url': video.get('webpage_url', ''),
        'title_analysis': title_analysis,
        'description_analysis': desc_analysis,
        'tags_analysis': tags_analysis,
        'optimization_score': optimization_score,
        'basic_suggestions': generate_basic_suggestions(title_analysis, desc_analysis, tags_analysis)
    }

def calculate_keyword_density(text: str) -> Dict:
    """Calculate keyword density for text"""
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return {}
    
    word_count = {}
    for word in words:
        if len(word) > 3:  # Only count words longer than 3 characters
            word_count[word] = word_count.get(word, 0) + 1
    
    total_words = len(words)
    return {word: (count / total_words) * 100 for word, count in word_count.items()}

def calculate_optimization_score(title_analysis: Dict, desc_analysis: Dict, tags_analysis: Dict) -> float:
    """Calculate basic optimization score"""
    score = 0
    max_score = 100
    
    # Title scoring (40 points max)
    if 40 <= title_analysis['length'] <= 60:
        score += 15
    if title_analysis['has_numbers']:
        score += 5
    if title_analysis['has_question'] or title_analysis['has_exclamation']:
        score += 10
    if 6 <= title_analysis['word_count'] <= 10:
        score += 10
    
    # Description scoring (35 points max)
    if desc_analysis['length'] >= 200:
        score += 15
    if desc_analysis['has_links']:
        score += 5
    if desc_analysis['has_timestamps']:
        score += 5
    if desc_analysis['has_hashtags']:
        score += 5
    if desc_analysis['line_count'] >= 3:
        score += 5
    
    # Tags scoring (25 points max)
    if tags_analysis['count'] >= 5:
        score += 10
    if tags_analysis['count'] <= 15:
        score += 10
    if 5 <= tags_analysis['avg_length'] <= 20:
        score += 5
    
    return min(score, max_score)

def generate_basic_suggestions(title_analysis: Dict, desc_analysis: Dict, tags_analysis: Dict) -> List[str]:
    """Generate basic optimization suggestions"""
    suggestions = []
    
    # Title suggestions
    if title_analysis['length'] < 40:
        suggestions.append("Consider making your title longer (40-60 characters) for better SEO")
    elif title_analysis['length'] > 60:
        suggestions.append("Consider shortening your title (40-60 characters) for better visibility")
    
    if not title_analysis['has_numbers']:
        suggestions.append("Adding numbers to titles often increases click-through rates")
    
    if not (title_analysis['has_question'] or title_analysis['has_exclamation']):
        suggestions.append("Consider adding emotional triggers (? or !) to your title")
    
    # Description suggestions
    if desc_analysis['length'] < 200:
        suggestions.append("Write a more detailed description (at least 200 characters) for better SEO")
    
    if not desc_analysis['has_links']:
        suggestions.append("Add relevant links in your description to increase engagement")
    
    if not desc_analysis['has_timestamps']:
        suggestions.append("Consider adding timestamps for better user experience")
    
    if not desc_analysis['has_hashtags']:
        suggestions.append("Add relevant hashtags to increase discoverability")
    
    # Tags suggestions
    if tags_analysis['count'] < 5:
        suggestions.append("Add more tags (5-15 recommended) to improve discoverability")
    elif tags_analysis['count'] > 15:
        suggestions.append("Reduce the number of tags to focus on most relevant keywords")
    
    return suggestions

def calculate_summary_stats(analysis_results: Dict):
    """Calculate summary statistics"""
    videos = analysis_results['videos']
    if not videos:
        return
    
    # Find top performing video
    top_video = max(videos, key=lambda x: x['engagement_rate'])
    analysis_results['summary']['top_performing'] = top_video
    
    # Calculate average engagement
    avg_engagement = sum(v['engagement_rate'] for v in videos) / len(videos)
    analysis_results['summary']['avg_engagement'] = avg_engagement
    
    # Count optimization opportunities
    opportunities = sum(len(v['basic_suggestions']) for v in videos)
    analysis_results['summary']['optimization_opportunities'] = opportunities

def display_analysis_results(results: Dict, export_json: bool, export_pdf: bool):
    """Display analysis results"""
    
    content_type = results.get('content_type', 'unknown')
    
    st.header("📊 Analysis Results")
    
    if content_type == 'video':
        display_video_results(results)
    elif content_type == 'channel':
        display_channel_results(results)
    elif content_type == 'website':
        display_website_results(results)
    else:
        st.error("Unknown content type")
        return
    
    # Export options
    if export_json or export_pdf:
        st.subheader("💾 Export Results")
        export_results(results, export_json, export_pdf)

def display_video_results(results: Dict):
    """Display results for single video analysis"""
    
    video_info = results.get('video_info', {})
    video_analysis = results['videos'][0] if results['videos'] else {}
    
    # Video overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Views", format_number(video_analysis.get('views', 0)))
    with col2:
        st.metric("Likes", format_number(video_analysis.get('likes', 0)))
    with col3:
        st.metric("Comments", format_number(video_analysis.get('comments', 0)))
    with col4:
        st.metric("Engagement Rate", f"{video_analysis.get('engagement_rate', 0):.2f}%")
    
    # Display detailed analysis
    with st.expander(f"📹 {video_analysis.get('title', 'Video Analysis')}", expanded=True):
        display_video_analysis(video_analysis)

def display_channel_results(results: Dict):
    """Display results for channel analysis"""
    
    # Channel overview
    channel_info = results.get('channel_info', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Videos", format_number(results['summary']['total_videos']))
    with col2:
        st.metric("Total Views", format_number(results['summary']['total_views']))
    with col3:
        st.metric("Avg Engagement", f"{results['summary']['avg_engagement']:.2f}%")
    with col4:
        st.metric("Optimization Opportunities", results['summary']['optimization_opportunities'])
    
    # Performance overview chart
    if len(results['videos']) > 1:
        st.subheader("📈 Performance Overview")
        
        videos_data = []
        for video in results['videos']:
            videos_data.append({
                'Title': truncate_text(video['title'], 30),
                'Views': video['views'],
                'Engagement Rate': video['engagement_rate'],
                'Optimization Score': video['optimization_score']
            })
        
        df = pd.DataFrame(videos_data)
        
        # Create performance chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Views'],
            y=df['Engagement Rate'],
            mode='markers',
            marker=dict(
                size=df['Optimization Score'] / 5,
                color=df['Optimization Score'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Optimization Score")
            ),
            text=df['Title'],
            hovertemplate='<b>%{text}</b><br>Views: %{x}<br>Engagement: %{y:.2f}%<br>Score: %{marker.color}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Video Performance vs Optimization Score",
            xaxis_title="Views",
            yaxis_title="Engagement Rate (%)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Individual video analysis
    st.subheader("🎥 Individual Video Analysis")
    
    for i, video in enumerate(results['videos']):
        with st.expander(f"📹 {video['title']}", expanded=i < 3):
            display_video_analysis(video)

def display_website_results(results: Dict):
    """Display results for website analysis"""
    
    website_info = results.get('website_info', {})
    
    # Website overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Title Length", results['summary']['title_length'])
    with col2:
        st.metric("Description Length", results['summary']['description_length'])
    with col3:
        st.metric("Headings", results['summary']['headings_count'])
    with col4:
        st.metric("Images", results['summary']['images_count'])
    
    # SEO Analysis
    st.subheader("🔍 SEO Analysis")
    seo_analysis = website_info.get('seo_analysis', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Basic SEO Elements**")
        st.write(f"Has Title: {'✅' if seo_analysis.get('has_title') else '❌'}")
        st.write(f"Title Length: {seo_analysis.get('title_length', 0)} chars")
        st.write(f"Has Meta Description: {'✅' if seo_analysis.get('has_meta_description') else '❌'}")
        st.write(f"Description Length: {seo_analysis.get('meta_description_length', 0)} chars")
    
    with col2:
        st.markdown("**Social Media**")
        st.write(f"H1 Tags: {seo_analysis.get('h1_count', 0)}")
        st.write(f"Open Graph Tags: {'✅' if seo_analysis.get('has_og_tags') else '❌'}")
        st.write(f"Twitter Cards: {'✅' if seo_analysis.get('has_twitter_cards') else '❌'}")
    
    # Content Analysis
    st.subheader("📄 Content Structure")
    content_analysis = website_info.get('content_analysis', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Paragraphs", content_analysis.get('paragraphs', 0))
        st.metric("Lists", content_analysis.get('lists', 0))
    
    with col2:
        st.metric("Tables", content_analysis.get('tables', 0))
        st.metric("Forms", content_analysis.get('forms', 0))
    
    with col3:
        st.metric("Scripts", content_analysis.get('scripts', 0))
        st.metric("Stylesheets", content_analysis.get('stylesheets', 0))
    
    # Headings Structure
    headings = website_info.get('headings', {})
    if any(headings.values()):
        st.subheader("� Headings Structure")
        for tag, heading_list in headings.items():
            if heading_list:
                st.markdown(f"**{tag.upper()}** ({len(heading_list)} found)")
                for heading in heading_list[:5]:  # Show first 5
                    st.write(f"• {truncate_text(heading, 80)}")
                if len(heading_list) > 5:
                    st.write(f"... and {len(heading_list) - 5} more")
    
    # AI Suggestions for website
    if 'ai_suggestions' in results:
        st.subheader("🤖 AI-Powered Website Optimization")
        ai_suggestions = results['ai_suggestions']
        
        if ai_suggestions.get('improved_title'):
            st.markdown("**Better Title:**")
            st.info(ai_suggestions['improved_title'])
        
        if ai_suggestions.get('improved_description'):
            st.markdown("**Better Meta Description:**")
            st.info(ai_suggestions['improved_description'])
        
        if ai_suggestions.get('suggested_tags'):
            st.markdown("**Suggested Keywords:**")
            st.info(", ".join(ai_suggestions['suggested_tags']))
        
        if ai_suggestions.get('content_ideas'):
            st.markdown("**Content Improvement Ideas:**")
            for idea in ai_suggestions['content_ideas']:
                st.markdown(f"• {idea}")

def display_video_analysis(video: Dict):
    """Display individual video analysis"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Basic metrics
        st.markdown("**📊 Metrics**")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Views", format_number(video['views']))
        with metric_col2:
            st.metric("Likes", format_number(video['likes']))
        with metric_col3:
            st.metric("Comments", format_number(video['comments']))
        
        st.metric("Engagement Rate", f"{video['engagement_rate']:.2f}%")
        st.metric("Optimization Score", f"{video['optimization_score']}/100")
    
    with col2:
        # Thumbnail
        if video.get('thumbnail'):
            st.image(video['thumbnail'], width=200)
    
    # Analysis details
    st.markdown("**🔍 Analysis Details**")
    
    analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
    
    with analysis_col1:
        st.markdown("**Title Analysis**")
        title_analysis = video['title_analysis']
        st.write(f"Length: {title_analysis['length']} chars")
        st.write(f"Words: {title_analysis['word_count']}")
        st.write(f"Has numbers: {'✅' if title_analysis['has_numbers'] else '❌'}")
        st.write(f"Has question/exclamation: {'✅' if title_analysis['has_question'] or title_analysis['has_exclamation'] else '❌'}")
    
    with analysis_col2:
        st.markdown("**Description Analysis**")
        desc_analysis = video['description_analysis']
        st.write(f"Length: {desc_analysis['length']} chars")
        st.write(f"Words: {desc_analysis['word_count']}")
        st.write(f"Has links: {'✅' if desc_analysis['has_links'] else '❌'}")
        st.write(f"Has timestamps: {'✅' if desc_analysis['has_timestamps'] else '❌'}")
    
    with analysis_col3:
        st.markdown("**Tags Analysis**")
        tags_analysis = video['tags_analysis']
        st.write(f"Count: {tags_analysis['count']}")
        st.write(f"Total chars: {tags_analysis['total_characters']}")
        st.write(f"Avg length: {tags_analysis['avg_length']:.1f}")
        st.write(f"Unique words: {tags_analysis['unique_words']}")
    
    # Basic suggestions
    if video['basic_suggestions']:
        st.markdown("**💡 Basic Suggestions**")
        for suggestion in video['basic_suggestions']:
            st.markdown(f"• {suggestion}")
    
    # AI suggestions if available
    if 'ai_suggestions' in video and video['ai_suggestions']:
        st.markdown("**🤖 AI-Powered Suggestions**")
        ai_suggestions = video['ai_suggestions']
        
        if ai_suggestions.get('improved_title'):
            st.markdown("**Better Title:**")
            st.info(ai_suggestions['improved_title'])
        
        if ai_suggestions.get('improved_description'):
            st.markdown("**Better Description:**")
            st.info(ai_suggestions['improved_description'])
        
        if ai_suggestions.get('suggested_tags'):
            st.markdown("**Suggested Tags:**")
            st.info(", ".join(ai_suggestions['suggested_tags']))
        
        if ai_suggestions.get('content_ideas'):
            st.markdown("**Content Ideas:**")
            for idea in ai_suggestions['content_ideas']:
                st.markdown(f"• {idea}")

    # Deep analysis button
    if st.button("🔬 Get Deep Analysis", key=f"deep_analysis_button_{video['video_id']}"):
        with st.spinner("🧠 Performing deep analysis..."):
            ai_analyzer = AIAnalyzer()
            deep_analysis = ai_analyzer.get_deep_analysis(video)
            st.session_state[f"deep_analysis_content_{video['video_id']}"] = deep_analysis.get('deep_analysis', 'No analysis available.')
            # No need to rerun, Streamlit's state management handles the update.

    # Display deep analysis if available
    if f"deep_analysis_content_{video['video_id']}" in st.session_state:
        st.markdown("---")
        st.markdown("### 🧠 Deep Analysis & Suggestions")
        st.markdown(st.session_state[f"deep_analysis_content_{video['video_id']}"], unsafe_allow_html=True)


def export_results(results: Dict, export_json: bool, export_pdf: bool):
    """Export analysis results"""
    
    if export_json:
        json_data = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="📄 Download JSON Report",
            data=json_data,
            file_name=f"youtube_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    if export_pdf:
        # This would require implementing PDF generation
        st.info("PDF export feature coming soon!")

if __name__ == "__main__":
    main()
