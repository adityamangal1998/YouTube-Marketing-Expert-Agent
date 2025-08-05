import os
import json
import boto3
from typing import Dict, List, Optional
from dotenv import load_dotenv
import re

load_dotenv()

class AIAnalyzer:
    """AWS Bedrock AI analyzer for YouTube content optimization"""
    
    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.bedrock_client = None
        
        if self.aws_access_key and self.aws_secret_key:
            try:
                # By creating a new session, we avoid loading from the default config file
                session = boto3.Session()
                self.bedrock_client = session.client(
                    'bedrock-runtime',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.aws_region
                )
            except Exception as e:
                print(f"Error initializing AWS Bedrock client: {e}")
    
    def is_configured(self) -> bool:
        """Check if AWS Bedrock is properly configured"""
        return self.bedrock_client is not None
    
    def analyze_video(self, video: Dict) -> Dict:
        """Analyze a video and provide AI-powered suggestions"""
        if not self.is_configured():
            return self._get_mock_suggestions(video)
        
        try:
            # Prepare video data for analysis
            video_context = {
                'title': video.get('title', ''),
                'description': video.get('description', '')[:1000],  # Limit description length
                'tags': video.get('tags', []),
                'views': video.get('viewCount', 0),
                'likes': video.get('likeCount', 0),
                'comments': video.get('commentCount', 0),
                'duration': video.get('duration', ''),
            }
            
            # Get AI suggestions
            suggestions = {}
            
            # Analyze title
            improved_title = self._generate_better_title(video_context)
            if improved_title:
                suggestions['improved_title'] = improved_title
            
            # Analyze description
            improved_description = self._improve_description(video_context)
            if improved_description:
                suggestions['improved_description'] = improved_description
            
            # Suggest tags
            suggested_tags = self._suggest_tags(video_context)
            if suggested_tags:
                suggestions['suggested_tags'] = suggested_tags
            
            # Generate content ideas
            content_ideas = self._generate_content_ideas(video_context)
            if content_ideas:
                suggestions['content_ideas'] = content_ideas
            
            # SEO analysis
            seo_analysis = self._analyze_seo(video_context)
            if seo_analysis:
                suggestions['seo_analysis'] = seo_analysis
            
            return suggestions
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return self._get_mock_suggestions(video)

    def get_deep_analysis(self, video: Dict) -> Dict:
        """Generate deep analysis for a video."""
        if not self.is_configured():
            return self._get_mock_deep_analysis(video)

        try:
            video_context = {
                'title': video.get('title', ''),
                'description': video.get('description', '')[:1000],
                'tags': video.get('tags', []),
                'views': video.get('views', 0),
                'engagement_rate': video.get('engagement_rate', 0)
            }

            prompt = f"""
            Provide a deep, comprehensive analysis of this YouTube video for performance improvement.

            **Video Context:**
            - **Title:** "{video_context['title']}"
            - **Description:** "{video_context['description'][:500]}"
            - **Tags:** {", ".join(video_context['tags'])}
            - **Views:** {video_context['views']}
            - **Engagement Rate:** {video_context.get('engagement_rate', 'N/A'):.2f}%

            **Analysis Sections:**

            1.  **Title Analysis**: 
                - Critique the current title's effectiveness (clarity, SEO, click-through potential).
                - Provide 3-5 alternative, optimized titles with explanations for why they are better.

            2.  **Description Analysis**:
                - Critique the current description's structure, SEO, and call-to-actions.
                - Provide a completely rewritten, optimized description that is ready to be copied and pasted.

            3.  **Tags Analysis**:
                - Critique the current tags for relevance, mix of broad/specific keywords, and volume.
                - Provide a list of 15-20 optimized tags.

            4.  **Thumbnail Analysis**: 
                - Critique the likely thumbnail concept based on the title.
                - Suggest 3 specific, actionable improvements for the thumbnail design to increase CTR.

            5.  **Content & Pacing**: 
                - Suggest an improved structure for this type of video (e.g., hook, intro, main points, CTA, outro).
                - Provide feedback on potential pacing improvements.

            6.  **Audience Persona**: 
                - Describe the likely target audience for this video and how to better tailor the content for them.

            7.  **Engagement Strategy**: 
                - Suggest 3 specific hooks or questions to add to the video to increase likes, comments, and shares.

            8.  **Monetization Potential**: 
                - Provide 2-3 creative ideas for monetizing this specific video's content or audience.
            
            9.  **Overall Score & Summary**:
                - Provide an overall optimization score out of 100.
                - Summarize the top 3 most critical changes needed to improve performance.

            Format the entire response in Markdown. Use headings for each section.
            """
            
            response = self._call_claude(prompt)
            
            if response:
                return {'deep_analysis': response}
            else:
                return self._get_mock_deep_analysis(video)

        except Exception as e:
            print(f"Error in deep AI analysis: {e}")
            return self._get_mock_deep_analysis(video)
    
    def _generate_better_title(self, video_context: Dict) -> Optional[str]:
        """Generate a better title using Claude"""
        prompt = f"""
        Analyze this YouTube video title and suggest an improved version that will get more clicks and views.
        
        Current title: "{video_context['title']}"
        Video performance: {video_context['views']} views, {video_context['likes']} likes
        Duration: {video_context['duration']}
        
        Please suggest a better title that:
        1. Is 40-60 characters long
        2. Uses emotional triggers
        3. Includes power words
        4. Is SEO-friendly
        5. Creates curiosity or urgency
        
        Respond with just the improved title, no explanation.
        """
        
        return self._call_claude(prompt)
    
    def _improve_description(self, video_context: Dict) -> Optional[str]:
        """Improve video description using Claude"""
        current_desc = video_context['description'][:500]  # First 500 chars
        
        prompt = f"""
        Improve this YouTube video description for better SEO and engagement:
        
        Current title: "{video_context['title']}"
        Current description: "{current_desc}"
        
        Create an improved description that:
        1. Starts with a compelling hook
        2. Includes relevant keywords naturally
        3. Has proper structure with line breaks
        4. Includes call-to-action
        5. Is 200-300 words long
        6. Uses timestamps if appropriate
        
        Respond with just the improved description.
        """
        
        return self._call_claude(prompt)
    
    def _suggest_tags(self, video_context: Dict) -> Optional[List[str]]:
        """Suggest better tags using Claude"""
        current_tags = ", ".join(video_context['tags'][:10])  # First 10 tags
        
        prompt = f"""
        Suggest better YouTube tags for this video:
        
        Title: "{video_context['title']}"
        Current tags: {current_tags}
        Description snippet: "{video_context['description'][:200]}"
        
        Suggest 10-15 optimized tags that:
        1. Include the main topic
        2. Have good search volume
        3. Mix broad and specific keywords
        4. Include trending terms
        5. Are relevant to the content
        
        Respond with tags separated by commas, no explanation.
        """
        
        response = self._call_claude(prompt)
        if response:
            # Parse tags from response
            tags = [tag.strip() for tag in response.split(',')]
            return [tag for tag in tags if tag and len(tag) <= 30]  # Filter valid tags
        return None
    
    def _generate_content_ideas(self, video_context: Dict) -> Optional[List[str]]:
        """Generate content ideas using Claude"""
        prompt = f"""
        Based on this YouTube video, suggest 5 related content ideas for future videos:
        
        Video title: "{video_context['title']}"
        Description: "{video_context['description'][:300]}"
        Performance: {video_context['views']} views, {video_context['likes']} likes
        
        Suggest content ideas that:
        1. Are related to the original topic
        2. Would appeal to the same audience
        3. Have viral potential
        4. Are actionable and specific
        5. Build on successful elements
        
        Format as a numbered list, one idea per line.
        """
        
        response = self._call_claude(prompt)
        if response:
            # Parse ideas from response
            ideas = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering
                    idea = re.sub(r'^\d+\.?\s*', '', line)
                    idea = re.sub(r'^-\s*', '', idea)
                    if idea:
                        ideas.append(idea)
            return ideas[:5]
        return None
    
    def _analyze_seo(self, video_context: Dict) -> Optional[Dict]:
        """Analyze SEO aspects of the video"""
        prompt = f"""
        Analyze the SEO aspects of this YouTube video:
        
        Title: "{video_context['title']}"
        Description: "{video_context['description'][:500]}"
        Tags: {", ".join(video_context['tags'][:10])}
        
        Provide analysis on:
        1. Title SEO score (1-10)
        2. Description SEO score (1-10)
        3. Tags effectiveness (1-10)
        4. Main keywords identified
        5. Missing keywords that should be added
        
        Format as JSON with keys: title_score, description_score, tags_score, main_keywords, missing_keywords
        """
        
        response = self._call_claude(prompt)
        if response:
            try:
                # Try to parse JSON response
                return json.loads(response)
            except:
                # If JSON parsing fails, return basic analysis
                return {
                    'title_score': 7,
                    'description_score': 6,
                    'tags_score': 5,
                    'main_keywords': self._extract_keywords(video_context['title']),
                    'missing_keywords': ['trending', 'popular', 'viral']
                }
        return None
    
    def _call_claude(self, prompt: str) -> Optional[str]:
        """Call Claude Sonnet 3.5 via AWS Bedrock"""
        if not self.bedrock_client:
            return None
        
        try:
            # Prepare the request body
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Call Bedrock - using the correct model ID
            response = self.bedrock_client.invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"Error calling Claude: {e}")
            return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'how', 'what', 'when', 'where', 'why'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return list(set(keywords))[:10]  # Return unique keywords, max 10
    
    def _get_mock_suggestions(self, video: Dict) -> Dict:
        """Generate mock suggestions when AI is not available"""
        title = video.get('title', '')
        description = video.get('description', '')
        tags = video.get('tags', [])
        
        return {
            'improved_title': self._generate_mock_title(title),
            'improved_description': self._generate_mock_description(title, description),
            'suggested_tags': self._generate_mock_tags(title, tags),
            'content_ideas': self._generate_mock_content_ideas(title),
            'seo_analysis': {
                'title_score': 7,
                'description_score': 6,
                'tags_score': 5,
                'main_keywords': self._extract_keywords(title),
                'missing_keywords': ['tutorial', 'guide', 'tips', 'secrets']
            }
        }
    
    def _generate_mock_title(self, current_title: str) -> str:
        """Generate a mock improved title"""
        # Add emotional triggers and numbers
        power_words = ['Ultimate', 'Secret', 'Proven', 'Amazing', 'Incredible', 'Essential']
        numbers = ['5', '7', '10', '15', '20']
        
        # Simple improvement logic
        if len(current_title) < 40:
            return f"{power_words[0]} {current_title} - {numbers[1]} Tips You Need!"
        else:
            return f"{numbers[2]} {power_words[1]} {current_title[:30]}... Revealed!"
    
    def _generate_mock_description(self, title: str, current_desc: str) -> str:
        """Generate a mock improved description"""
        hook = "🔥 Get ready to transform your understanding!"
        keywords = self._extract_keywords(title)
        keyword_text = f"Learn about {', '.join(keywords[:3])} and more!"
        
        cta = """
        
🔔 Don't forget to SUBSCRIBE for more amazing content!
👍 LIKE this video if it helped you!
💬 COMMENT below with your thoughts!
        
#trending #viral #tutorial
        """
        
        if len(current_desc) > 100:
            return f"{hook}\n\n{current_desc[:200]}...\n\n{keyword_text}{cta}"
        else:
            return f"{hook}\n\n{keyword_text}\n\nThis video covers everything you need to know!{cta}"
    
    def _generate_mock_tags(self, title: str, current_tags: List[str]) -> List[str]:
        """Generate mock improved tags"""
        base_keywords = self._extract_keywords(title)
        trending_tags = ['viral', 'trending', 'popular', 'new', 'latest', 'best', 'top', 'guide', 'tutorial', 'tips']
        
        suggested_tags = base_keywords + trending_tags + current_tags[:5]
        return list(set(suggested_tags))[:12]  # Remove duplicates, max 12 tags
    
    def _generate_mock_content_ideas(self, title: str) -> List[str]:
        """Generate mock content ideas"""
        keywords = self._extract_keywords(title)
        main_topic = keywords[0] if keywords else "content"
        
        return [
            f"Top 10 {main_topic} mistakes to avoid",
            f"Beginner's guide to {main_topic}",
            f"Advanced {main_topic} techniques revealed",
            f"{main_topic} vs alternatives comparison",
            f"Future of {main_topic} in 2025"
        ]

    def _get_mock_deep_analysis(self, video: Dict) -> Dict:
        """Generate mock deep analysis when AI is not available"""
        title = video.get('title', 'your video')
        return {
            'deep_analysis': f"""
### 🧠 Deep Analysis & Suggestions for "{title}"

**Thumbnail Analysis**
1.  **Use High-Contrast Colors**: Make your thumbnail pop with bright, contrasting colors.
2.  **Include a Human Face**: Thumbnails with expressive faces get more clicks.
3.  **Add Text Overlay**: Use a short, bold title on the thumbnail itself.

**Content Structure**
*   **Hook (0-15s)**: Start with a question or a surprising statement.
*   **Intro (15-30s)**: Briefly explain what the video is about.
*   **Main Content (30s-end)**: Deliver your main points clearly.
*   **CTA**: Ask for likes and subscribes around the midpoint.
*   **Outro**: Tease your next video.

**Audience Persona**
*   **Who they are**: Likely beginners interested in {self._extract_keywords(title)[0] if self._extract_keywords(title) else 'this topic'}.
*   **What they want**: Quick, easy-to-understand solutions.
*   **How to tailor**: Use simple language, avoid jargon.

**Engagement Hooks**
1.  Ask a question and tell viewers to answer in the comments.
2.  Run a poll using YouTube's poll card feature.
3.  Create a "video challenge" related to your content.

**Monetization Potential**
1.  **Affiliate Marketing**: Link to products you used in the video.
2.  **Create a Course**: Sell a more in-depth course on the topic.
3.  **Offer Consulting**: Provide one-on-one help for a fee.
"""
        }
