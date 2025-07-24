from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import os
import google.generativeai as genai
from src.models.user import User

generate_bp = Blueprint("generate_bp", __name__)

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyByygDJpW77FE9gEHDspckwsnQ0IMXBoYk"))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, os.environ.get("SECRET_KEY", "supersecretkey"), algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
        except:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def create_content_prompt(topic, keywords, content_type, platform, tone, style):
    """Create a detailed prompt for content generation"""
    
    platform_specs = {
        "instagram": "Instagram post (engaging, visual-focused, use relevant hashtags)",
        "twitter": "Twitter/X post (concise, under 280 characters, engaging)",
        "facebook": "Facebook post (conversational, community-focused)",
        "linkedin": "LinkedIn post (professional, industry-focused, thought leadership)",
        "tiktok": "TikTok caption (trendy, fun, engaging for Gen Z)",
        "youtube": "YouTube description (detailed, SEO-optimized, includes call-to-action)"
    }
    
    content_type_specs = {
        "post": "social media post",
        "caption": "engaging caption",
        "story": "story content",
        "ad": "advertisement copy",
        "blog": "blog post excerpt",
        "announcement": "announcement post"
    }
    
    tone_guidance = {
        "professional": "formal, authoritative, and business-appropriate",
        "casual": "relaxed, friendly, and conversational",
        "humorous": "funny, witty, and entertaining",
        "inspirational": "motivating, uplifting, and encouraging",
        "educational": "informative, clear, and instructional",
        "promotional": "persuasive, sales-focused, and compelling"
    }
    
    platform_spec = platform_specs.get(platform.lower(), f"{platform} post")
    content_spec = content_type_specs.get(content_type.lower(), content_type)
    tone_spec = tone_guidance.get(tone.lower(), tone)
    
    prompt = f"""Create a {platform_spec} about "{topic}".

Content Requirements:
- Type: {content_spec}
- Platform: {platform}
- Tone: {tone_spec}
- Style: {style}
- Keywords to include: {keywords}

Platform-specific guidelines:
- Follow {platform} best practices and character limits
- Use appropriate formatting and structure
- Include relevant hashtags if applicable
- Make it engaging and shareable

Generate high-quality, original content that is:
1. Engaging and attention-grabbing
2. Relevant to the target audience
3. Optimized for the platform
4. Incorporates the specified keywords naturally
5. Matches the requested tone and style

Content:"""
    
    return prompt

@generate_bp.route("/content", methods=["POST"])
@token_required
def generate_content(current_user):
    try:
        data = request.get_json()
        topic = data.get("topic")
        keywords = data.get("keywords")
        content_type = data.get("content_type")
        platform = data.get("platform")
        tone = data.get("tone", "casual")
        style = data.get("style", "engaging")
        num_variations = data.get("num_variations", 1)

        if not topic or not keywords or not content_type or not platform:
            return jsonify({"message": "Missing required content generation parameters"}), 400

        # Validate input lengths to prevent server errors
        if len(topic) > 500:
            return jsonify({"message": "Topic must be 500 characters or less"}), 400
        if len(keywords) > 200:
            return jsonify({"message": "Keywords must be 200 characters or less"}), 400
        if len(style) > 100:
            return jsonify({"message": "Style must be 100 characters or less"}), 400

        # Validate num_variations
        if not isinstance(num_variations, int) or num_variations < 1 or num_variations > 5:
            return jsonify({"message": "Number of variations must be between 1 and 5"}), 400

        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        generated_contents = []
        
        for i in range(min(num_variations, 5)):  # Limit to 5 variations max
            try:
                prompt = create_content_prompt(topic, keywords, content_type, platform, tone, style)
                
                # Add variation instruction for multiple generations
                if num_variations > 1:
                    prompt += f"\n\nGenerate variation #{i+1} with a unique approach while maintaining the same requirements."
                
                response = model.generate_content(prompt)
                generated_text = response.text.strip()
                generated_contents.append(generated_text)
                
            except Exception as e:
                print(f"Error generating variation {i+1}: {str(e)}")
                # Fallback to a basic generated message if AI fails
                fallback_text = f"AI-generated {content_type} about '{topic}' for {platform}. Keywords: {keywords}. Tone: {tone}. Style: {style}. (Variation {i+1})"
                generated_contents.append(fallback_text)

        if not generated_contents:
            return jsonify({"message": "Failed to generate content"}), 500

        return jsonify({"generated_texts": generated_contents}), 200
        
    except Exception as e:
        print(f"Content generation error: {str(e)}")
        return jsonify({"message": "Content generation failed", "error": str(e)}), 500

