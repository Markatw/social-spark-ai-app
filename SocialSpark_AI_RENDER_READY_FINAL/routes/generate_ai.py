import os
import re
import json
import time
import random
import requests
from flask import Blueprint, request, jsonify

generate_bp = Blueprint('generate', __name__)

# Gemini API configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'AIzaSyByygDJpW77FE9gEHDspckwsnQ0IMXBoYk'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'

# Fallback templates for when AI is unavailable
PLATFORM_TEMPLATES = {
    'instagram': [
        "🌟 {topic} is trending! Here's what you need to know... #trending #lifestyle",
        "✨ Discover the magic of {topic}! Share your thoughts below 👇 #discover #share",
        "💫 {topic} inspiration for your day! What's your favorite part? #inspiration #daily"
    ],
    'facebook': [
        "Let's talk about {topic}! What are your thoughts on this? I'd love to hear your perspective in the comments.",
        "Have you tried {topic} yet? Here's my experience and why I think you should give it a shot!",
        "The latest trends in {topic} are fascinating! Here's what caught my attention recently."
    ],
    'twitter': [
        "Quick thoughts on {topic}: This is game-changing! What do you think? #trending",
        "{topic} update: Here's what everyone should know 🧵 #thread #update",
        "Hot take on {topic}: This could change everything! Thoughts? #hottake"
    ],
    'linkedin': [
        "Professional insights on {topic}: Here's what industry leaders are saying about the latest developments.",
        "Career tip: Understanding {topic} can give you a competitive edge in today's market.",
        "Industry analysis: How {topic} is reshaping the professional landscape."
    ]
}

def call_gemini_api(prompt, max_tokens=1000):
    """Make HTTP request to Gemini API"""
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY not configured")
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        'contents': [{
            'parts': [{
                'text': prompt
            }]
        }],
        'generationConfig': {
            'temperature': 0.7,
            'topK': 40,
            'topP': 0.95,
            'maxOutputTokens': max_tokens,
        }
    }
    
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']
                return content.strip()
            else:
                raise Exception("No content generated")
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")

def generate_fallback_content(topic, platform, tone):
    """Generate content using templates when AI is unavailable"""
    templates = PLATFORM_TEMPLATES.get(platform, PLATFORM_TEMPLATES['instagram'])
    selected_template = random.choice(templates)
    content = selected_template.format(topic=topic)
    
    if tone == 'professional':
        content = content.replace('!', '.').replace('🌟', '').replace('✨', '').replace('💫', '')
    elif tone == 'enthusiastic':
        content += " 🎉🚀"
    
    return content

