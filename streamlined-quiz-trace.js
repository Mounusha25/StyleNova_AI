/**
 * Updated Quiz Flow Tracer - Streamlined for Backend API
 */

// 1. NEW STREAMLINED QUIZ SUBMISSION
const streamlinedQuizAnswers = [
  { qid: "categories", type: "multi", value: ["shoes", "shirt"] },
  { qid: "colors", type: "multi", value: ["black", "white"] },
  { qid: "brands", type: "multi", value: ["nike", "zara"] },
  { qid: "styles", type: "multi", value: ["casual", "sporty"] },
  { qid: "size", type: "single", value: "M" },
  { qid: "budget", type: "scale", value: 100 }
];

console.log("📝 1. STREAMLINED QUIZ SUBMISSION:");
console.log("Only 6 questions instead of 12!");
console.log("Quiz answers:", JSON.stringify(streamlinedQuizAnswers, null, 2));

// 2. DIRECT MAPPING TO BACKEND API
const backendRequest = {
  user_id: "user_123",
  quiz_features: {
    size: "M",
    preferred_categories: ["shoes", "shirt"],
    preferred_colors: ["black", "white"],
    max_price: 100,
    preferred_brands: ["nike", "zara"],
    preferred_styles: ["casual", "sporty"]
  },
  adaptation_strength: 0.5,
  k: 10
};

console.log("\n🎯 2. PERFECT BACKEND API MAPPING:");
console.log("POST http://localhost:8004/recommend/adaptive");
console.log("Body:", JSON.stringify(backendRequest, null, 2));

// 3. QUIZ QUESTIONS REMOVED
const removedQuestions = [
  "What's your gender?",
  "What's your age range?", 
  "How much do you spend on tops?",
  "How much do you spend on bottoms?",
  "What occasions do you dress for?",
  "What colors do you avoid?",
  "What's your preferred jean fit?",
  "How adventurous are you with trends?",
  "What's your body type?"
];

console.log("\n❌ 3. REMOVED IRRELEVANT QUESTIONS:");
removedQuestions.forEach(q => console.log(`   - ${q}`));

// 4. KEPT ESSENTIAL QUESTIONS
const keptQuestions = [
  "What types of clothing are you looking for? → preferred_categories",
  "What colors do you prefer? → preferred_colors", 
  "Which brands do you like? → preferred_brands",
  "Which styles appeal to you? → preferred_styles",
  "What's your size? → size",
  "What's your maximum budget per item? → max_price"
];

console.log("\n✅ 4. KEPT ESSENTIAL QUESTIONS:");
keptQuestions.forEach(q => console.log(`   - ${q}`));

console.log("\n🎯 BENEFITS:");
console.log("✅ Reduced from 12 questions to 6 (50% shorter)");
console.log("✅ Perfect 1:1 mapping to backend API");
console.log("✅ No unnecessary data processing");
console.log("✅ Faster user experience");
console.log("✅ Direct backend integration");

export {};