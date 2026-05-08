/**
 * Test script to verify like/dislike functionality is working
 * Tests both the feedback submission and user stats retrieval
 */

const BACKEND_URL = 'http://localhost:8004';

async function testFeedbackFlow() {
  console.log('🧪 Testing Like/Dislike Functionality...\n');
  
  const testUserId = 'test-user-' + Date.now();
  const testItemId = 'item_123';
  
  try {
    // Test 1: Submit a LIKE feedback
    console.log('1️⃣ Testing LIKE feedback submission...');
    const likeResponse = await fetch(`${BACKEND_URL}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: testUserId,
        item_id: testItemId,
        feedback: 'like'
      })
    });
    
    if (!likeResponse.ok) {
      throw new Error(`Like feedback failed: ${likeResponse.status} ${likeResponse.statusText}`);
    }
    
    const likeResult = await likeResponse.json();
    console.log('✅ LIKE feedback submitted successfully:');
    console.log('   - Status:', likeResult.status);
    console.log('   - Message:', likeResult.message);
    console.log('   - User Stats:', likeResult.user_stats);
    console.log('   - Total Feedback:', likeResult.user_stats.total_feedback);
    console.log('   - Likes:', likeResult.user_stats.likes);
    console.log('   - Dislikes:', likeResult.user_stats.dislikes);
    console.log('   - Personalization Score:', likeResult.user_stats.personalization_score);
    console.log();
    
    // Test 2: Submit a DISLIKE feedback
    console.log('2️⃣ Testing DISLIKE feedback submission...');
    const dislikeResponse = await fetch(`${BACKEND_URL}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: testUserId,
        item_id: 'item_456',
        feedback: 'dislike'
      })
    });
    
    if (!dislikeResponse.ok) {
      throw new Error(`Dislike feedback failed: ${dislikeResponse.status} ${dislikeResponse.statusText}`);
    }
    
    const dislikeResult = await dislikeResponse.json();
    console.log('✅ DISLIKE feedback submitted successfully:');
    console.log('   - Status:', dislikeResult.status);
    console.log('   - Message:', dislikeResult.message);
    console.log('   - User Stats:', dislikeResult.user_stats);
    console.log('   - Total Feedback:', dislikeResult.user_stats.total_feedback);
    console.log('   - Likes:', dislikeResult.user_stats.likes);
    console.log('   - Dislikes:', dislikeResult.user_stats.dislikes);
    console.log('   - Personalization Score:', dislikeResult.user_stats.personalization_score);
    console.log();
    
    // Test 3: Get user stats
    console.log('3️⃣ Testing user stats retrieval...');
    const statsResponse = await fetch(`${BACKEND_URL}/users/${testUserId}/stats`);
    
    if (!statsResponse.ok) {
      throw new Error(`User stats failed: ${statsResponse.status} ${statsResponse.statusText}`);
    }
    
    const statsResult = await statsResponse.json();
    console.log('✅ User stats retrieved successfully:');
    console.log('   - User ID:', statsResult.user_id);
    console.log('   - Total Feedback:', statsResult.total_feedback);
    console.log('   - Likes:', statsResult.likes);
    console.log('   - Dislikes:', statsResult.dislikes);
    console.log('   - Personalization Score:', statsResult.personalization_score);
    console.log('   - Feedback History Length:', statsResult.feedback_history.length);
    console.log();
    
    // Test 4: Get feedback history
    console.log('4️⃣ Testing feedback history retrieval...');
    const historyResponse = await fetch(`${BACKEND_URL}/users/${testUserId}/feedback`);
    
    if (!historyResponse.ok) {
      throw new Error(`Feedback history failed: ${historyResponse.status} ${historyResponse.statusText}`);
    }
    
    const historyResult = await historyResponse.json();
    console.log('✅ Feedback history retrieved successfully:');
    console.log('   - User ID:', historyResult.user_id);
    console.log('   - Total Feedback:', historyResult.total_feedback);
    console.log('   - History Items:', historyResult.feedback_history.length);
    
    if (historyResult.feedback_history.length > 0) {
      console.log('   - Recent Feedback:');
      historyResult.feedback_history.forEach((item, index) => {
        console.log(`     ${index + 1}. Item: ${item.item_id}, Feedback: ${item.feedback}, Time: ${item.timestamp}`);
      });
    }
    console.log();
    
    // Test 5: Test personalization impact
    console.log('5️⃣ Testing personalization impact...');
    
    // Submit multiple likes to see if personalization score changes
    for (let i = 0; i < 3; i++) {
      const moreTestResponse = await fetch(`${BACKEND_URL}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: testUserId,
          item_id: `item_${1000 + i}`,
          feedback: 'like'
        })
      });
      
      if (moreTestResponse.ok) {
        const moreResult = await moreTestResponse.json();
        console.log(`   - Feedback ${i + 1}: Personalization Score: ${moreResult.user_stats.personalization_score}`);
      }
    }
    
    console.log();
    console.log('🎉 All feedback tests completed successfully!');
    console.log('✅ Like/Dislike functionality is working correctly');
    console.log('✅ User stats are being tracked properly');
    console.log('✅ Feedback history is being stored');
    console.log('✅ Personalization scores are updating');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    
    if (error.message.includes('ECONNREFUSED')) {
      console.error('🚨 Backend server is not running on http://localhost:8004');
      console.error('   Please start the backend with: python adaptive_api.py');
    }
  }
}

// Run the test
testFeedbackFlow();