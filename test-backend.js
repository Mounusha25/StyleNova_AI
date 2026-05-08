// Quick test script to check backend API endpoints
const BASE_URL = 'http://localhost:8004';

async function testEndpoint(endpoint, method = 'GET', body = null) {
  try {
    console.log(`\n🧪 Testing ${method} ${endpoint}`);
    
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      }
    };
    
    if (body) {
      options.body = JSON.stringify(body);
    }
    
    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    const status = response.status;
    const statusText = response.statusText;
    
    console.log(`   Status: ${status} ${statusText}`);
    
    if (response.ok) {
      const data = await response.json();
      console.log(`   ✅ Success:`, JSON.stringify(data, null, 2));
    } else {
      const errorText = await response.text();
      console.log(`   ❌ Error:`, errorText);
    }
    
    return { status, ok: response.ok };
  } catch (error) {
    console.log(`   💥 Network Error:`, error.message);
    return { error: error.message };
  }
}

async function runTests() {
  console.log('🚀 Testing Fashion API Backend\n');
  
  // Test basic endpoints
  await testEndpoint('/');
  await testEndpoint('/health');
  await testEndpoint('/docs'); // This might be GET only
  
  // Test recommendations endpoint (should require POST)
  await testEndpoint('/recommend/adaptive', 'GET'); // This should fail with 405
  
  // Test with proper POST request
  const sampleRequest = {
    user_id: 'test_user_123',
    brand_name: 'Nike',
    adaptation_strength: 0.5,
    k: 5
  };
  
  await testEndpoint('/recommend/adaptive', 'POST', sampleRequest);
  
  // Test feedback endpoint
  const feedbackRequest = {
    user_id: 'test_user_123',
    item_id: 'item_001',
    feedback: 'like'
  };
  
  await testEndpoint('/feedback', 'POST', feedbackRequest);
  
  console.log('\n🏁 Test completed!');
}

runTests().catch(console.error);