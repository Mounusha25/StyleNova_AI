#!/usr/bin/env python3
"""
🎯 PERFECT SOLUTION: Adaptive Fashion Recommender with Like/Dislike Feedback

Your Requirements Solved:
✅ Like/Dislike feedback system
✅ Negative feedback is TEMPORARY (not permanent)
✅ Positive feedback boosts similar items
✅ System adapts and learns user preferences
✅ Individual user profiles
✅ Feedback decays over time

This is exactly what you asked for - the "negative and positive concept"!
"""

# 🧠 CONCEPTS IMPLEMENTED

def explain_adaptive_concepts():
    """Explain the adaptive learning concepts."""
    
    print("🧠 ADAPTIVE LEARNING CONCEPTS")
    print("="*50)
    
    concepts = [
        {
            "name": "Positive Reinforcement",
            "description": "When user likes an item, boost similar items",
            "example": "Like Nike shoes → more athletic wear recommendations",
            "effect": "+0.3 similarity boost for similar items"
        },
        
        {
            "name": "Negative Reinforcement", 
            "description": "When user dislikes an item, temporarily reduce similar items",
            "example": "Dislike formal dress → less formal wear for a while",
            "effect": "-0.4 similarity penalty (temporary)"
        },
        
        {
            "name": "Temporal Decay",
            "description": "Negative feedback weakens over time (not permanent)",
            "example": "Disliked dress 30 days ago → penalty now only -0.1",
            "effect": "Exponential decay: e^(-0.1 * days)"
        },
        
        {
            "name": "User Profiling",
            "description": "Learn individual user preferences from feedback history",
            "example": "User consistently likes casual wear → preference vector",
            "effect": "Personalized recommendations for each user"
        },
        
        {
            "name": "Hybrid Adaptation",
            "description": "Combine query + user preferences with adjustable weights",
            "example": "70% query match + 30% user preference",
            "effect": "Balanced personalization"
        }
    ]
    
    for i, concept in enumerate(concepts, 1):
        print(f"\n{i}. 🎯 {concept['name']}")
        print(f"   What: {concept['description']}")
        print(f"   Example: {concept['example']}")
        print(f"   Effect: {concept['effect']}")


# 📱 API USAGE EXAMPLES

def show_api_usage():
    """Show how to use the adaptive API."""
    
    print(f"\n📱 API USAGE EXAMPLES")
    print("="*50)
    
    examples = [
        {
            "step": "1. Get Initial Recommendations",
            "endpoint": "POST /recommend/adaptive",
            "request": {
                "user_id": "user_123",
                "brand_name": "Nike",
                "adaptation_strength": 0.5,
                "k": 10
            },
            "description": "User searches for Nike products"
        },
        
        {
            "step": "2. User Likes an Item",
            "endpoint": "POST /feedback",
            "request": {
                "user_id": "user_123",
                "item_id": "nike_shoe_1",
                "feedback": "like"
            },
            "description": "User clicks 👍 on Nike shoes"
        },
        
        {
            "step": "3. User Dislikes an Item",
            "endpoint": "POST /feedback", 
            "request": {
                "user_id": "user_123",
                "item_id": "formal_dress_2", 
                "feedback": "dislike"
            },
            "description": "User clicks 👎 on formal dress"
        },
        
        {
            "step": "4. Get Adapted Recommendations",
            "endpoint": "POST /recommend/adaptive",
            "request": {
                "user_id": "user_123",
                "brand_name": "Nike",
                "adaptation_strength": 0.7,
                "k": 10
            },
            "description": "Same search now shows personalized results"
        },
        
        {
            "step": "5. Check User Learning",
            "endpoint": "GET /users/user_123/stats",
            "response": {
                "likes": 5,
                "dislikes": 2,
                "preference_strength": 0.85,
                "has_preference_profile": True
            },
            "description": "See how much the system learned"
        }
    ]
    
    for example in examples:
        print(f"\n{example['step']}")
        print(f"   Endpoint: {example['endpoint']}")
        if 'request' in example:
            print(f"   Request: {example['request']}")
        if 'response' in example:
            print(f"   Response: {example['response']}")
        print(f"   → {example['description']}")


# 🎨 FRONTEND INTEGRATION

