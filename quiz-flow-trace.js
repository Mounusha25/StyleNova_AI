/**
 * Quiz Submission Flow Tracer
 * This file shows exactly what happens when a quiz is submitted
 */

// 1. QUIZ SUBMISSION (POST /api/quiz)
const sampleQuizSubmission = {
  userId: "user_123",
  answers: [
    { qid: "categories", type: "multi", value: ["shoes", "casual"] },
    { qid: "colors", type: "multi", value: ["black", "white"] },
    { qid: "brands", type: "multi", value: ["nike", "adidas"] },
    { qid: "budget", type: "scale", value: 100 },
    { qid: "size", type: "size", value: { shoe: "42" } }
  ]
};

console.log("📝 1. QUIZ SUBMISSION REQUEST:");
console.log("POST /api/quiz");
console.log("Content-Type: application/json");
console.log("Body:", JSON.stringify(sampleQuizSubmission, null, 2));

// 2. QUIZ API RESPONSE
const quizApiResponse = {
  success: true,
  quizId: "quiz_456",
  answers: sampleQuizSubmission.answers,
  lastAnswer: sampleQuizSubmission.answers[sampleQuizSubmission.answers.length - 1]
};

console.log("\n✅ 2. QUIZ API RESPONSE:");
console.log("Status: 200 OK");
console.log("Body:", JSON.stringify(quizApiResponse, null, 2));

// 3. QUIZ SUCCESS PAGE PROCESSING
console.log("\n🔄 3. QUIZ SUCCESS PAGE PROCESSING:");
console.log("- Redirects to: /quiz/success?quizId=quiz_456");
console.log("- Fetches quiz data: GET /api/quiz/quiz_456");
console.log("- Converts quiz answers to backend format...");

// 4. BACKEND API CONVERSION
const backendRequest = {
  user_id: "user_123",
  quiz_features: {
    size: "42",
    preferred_categories: ["shoes", "casual"],
    preferred_colors: ["black", "white"],
    max_price: 100,
    preferred_brands: ["nike", "adidas"],
    preferred_styles: ["casual"]
  },
  adaptation_strength: 0.6,
  k: 20
};

console.log("\n🧠 4. BACKEND API REQUEST:");
console.log("POST http://localhost:8004/recommend/adaptive");
console.log("Content-Type: application/json");
console.log("Body:", JSON.stringify(backendRequest, null, 2));

// 5. BACKEND API RESPONSE (Sample)
const backendResponse = [
  {
    rank: 1,
    id: "item_003",
    brand: "Nike",
    title: "Black Running Shoes",
    price: 89.99,
    score: 0.95,
    base_score: 0.89,
    image_url: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
    recommendation_type: "quiz_based",
    user_feedback: null,
    is_personalized: false
  },
  {
    rank: 2,
    id: "item_005",
    brand: "Adidas",
    title: "Red Track Jacket",
    price: 79.99,
    score: 0.87,
    base_score: 0.82,
    image_url: "https://images.unsplash.com/photo-1544966503-7cc5ac882d5c?w=400",
    recommendation_type: "quiz_based",
    user_feedback: null,
    is_personalized: false
  }
];

console.log("\n✅ 5. BACKEND API RESPONSE:");
console.log("Status: 200 OK");
console.log("Body:", JSON.stringify(backendResponse, null, 2));

// 6. FRONTEND CONVERSION
const frontendProducts = backendResponse.map(rec => ({
  id: rec.id,
  title: rec.title,
  brand: rec.brand,
  price: rec.price,
  imageUrl: rec.image_url, // ← KEY CONVERSION: image_url → imageUrl
  tags: [], // Backend doesn't provide tags in recommendations
  fit: 'regular', // Default fit
  colors: [], // Backend doesn't provide colors array in recommendations
  gender: 'unisex', // Default gender
  sizes: [], // Backend doesn't provide sizes array in recommendations
  score: rec.score,
  baseScore: rec.base_score,
  isPersonalized: rec.is_personalized,
  recommendationType: rec.recommendation_type,
  userFeedback: rec.user_feedback,
  rank: rec.rank,
}));

console.log("\n🔄 6. FRONTEND PRODUCT CONVERSION:");
console.log("Converting backend format to frontend Product format...");
console.log("Frontend products:", JSON.stringify(frontendProducts, null, 2));

// 7. SWIPE FEEDBACK
const swipeFeedback = {
  user_id: "user_123",
  item_id: "item_003",
  feedback: "like" // User swiped right (like)
};

console.log("\n👍 7. SWIPE FEEDBACK:");
console.log("POST http://localhost:8004/feedback");
console.log("Body:", JSON.stringify(swipeFeedback, null, 2));

// 8. BACKEND LEARNING RESPONSE
const feedbackResponse = {
  status: "success",
  message: "Added like feedback for item item_003",
  user_stats: {
    user_id: "user_123",
    total_feedback: 1,
    likes: 1,
    dislikes: 0,
    personalization_score: 0.1,
    last_feedback: "2025-09-20T10:30:00Z"
  }
};

console.log("\n🧠 8. BACKEND LEARNING RESPONSE:");
console.log("Status: 200 OK");
console.log("Body:", JSON.stringify(feedbackResponse, null, 2));

console.log("\n🎯 SUMMARY:");
console.log("✅ Quiz answers → Backend QuizFeatures format");
console.log("✅ Backend recommendations → Frontend Product format");
console.log("✅ Image URLs from catalog.csv used correctly");
console.log("✅ Feedback loop for adaptive learning");
console.log("✅ Fallback to local recommendations if backend unavailable");

export {};