@generate_bp.route('/content', methods=['POST'])
def generate_content():
    try:
        data = request.get_json()
        topic = data.get('topic', 'social media')
        platform = data.get('platform', 'instagram').lower()
        tone = data.get('tone', 'casual')
        keywords = data.get('keywords', [])
        
        # Create AI prompt
        keyword_text = f" Include these keywords naturally: {', '.join(keywords)}" if keywords else ""
        
        prompt = f"""Create engaging {platform} content about {topic}. 
        Tone: {tone}
        Platform: {platform}
        Requirements:
        - Write in {tone} tone
        - Optimize for {platform} audience
        - Include relevant emojis if appropriate
        - Make it engaging and shareable{keyword_text}
        - Keep within platform character limits
        
        Generate only the content, no explanations."""
        
        try:
            # Try AI generation first
            ai_content = call_gemini_api(prompt)
            content = ai_content
            generation_method = "ai"
        except Exception as ai_error:
            # Fall back to templates
            print(f"AI generation failed: {ai_error}")
            content = generate_fallback_content(topic, platform, tone)
            generation_method = "template"
        
        return jsonify({
            'content': content,
            'platform': platform,
            'character_count': len(content),
            'word_count': len(content.split()),
            'generation_method': generation_method
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generate_bp.route('/hashtags', methods=['POST'])
def generate_hashtags():
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        category = data.get('category', 'general')
        count = min(data.get('count', 5), 10)
        
        prompt = f"""Generate {count} relevant hashtags for {topic} in the {category} category.
        Requirements:
        - Make them specific and relevant to {topic}
        - Include mix of popular and niche hashtags
        - Suitable for social media platforms
        - No spaces in hashtags
        - Return only hashtags, one per line, starting with #"""
        
        try:
            # Try AI generation
            ai_response = call_gemini_api(prompt, max_tokens=200)
            hashtags = [line.strip() for line in ai_response.split('\n') if line.strip().startswith('#')]
            hashtags = hashtags[:count]  # Limit to requested count
            generation_method = "ai"
        except Exception:
            # Fallback hashtag generation
            base_hashtags = ['#trending', '#viral', '#content', '#social', '#digital']
            topic_hashtags = [f"#{word.lower()}" for word in topic.split() if len(word) > 2]
            hashtags = (base_hashtags + topic_hashtags)[:count]
            generation_method = "template"
        
        return jsonify({
            'hashtags': hashtags,
            'count': len(hashtags),
            'generation_method': generation_method
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generate_bp.route('/analyze', methods=['POST'])
def analyze_content():
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        # Basic analysis
        word_count = len(content.split())
        char_count = len(content)
        hashtag_count = len(re.findall(r'#\w+', content))
        
        # Simple readability score
        avg_word_length = sum(len(word) for word in content.split()) / max(word_count, 1)
        readability_score = max(0, min(100, 100 - (avg_word_length - 4) * 10))
        
        # Keyword density
        words = content.lower().split()
        word_freq = {}
        for word in words:
            word = re.sub(r'[^\w]', '', word)
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        keyword_density = {word: (count / word_count) * 100 
                          for word, count in word_freq.items() 
                          if count > 1}
        
        # AI-powered analysis (if available)
        analysis_method = "basic"
        ai_insights = None
        
        try:
            if GEMINI_API_KEY and len(content) > 10:
                analysis_prompt = f"""Analyze this social media content for SEO and engagement:
                "{content}"
                
                Provide insights on:
                1. Engagement potential (1-10)
                2. SEO effectiveness (1-10)
                3. Key strengths
                4. Improvement suggestions
                
                Format as JSON with keys: engagement_score, seo_score, strengths, suggestions"""
                
                ai_response = call_gemini_api(analysis_prompt, max_tokens=300)
                # Try to parse JSON response
                try:
                    ai_insights = json.loads(ai_response)
                    analysis_method = "ai"
                except:
                    # If JSON parsing fails, use the response as text
                    ai_insights = {"analysis": ai_response}
                    analysis_method = "ai_text"
        except Exception:
            pass  # Continue with basic analysis
        
        result = {
            'word_count': word_count,
            'character_count': char_count,
            'hashtag_count': hashtag_count,
            'readability_score': round(readability_score, 1),
            'keyword_density': dict(list(keyword_density.items())[:5]),
            'analysis_method': analysis_method
        }
        
        if ai_insights:
            result['ai_insights'] = ai_insights
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generate_bp.route('/cta', methods=['POST'])
def generate_cta():
    try:
        data = request.get_json()
        cta_type = data.get('type', 'engagement')
        platform = data.get('platform', 'instagram')
        topic = data.get('topic', '')
        
        prompt = f"""Generate a compelling call-to-action for {platform} about {topic}.
        Type: {cta_type} (engagement/action/conversion)
        Requirements:
        - Platform-appropriate tone and style
        - Encourage user interaction
        - Be specific and actionable
        - Include relevant emojis if suitable
        
        Generate only the CTA text, no explanations."""
        
        try:
            # Try AI generation
            ai_cta = call_gemini_api(prompt, max_tokens=100)
            cta = ai_cta
            generation_method = "ai"
        except Exception:
            # Fallback CTAs
            fallback_ctas = {
                'engagement': [
                    "What do you think? Share your thoughts below! 👇",
                    "Double tap if you agree! ❤️",
                    "Tag someone who needs to see this! 👥"
                ],
                'action': [
                    "Click the link in bio to learn more! 🔗",
                    "Follow for daily updates! ➕",
                    "Save this post for later! 📌"
                ]
            }
            ctas = fallback_ctas.get(cta_type, fallback_ctas['engagement'])
            cta = random.choice(ctas)
            generation_method = "template"
        
        return jsonify({
            'cta': cta,
            'type': cta_type,
            'platform': platform,
            'generation_method': generation_method
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generate_bp.route('/optimize', methods=['POST'])
def optimize_content():
    try:
        data = request.get_json()
        content = data.get('content', '')
        platform = data.get('platform', 'instagram')
        
        char_count = len(content)
        word_count = len(content.split())
        hashtag_count = len(re.findall(r'#\w+', content))
        
        # Basic optimization suggestions
        suggestions = []
        
        # Platform-specific recommendations
        if platform == 'instagram':
            if char_count > 2200:
                suggestions.append(f"Consider shortening your caption (current: {char_count} chars, ideal: under 2200)")
            if hashtag_count < 5:
                suggestions.append(f"Add more hashtags (current: {hashtag_count}, recommended: 5-10)")
        elif platform == 'twitter':
            if char_count > 280:
                suggestions.append(f"Content too long for Twitter (current: {char_count} chars, max: 280)")
        elif platform == 'linkedin':
            if word_count < 50:
                suggestions.append(f"Consider expanding your post (current: {word_count} words, ideal: 50+ words)")
        
        # AI-powered optimization (if available)
        optimization_method = "basic"
        ai_suggestions = []
        
        try:
            if GEMINI_API_KEY and len(content) > 10:
                optimization_prompt = f"""Optimize this {platform} content for better engagement and SEO:
                "{content}"
                
                Provide 3-5 specific, actionable optimization suggestions.
                Focus on:
                - Platform best practices
                - Engagement optimization
                - SEO improvements
                - Content structure
                
                Return as a JSON array of suggestion strings."""
                
                ai_response = call_gemini_api(optimization_prompt, max_tokens=400)
                try:
                    ai_suggestions = json.loads(ai_response)
                    if isinstance(ai_suggestions, list):
                        suggestions.extend(ai_suggestions)
                        optimization_method = "ai"
                except:
                    # If JSON parsing fails, add as single suggestion
                    suggestions.append(f"AI Suggestion: {ai_response}")
                    optimization_method = "ai_text"
        except Exception:
            pass  # Continue with basic suggestions
        
        # General suggestions
        if not re.search(r'[!?]', content):
            suggestions.append("Add some excitement with exclamation marks or questions")
        
        if hashtag_count == 0:
            suggestions.append("Add relevant hashtags to increase discoverability")
        
        optimization_score = max(0, 100 - len(suggestions) * 15)
        
        return jsonify({
            'optimization_score': optimization_score,
            'suggestions': suggestions[:8],  # Limit to 8 suggestions
            'character_count': char_count,
            'word_count': word_count,
            'hashtag_count': hashtag_count,
            'optimization_method': optimization_method
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generate_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify AI integration status"""
    try:
        ai_status = "available" if GEMINI_API_KEY else "unavailable"
        
        # Test AI connection if key is available
        if GEMINI_API_KEY:
            try:
                test_response = call_gemini_api("Test", max_tokens=10)
                ai_status = "connected"
            except Exception:
                ai_status = "error"
        
        return jsonify({
            'status': 'healthy',
            'ai_integration': ai_status,
            'fallback_available': True,
            'timestamp': str(int(time.time()) if 'time' in globals() else 0)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