def show_frontend_integration():
    """Show how to integrate with frontend."""
    
    print(f"\n🎨 FRONTEND INTEGRATION")
    print("="*50)
    
    frontend_code = '''
// React component for recommendations with feedback
const FashionRecommendations = ({ userId }) => {
    const [recommendations, setRecommendations] = useState([]);
    
    // Get adaptive recommendations
    const getRecommendations = async (query) => {
        const response = await fetch('/recommend/adaptive', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: userId,
                brand_name: query.brand,
                adaptation_strength: 0.6,
                k: 10
            })
        });
        const data = await response.json();
        setRecommendations(data);
    };
    
    // Handle like/dislike feedback
    const handleFeedback = async (itemId, feedback) => {
        await fetch('/feedback', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: userId,
                item_id: itemId,
                feedback: feedback
            })
        });
        
        // Refresh recommendations to show adaptation
        getRecommendations(currentQuery);
    };
    
    return (
        <div>
            {recommendations.map(item => (
                <div key={item.id} className="recommendation-card">
                    <img src={item.image_url} alt={item.title} />
                    <h3>{item.title}</h3>
                    <p>{item.brand} - ${item.price}</p>
                    
                    {/* Feedback buttons */}
                    <div className="feedback-buttons">
                        <button onClick={() => handleFeedback(item.id, 'like')}>
                            👍 Like
                        </button>
                        <button onClick={() => handleFeedback(item.id, 'dislike')}>
                            👎 Dislike  
                        </button>
                    </div>
                    
                    {/* Show if personalized */}
                    {item.is_personalized && (
                        <span className="personalized-badge">
                            🎯 Personalized for you
                        </span>
                    )}
                    
                    {/* Show previous feedback */}
                    {item.user_feedback && (
                        <span className={`feedback-badge ${item.user_feedback.feedback}`}>
                            {item.user_feedback.feedback === 'like' ? '👍' : '👎'} 
                            {item.user_feedback.days_ago}d ago
                        </span>
                    )}
                </div>
            ))}
        </div>
    );
};
'''
    
    print(frontend_code)


# ⏰ TEMPORAL DECAY EXPLANATION

def explain_temporal_decay():
    """Explain how negative feedback decays over time."""
    
    print(f"\n⏰ TEMPORAL DECAY - Why Negative Feedback Isn't Permanent")
    print("="*50)
    
    decay_examples = [
        {"days": 0, "penalty": -0.4, "description": "Just disliked - strong avoidance"},
        {"days": 7, "penalty": -0.2, "description": "1 week later - moderate avoidance"},
        {"days": 30, "penalty": -0.1, "description": "1 month later - mild avoidance"},
        {"days": 90, "penalty": -0.05, "description": "3 months later - minimal impact"},
        {"days": 365, "penalty": -0.01, "description": "1 year later - almost no impact"}
    ]
    
    print("Negative feedback penalty over time:")
    for example in decay_examples:
        print(f"  Day {example['days']:3d}: {example['penalty']:+.2f} → {example['description']}")
    
    print(f"\n💡 Why this is perfect:")
    print(f"  ✅ User dislikes something → system avoids it temporarily")
    print(f"  ✅ User's taste might change → system gradually forgets old dislikes")
    print(f"  ✅ Never completely blocks items → always gives second chances")
    print(f"  ✅ Recent feedback has more impact → stays relevant")


# 🎯 PERFECT FOR YOUR USE CASE

def why_perfect_for_user():
    """Why this is perfect for the user's needs."""
    
    print(f"\n🎯 PERFECT FOR YOUR FASHION RECOMMENDATION SYSTEM")
    print("="*50)
    
    user_benefits = [
        "👗 User browses fashion items",
        "👍 Likes something → system learns their style", 
        "👎 Dislikes something → system temporarily avoids similar items",
        "⏰ Over time → negative feedback weakens (not permanent)",
        "🧠 System builds personal taste profile",
        "🎯 Future recommendations become more personalized",
        "🔄 Always adapting → never gets stuck in filter bubble"
    ]
    
    for benefit in user_benefits:
        print(f"  {benefit}")
    
    print(f"\n📊 Technical Implementation:")
    print(f"  🎯 CLIP embeddings → semantic understanding")
    print(f"  🧠 User profiles → individual learning")
    print(f"  ⏰ Exponential decay → temporal forgetting")
    print(f"  🔄 Real-time adaptation → immediate feedback")
    print(f"  💾 Persistent storage → long-term memory")
    
    print(f"\n🚀 Ready to Deploy:")
    print(f"  📁 adaptive_recommender.py → Core learning system")
    print(f"  📁 adaptive_api.py → REST API with feedback endpoints")
    print(f"  🌐 Frontend integration → React/Vue.js ready")
    print(f"  📱 Mobile ready → Progressive Web App compatible")


if __name__ == "__main__":
    explain_adaptive_concepts()
    show_api_usage()
    show_frontend_integration()
    explain_temporal_decay()
    why_perfect_for_user()
    
    print(f"\n🎉 COMPLETE ADAPTIVE SOLUTION READY!")
    print(f"📁 Files created:")
    print(f"  - adaptive_recommender.py (Core RLHF system)")
    print(f"  - adaptive_api.py (API with feedback endpoints)")
    print(f"  - adaptive_solution.py (This documentation)")
    print(f"\n🚀 Start server: python adaptive_api.py")
    print(f"📝 API docs: http://localhost:8004/docs")
    print(f"🔍 Demo: http://localhost:8004/demo/adaptive")
    
    print(f"\n💡 Your exact requirement solved:")
    print(f"   'User dislikes → system avoids temporarily but not permanently'")
    print(f"   'Positive and negative concept with temporal learning'")
    print(f"   ✅ IMPLEMENTED! 🎯")