@generate_bp.route("/analyze-seo", methods=["POST"])
@token_required
def analyze_seo(current_user):
    """Analyze content for SEO metrics"""
    try:
        data = request.get_json()
        content = data.get("content", "")
        target_keywords = data.get("keywords", [])
        
        if not content:
            return jsonify({"message": "Content is required for SEO analysis"}), 400
        
        # Basic SEO analysis
        word_count = len(content.split())
        char_count = len(content)
        char_count_no_spaces = len(content.replace(" ", ""))
        
        # Keyword density analysis
        content_lower = content.lower()
        keyword_analysis = {}
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            count = content_lower.count(keyword_lower)
            density = (count / word_count * 100) if word_count > 0 else 0
            keyword_analysis[keyword] = {
                "count": count,
                "density": round(density, 2)
            }
        
        # Readability score (simplified)
        sentences = content.count('.') + content.count('!') + content.count('?')
        avg_words_per_sentence = word_count / sentences if sentences > 0 else word_count
        
        # Simple readability score (lower is better)
        readability_score = min(100, max(0, 100 - (avg_words_per_sentence * 2)))
        
        # Generate hashtag suggestions
        hashtag_suggestions = generate_hashtag_suggestions(content, target_keywords)
        
        return jsonify({
            "word_count": word_count,
            "character_count": char_count,
            "character_count_no_spaces": char_count_no_spaces,
            "keyword_analysis": keyword_analysis,
            "readability_score": round(readability_score, 1),
            "hashtag_suggestions": hashtag_suggestions
        }), 200
        
    except Exception as e:
        print(f"SEO analysis error: {str(e)}")
        return jsonify({"message": "SEO analysis failed", "error": str(e)}), 500

