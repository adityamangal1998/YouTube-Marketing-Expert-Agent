import os
import re
from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import isodate

load_dotenv()

class YouTubeAPI:
    """YouTube Data API v3 wrapper"""
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = None
        if self.api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                print(f"Error initializing YouTube API: {e}")
    
    def is_configured(self) -> bool:
        """Check if YouTube API is properly configured"""
        return self.youtube is not None and self.api_key is not None
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Get basic channel information"""
        if not self.is_configured():
            return None
        
        try:
            request = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                id=channel_id
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]
            return None
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return None
    
    def get_channel_id_from_username(self, username: str) -> Optional[str]:
        """Get channel ID from username"""
        if not self.is_configured():
            return None
        
        try:
            request = self.youtube.channels().list(
                part='id',
                forUsername=username
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]['id']
            return None
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return None
    
    def search_channel_by_handle(self, handle: str) -> Optional[str]:
        """Search for channel by handle (@username)"""
        if not self.is_configured():
            return None
        
        try:
            # Remove @ if present
            handle = handle.lstrip('@')
            
            request = self.youtube.search().list(
                part='snippet',
                q=handle,
                type='channel',
                maxResults=5
            )
            response = request.execute()
            
            # Look for exact match or close match
            for item in response['items']:
                channel_title = item['snippet']['title'].lower()
                if handle.lower() in channel_title or channel_title in handle.lower():
                    return item['snippet']['channelId']
            
            # If no close match, return the first result
            if response['items']:
                return response['items'][0]['snippet']['channelId']
            
            return None
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return None
    
    def get_channel_videos(self, channel_id: str, max_results: int = 20, include_shorts: bool = True) -> List[Dict]:
        """Get videos from a channel"""
        if not self.is_configured():
            return []
        
        try:
            # First, get the uploads playlist ID
            channel_request = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            channel_response = channel_request.execute()
            
            if not channel_response['items']:
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                playlist_request = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                )
                playlist_response = playlist_request.execute()
                
                video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]
                
                # Get detailed video information
                videos_request = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(video_ids)
                )
                videos_response = videos_request.execute()
                
                for video in videos_response['items']:
                    video_data = self._process_video_data(video)
                    
                    # Filter shorts if not included
                    if not include_shorts and self._is_short_video(video_data['duration']):
                        continue
                    
                    videos.append(video_data)
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return videos[:max_results]
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return []
    
    def _process_video_data(self, video: Dict) -> Dict:
        """Process raw video data from YouTube API"""
        snippet = video['snippet']
        statistics = video.get('statistics', {})
        content_details = video.get('contentDetails', {})
        
        # Parse duration
        duration_iso = content_details.get('duration', 'PT0S')
        duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())
        duration_formatted = self._format_duration(duration_seconds)
        
        # Get thumbnail URL
        thumbnails = snippet.get('thumbnails', {})
        thumbnail_url = (
            thumbnails.get('maxres', {}).get('url') or
            thumbnails.get('high', {}).get('url') or
            thumbnails.get('medium', {}).get('url') or
            thumbnails.get('default', {}).get('url', '')
        )
        
        return {
            'id': video['id'],
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'tags': snippet.get('tags', []),
            'publishedAt': snippet.get('publishedAt', ''),
            'thumbnail': thumbnail_url,
            'duration': duration_formatted,
            'duration_seconds': duration_seconds,
            'viewCount': int(statistics.get('viewCount', 0)),
            'likeCount': int(statistics.get('likeCount', 0)),
            'commentCount': int(statistics.get('commentCount', 0)),
            'categoryId': snippet.get('categoryId', ''),
        }
    
    def _is_short_video(self, duration: str) -> bool:
        """Check if video is a YouTube Short (under 60 seconds)"""
        # Parse duration string like "1:30" or "0:45"
        try:
            parts = duration.split(':')
            if len(parts) == 2:
                minutes, seconds = int(parts[0]), int(parts[1])
                total_seconds = minutes * 60 + seconds
                return total_seconds <= 60
            elif len(parts) == 3:
                hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                return hours == 0 and minutes == 0 and seconds <= 60
        except:
            pass
        return False
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to HH:MM:SS or MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict]:
        """Get comments for a video"""
        if not self.is_configured():
            return []
        
        try:
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                order='relevance'
            )
            response = request.execute()
            
            comments = []
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'text': comment['textDisplay'],
                    'author': comment['authorDisplayName'],
                    'likeCount': comment['likeCount'],
                    'publishedAt': comment['publishedAt']
                })
            
            return comments
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return []
