/**
 * CORS Test Script
 * Run this in the browser console at http://localhost:3000 to test CORS
 */

async function testCORS() {
  console.log('🧪 Testing CORS for Fashion API...');
  
  try {
    // Test health endpoint
    console.log('Testing GET /health...');
    const healthResponse = await fetch('http://localhost:8004/health', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (healthResponse.ok) {
      const healthData = await healthResponse.json();
      console.log('✅ CORS Health Check SUCCESS:', healthData);
    } else {
      console.log('❌ Health Check Failed:', healthResponse.status, healthResponse.statusText);
    }
    
    // Test recommendations endpoint
    console.log('Testing POST /recommend/adaptive...');
    const recResponse = await fetch('http://localhost:8004/recommend/adaptive', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: 'cors_test_user',
        quiz_features: {
          size: 'M',
          preferred_categories: ['shirt'],
          preferred_colors: ['black'],
          max_price: 100,
          preferred_brands: ['zara'],
          preferred_styles: ['casual']
        },
        adaptation_strength: 0.5,
        k: 3
      })
    });
    
    if (recResponse.ok) {
      const recData = await recResponse.json();
      console.log('✅ CORS Recommendations SUCCESS:', recData);
    } else {
      console.log('❌ Recommendations Failed:', recResponse.status, recResponse.statusText);
    }
    
  } catch (error) {
    console.log('💥 CORS Test Error:', error.message);
    
    if (error.message.includes('CORS')) {
      console.log('🔧 CORS Fix Needed: Add CORS middleware to FastAPI backend');
    }
  }
}

// Auto-run if in browser
if (typeof window !== 'undefined') {
  testCORS();
} else {
  module.exports = { testCORS };
}