@generate_bp.route("/cta-suggestions", methods=["POST"])
@token_required
def get_cta_suggestions(current_user):
    """Get call-to-action suggestions based on content type and platform"""
    try:
        data = request.get_json()
        content_type = data.get("content_type", "post")
        platform = data.get("platform", "instagram")
        topic = data.get("topic", "")
        
        # CTA library organized by platform and content type
        cta_library = {
            "instagram": {
                "post": [
                    "Double tap if you agree! ❤️",
                    "Save this post for later! 📌",
                    "Share your thoughts in the comments below! 👇",
                    "Tag a friend who needs to see this! 👥",
                    "What's your experience with this? Tell us! 💬",
                    "Follow for more tips like this! ✨",
                    "DM us your questions! 📩",
                    "Which tip will you try first? 🤔"
                ],
                "story": [
                    "Swipe up for more! ⬆️",
                    "DM me your thoughts! 💭",
                    "React with your favorite emoji! 😍",
                    "Share this to your story! 📱",
                    "Vote in our poll! 🗳️"
                ],
                "ad": [
                    "Shop now - limited time offer! 🛒",
                    "Learn more in our bio link! 🔗",
                    "Get started today! 🚀",
                    "Claim your discount now! 💰",
                    "Book your free consultation! 📅"
                ]
            },
            "facebook": {
                "post": [
                    "What do you think? Share your opinion!",
                    "Like and share if this resonates with you!",
                    "Comment below with your experience!",
                    "Tag someone who would find this helpful!",
                    "Follow our page for more content like this!",
                    "Join the conversation in the comments!",
                    "Share this post to spread the word!"
                ]
            },
            "twitter": {
                "post": [
                    "Retweet if you agree!",
                    "What's your take? Reply below!",
                    "Thread 🧵 (1/n)",
                    "Thoughts? 💭",
                    "RT to share with your followers!",
                    "Join the conversation! 🗣️"
                ]
            },
            "linkedin": {
                "post": [
                    "What's your experience with this? Share in the comments.",
                    "Agree? Disagree? Let's discuss in the comments.",
                    "Connect with me for more insights like this.",
                    "Share this post if you found it valuable.",
                    "What would you add to this list?",
                    "Follow for more industry insights.",
                    "Tag a colleague who should see this!"
                ]
            },
            "tiktok": {
                "post": [
                    "Follow for more tips! ✨",
                    "Comment your thoughts! 💭",
                    "Duet this if you agree! 🤝",
                    "Save this for later! 📌",
                    "Share with your friends! 👥",
                    "What do you think? 🤔",
                    "Try this and let me know how it goes! 💪"
                ]
            },
            "youtube": {
                "post": [
                    "Subscribe for more content like this!",
                    "Hit the bell icon for notifications! 🔔",
                    "Like this video if it helped you!",
                    "Comment your questions below!",
                    "Share this video with someone who needs it!",
                    "Check out our other videos in the description!",
                    "What topic should we cover next?"
                ]
            }
        }
        
        # Get platform-specific CTAs
        platform_ctas = cta_library.get(platform.lower(), {})
        content_ctas = platform_ctas.get(content_type.lower(), [])
        
        # If no specific CTAs found, use general ones
        if not content_ctas:
            content_ctas = [
                "Share your thoughts!",
                "Let us know what you think!",
                "Follow for more content!",
                "Engage with us in the comments!",
                "What's your opinion on this?"
            ]
        
        # Generate AI-powered custom CTA if topic is provided
        custom_cta = None
        if topic:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""Create a compelling call-to-action for a {platform} {content_type} about "{topic}".

The CTA should be:
1. Platform-appropriate for {platform}
2. Engaging and action-oriented
3. Relevant to the topic "{topic}"
4. Concise and clear
5. Include relevant emojis if appropriate for the platform

