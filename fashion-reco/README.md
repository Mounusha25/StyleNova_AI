# 🎯 Adaptive Fashion Recommendation System

An intelligent fashion recommendation system that learns from user feedback using **CLIP + Reinforcement Learning from Human Feedback (RLHF)**. The system adapts to user preferences over time with temporal decay for negative feedback.

## ✨ Features

- **🧠 Adaptive Learning**: Like/dislike feedback that improves recommendations
- **⏰ Temporal Decay**: Negative feedback weakens over time (not permanent)
- **👤 User Profiles**: Individual preference learning for each user
- **🔍 Multiple Input Methods**: Quiz features, image URLs, or brand names
- **🎯 Real-time Adaptation**: Immediate feedback integration
- **💾 Persistent Storage**: User preferences saved across sessions

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (included)

### 1. Setup & Installation

```bash
# Navigate to the project directory
cd /path/to/fashion-reco

# Activate virtual environment
source fashion_venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# Start the adaptive API server
python adaptive_api.py
```

The server will start on `http://localhost:8004`

**You should see:**
```
🚀 Starting Adaptive Fashion Recommender API Server...
📝 API Documentation: http://localhost:8004/docs
✅ Adaptive system initialized successfully!
INFO:     Uvicorn running on http://0.0.0.0:8004
```

### 3. Test the System

```bash
# In a NEW terminal (keep server running)
cd /path/to/fashion-reco
source fashion_venv/bin/activate

# Run simple test
python simple_adaptive_test.py

# Test all input methods
python test_all_methods.py
```

## 📚 API Usage

### Endpoint: `POST /recommend/adaptive`

**Method 1: Quiz Features**
```json
{
  "user_id": "user123",
  "quiz_features": {
    "size": "M",
    "preferred_categories": ["shoes"],
    "preferred_colors": ["white"],
    "max_price": 100,
    "preferred_brands": ["nike"],
    "preferred_styles": ["casual"]
  },
  "adaptation_strength": 0.5,
  "k": 5
}
```

**Method 2: Image URL**
```json
{
  "user_id": "user123",
  "image_url": "https://example.com/shoe-image.jpg",
  "adaptation_strength": 0.5,
  "k": 5
}
```

**Method 3: Brand Search**
```json
{
  "user_id": "user123",
  "brand_name": "Nike",
  "category": "shoes",
  "adaptation_strength": 0.5,
  "k": 5
}
```

### Endpoint: `POST /feedback`

**Give Feedback (Like/Dislike)**
```json
{
  "user_id": "user123",
  "item_id": "item_003",
  "feedback": "like"
}
```

### Endpoint: `GET /users/{user_id}/stats`

**Check User Learning Progress**
```bash
curl http://localhost:8004/users/user123/stats
```

## 🧪 Testing Commands

```bash
# Test basic adaptive functionality
python simple_adaptive_test.py

# Test all input methods (quiz, image, brand)
python test_all_methods.py

# Manual testing with real catalog items
python manual_test.py
```

## 📊 System Architecture

### Core Files
- `adaptive_api.py` - Main FastAPI server with all endpoints
- `adaptive_recommender.py` - Core RLHF adaptive learning logic
- `clip_recommender.py` - CLIP-based semantic recommendations
- `catalog.csv` - Product catalog (5 sample items)
- `user_profiles.json` - Persistent user learning data

### Key Features
- **CLIP Model**: OpenAI's ViT-B/32 for joint text-image understanding
- **Adaptive Learning**: +0.3 boost for liked items, -0.4 penalty for disliked
- **Temporal Decay**: `penalty = -0.4 * exp(-0.1 * days)` 
- **Individual Users**: Separate learning profiles per user
- **Persistent Storage**: Automatic save/load of user preferences

## 🎯 Valid Item IDs for Testing

Your catalog contains these items:
- `item_001` - Zara White Cotton T-Shirt ($29.99)
- `item_002` - H&M Blue Denim Jeans ($49.99)
- `item_003` - Nike Black Running Shoes ($89.99)
- `item_004` - Uniqlo Gray Hoodie ($39.99)
- `item_005` - Adidas Red Track Jacket ($79.99)

## 🔧 API Documentation

Visit `http://localhost:8004/docs` for interactive API documentation with:
- Request/response examples
- Parameter descriptions
- Try-it-out functionality

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
lsof -i :8004

# Kill existing process
kill -9 <PID>

# Restart server
python adaptive_api.py
```

### Virtual Environment Issues
```bash
# Recreate virtual environment if needed
python -m venv fashion_venv
source fashion_venv/bin/activate
pip install -r requirements.txt
```

### Dependencies Missing
```bash
# Reinstall all dependencies
source fashion_venv/bin/activate
pip install -r requirements.txt
```

### Test Fails with "Server not running"
Make sure the server is running in a separate terminal:
```bash
# Terminal 1: Server
python adaptive_api.py

# Terminal 2: Tests
python simple_adaptive_test.py
```

## 📈 How Adaptation Works

1. **Initial State**: User gets base recommendations
2. **Feedback**: User likes/dislikes items
3. **Learning**: System updates user preference profile
4. **Adaptation**: Future recommendations are personalized
5. **Temporal Decay**: Old negative feedback weakens over time

### Example Flow
```
1. User searches "Nike shoes" → Gets 5 results
2. User likes Nike Air Max → System learns user likes athletic wear
3. User dislikes formal shoes → System temporarily avoids formal items
4. Next search → Athletic shoes ranked higher, formal shoes lower
5. After 30 days → Negative feedback impact reduced by ~75%
```

## 🎉 Success Indicators

✅ **Scores change** after giving feedback  
✅ **Rankings reorder** based on user preferences  
✅ **Similar items** get boosted/penalized together  
✅ **User stats** show learning progress  
✅ **Recommendations** show `"is_personalized": true`  
✅ **Temporal decay** works (old feedback matters less)

## 📞 Support

If you encounter issues:
1. Check server logs for error messages
2. Verify virtual environment is activated
3. Ensure all dependencies are installed
4. Test with provided sample requests
5. Check API documentation at `/docs`

---

**� Your adaptive fashion recommendation system is ready to learn and adapt to user preferences!**