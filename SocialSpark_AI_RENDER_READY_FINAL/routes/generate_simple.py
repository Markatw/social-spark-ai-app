from flask import Blueprint, request, jsonify
import re
import random

generate_bp = Blueprint('generate', __name__)

# Sample content templates for different platforms
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

HASHTAG_SUGGESTIONS = {
    'general': ['#trending', '#viral', '#content', '#social', '#digital', '#online'],
    'business': ['#business', '#entrepreneur', '#startup', '#success', '#growth', '#innovation'],
    'lifestyle': ['#lifestyle', '#wellness', '#health', '#fitness', '#mindfulness', '#selfcare'],
    'technology': ['#tech', '#innovation', '#digital', '#ai', '#future', '#startup']
}

CTA_LIBRARY = {
    'engagement': [
        "What do you think? Share your thoughts below! 👇",
        "Double tap if you agree! ❤️",
        "Tag someone who needs to see this! 👥",
        "Save this post for later! 📌"
    ],
    'action': [
        "Click the link in bio to learn more! 🔗",
        "Swipe left for more tips! ➡️",
        "Follow for daily updates! ➕",
        "Turn on notifications! 🔔"
    ]
}

@generate_bp.route('/content', methods=['POST'])
def generate_content():
    try:
        data = request.get_json()
        topic = data.get('topic', 'social media')
        platform = data.get('platform', 'instagram').lower()
        tone = data.get('tone', 'casual')
        
        # Select template based on platform
        templates = PLATFORM_TEMPLATES.get(platform, PLATFORM_TEMPLATES['instagram'])
        selected_template = random.choice(templates)
        
        # Generate content
        content = selected_template.format(topic=topic)
        
        # Add tone-specific modifications
        if tone == 'professional':
            content = content.replace('!', '.').replace('🌟', '').replace('✨', '').replace('💫', '')
        elif tone == 'enthusiastic':
            content += " 🎉🚀"
        
        return jsonify({
            'content': content,
            'platform': platform,
            'character_count': len(content),
            'word_count': len(content.split())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generate_bp.route('/hashtags', methods=['POST'])
def generate_hashtags():
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        category = data.get('category', 'general')
        count = min(data.get('count', 5), 10)  # Max 10 hashtags
        
        # Get base hashtags for category
        base_hashtags = HASHTAG_SUGGESTIONS.get(category, HASHTAG_SUGGESTIONS['general'])
        
        # Generate topic-specific hashtags
        topic_words = topic.lower().split()
        topic_hashtags = [f"#{word}" for word in topic_words if len(word) > 2]
        
        # Combine and select
        all_hashtags = base_hashtags + topic_hashtags
        selected_hashtags = random.sample(all_hashtags, min(count, len(all_hashtags)))
        
        return jsonify({
            'hashtags': selected_hashtags,
            'count': len(selected_hashtags)
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
        
        # Simple readability score (based on average word length)
        avg_word_length = sum(len(word) for word in content.split()) / max(word_count, 1)
        readability_score = max(0, min(100, 100 - (avg_word_length - 4) * 10))
        
        # Keyword density (simple version)
        words = content.lower().split()
        word_freq = {}
        for word in words:
            word = re.sub(r'[^\w]', '', word)
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        keyword_density = {word: (count / word_count) * 100 
                          for word, count in word_freq.items() 
                          if count > 1}
        
        return jsonify({
            'word_count': word_count,
            'character_count': char_count,
            'hashtag_count': hashtag_count,
            'readability_score': round(readability_score, 1),
            'keyword_density': dict(list(keyword_density.items())[:5])  # Top 5
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generate_bp.route('/cta', methods=['POST'])
def generate_cta():
    try:
        data = request.get_json()
        cta_type = data.get('type', 'engagement')
        platform = data.get('platform', 'instagram')
        
        # Select CTA based on type
        ctas = CTA_LIBRARY.get(cta_type, CTA_LIBRARY['engagement'])
        selected_cta = random.choice(ctas)
        
        return jsonify({
            'cta': selected_cta,
            'type': cta_type,
            'platform': platform
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generate_bp.route('/optimize', methods=['POST'])
def optimize_content():
    try:
        data = request.get_json()
        content = data.get('content', '')
        platform = data.get('platform', 'instagram')
        
        # Platform-specific optimization suggestions
        suggestions = []
        
        char_count = len(content)
        word_count = len(content.split())
        hashtag_count = len(re.findall(r'#\w+', content))
        
        # Platform-specific recommendations
        if platform == 'instagram':
            if char_count > 2200:
                suggestions.append("Consider shortening your caption (current: {} chars, ideal: under 2200)".format(char_count))
            if hashtag_count < 5:
                suggestions.append("Add more hashtags (current: {}, recommended: 5-10)".format(hashtag_count))
        elif platform == 'twitter':
            if char_count > 280:
                suggestions.append("Content too long for Twitter (current: {} chars, max: 280)".format(char_count))
        elif platform == 'linkedin':
            if word_count < 50:
                suggestions.append("Consider expanding your post (current: {} words, ideal: 50+ words)".format(word_count))
        
        # General suggestions
        if not re.search(r'[!?]', content):
            suggestions.append("Add some excitement with exclamation marks or questions")
        
        if hashtag_count == 0:
            suggestions.append("Add relevant hashtags to increase discoverability")
        
        optimization_score = max(0, 100 - len(suggestions) * 20)
        
        return jsonify({
            'optimization_score': optimization_score,
            'suggestions': suggestions,
            'character_count': char_count,
            'word_count': word_count,
            'hashtag_count': hashtag_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