Generate only the CTA text, nothing else."""
                
                response = model.generate_content(prompt)
                custom_cta = response.text.strip()
            except Exception as e:
                print(f"Custom CTA generation error: {str(e)}")
        
        result = {
            "platform": platform,
            "content_type": content_type,
            "suggested_ctas": content_ctas,
        }
        
        if custom_cta:
            result["custom_cta"] = custom_cta
            
        return jsonify(result), 200
        
    except Exception as e:
        print(f"CTA suggestions error: {str(e)}")
        return jsonify({"message": "CTA suggestions failed", "error": str(e)}), 500

@generate_bp.route("/optimize-content", methods=["POST"])
@token_required
def optimize_content(current_user):
    """Provide content optimization recommendations"""
    try:
        data = request.get_json()
        content = data.get("content", "")
        platform = data.get("platform", "instagram")
        target_keywords = data.get("keywords", [])
        
        if not content:
            return jsonify({"message": "Content is required for optimization"}), 400
        
        # Platform-specific optimization guidelines
        platform_guidelines = {
            "instagram": {
                "ideal_length": {"min": 125, "max": 2200},
                "hashtag_limit": 30,
                "character_limit": 2200,
                "best_practices": [
                    "Use 3-5 hashtags in the first comment",
                    "Include a clear call-to-action",
                    "Use line breaks for readability",
                    "Add emojis to increase engagement"
                ]
            },
            "twitter": {
                "ideal_length": {"min": 71, "max": 280},
                "hashtag_limit": 2,
                "character_limit": 280,
                "best_practices": [
                    "Keep it concise and punchy",
                    "Use 1-2 relevant hashtags",
                    "Include media when possible",
                    "Ask questions to encourage replies"
                ]
            },
            "facebook": {
                "ideal_length": {"min": 40, "max": 80},
                "hashtag_limit": 3,
                "character_limit": 63206,
                "best_practices": [
                    "Shorter posts get more engagement",
                    "Use storytelling approach",
                    "Include a clear call-to-action",
                    "Post when your audience is most active"
                ]
            },
            "linkedin": {
                "ideal_length": {"min": 150, "max": 1300},
                "hashtag_limit": 5,
                "character_limit": 3000,
                "best_practices": [
                    "Start with a hook in the first line",
                    "Use professional tone",
                    "Include industry-relevant hashtags",
                    "End with a question or call-to-action"
                ]
            }
        }
        
        guidelines = platform_guidelines.get(platform.lower(), platform_guidelines["instagram"])
        
        # Analyze current content
        word_count = len(content.split())
        char_count = len(content)
        
        recommendations = []
        
        # Length optimization
        if char_count < guidelines["ideal_length"]["min"]:
            recommendations.append({
                "type": "length",
                "priority": "medium",
                "message": f"Consider expanding your content. Current: {char_count} chars, Recommended: {guidelines['ideal_length']['min']}-{guidelines['ideal_length']['max']} chars"
            })
        elif char_count > guidelines["ideal_length"]["max"]:
            recommendations.append({
                "type": "length",
                "priority": "high",
                "message": f"Content might be too long for {platform}. Current: {char_count} chars, Recommended: {guidelines['ideal_length']['min']}-{guidelines['ideal_length']['max']} chars"
            })
        
        # Keyword optimization
        content_lower = content.lower()
        missing_keywords = []
        for keyword in target_keywords:
            if keyword.lower() not in content_lower:
                missing_keywords.append(keyword)
        
        if missing_keywords:
            recommendations.append({
                "type": "keywords",
                "priority": "medium",
                "message": f"Consider including these keywords: {', '.join(missing_keywords)}"
            })
        
        # CTA check
        cta_indicators = ["comment", "share", "like", "follow", "click", "visit", "check", "try", "join", "subscribe"]
        has_cta = any(indicator in content_lower for indicator in cta_indicators)
        
        if not has_cta:
            recommendations.append({
                "type": "engagement",
                "priority": "high",
                "message": "Add a clear call-to-action to encourage engagement"
            })
        
        # Hashtag check (basic)
        hashtag_count = content.count('#')
        if hashtag_count == 0:
            recommendations.append({
                "type": "hashtags",
                "priority": "medium",
                "message": f"Consider adding relevant hashtags (recommended: 1-{guidelines['hashtag_limit']} for {platform})"
            })
        elif hashtag_count > guidelines["hashtag_limit"]:
            recommendations.append({
                "type": "hashtags",
                "priority": "low",
                "message": f"You might have too many hashtags ({hashtag_count}). Recommended: 1-{guidelines['hashtag_limit']} for {platform}"
            })
        
        return jsonify({
            "platform": platform,
            "current_stats": {
                "character_count": char_count,
                "word_count": word_count,
                "hashtag_count": hashtag_count
            },
            "platform_guidelines": guidelines,
            "recommendations": recommendations,
            "optimization_score": max(0, 100 - len([r for r in recommendations if r["priority"] in ["high", "medium"]]) * 15)
        }), 200
        
    except Exception as e:
        print(f"Content optimization error: {str(e)}")
        return jsonify({"message": "Content optimization failed", "error": str(e)}), 500

def generate_hashtag_suggestions(content, keywords):
    """Generate hashtag suggestions based on content and keywords"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Based on this content and keywords, suggest 10-15 relevant hashtags:

Content: {content[:500]}...
Keywords: {', '.join(keywords)}

Generate hashtags that are:
1. Relevant to the content
2. Popular but not overly saturated
3. Mix of broad and niche tags
4. Appropriate for social media

Return only the hashtags, one per line, starting with #"""
        
        response = model.generate_content(prompt)
        hashtags = [line.strip() for line in response.text.strip().split('\n') if line.strip().startswith('#')]
        
        return hashtags[:15]  # Limit to 15 hashtags
        
    except Exception as e:
        print(f"Hashtag generation error: {str(e)}")
        # Fallback hashtag suggestions
        return [f"#{keyword.replace(' ', '').lower()}" for keyword in keywords]

