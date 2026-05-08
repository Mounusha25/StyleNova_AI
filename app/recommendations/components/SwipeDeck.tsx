'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence, PanInfo } from 'framer-motion'
import { ProductCard } from './ProductCard'
import { useRecommendationStore, useUserStore } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { Heart, X, Sparkles, Brain, TrendingUp } from 'lucide-react'
import { submitFeedback, FashionAPIError, getAdaptiveRecommendations, convertRecommendationToProduct } from '@/lib/fashion-api'

export function SwipeDeck() {
  const { recommendations, currentIndex, swipeProduct, addRecommendations, likedProducts, passedProducts } = useRecommendationStore()
  const { userId } = useUserStore()
  const [isAnimating, setIsAnimating] = useState(false)
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false)
  const [isFetchingNewRecommendations, setIsFetchingNewRecommendations] = useState(false)
  const [adaptationCount, setAdaptationCount] = useState(0)
  const [userPersonalizationScore, setUserPersonalizationScore] = useState(0.75) // Demo: Show 75% for testing
  const [showAdaptationBadge, setShowAdaptationBadge] = useState(false)
  const [lastAdaptationAt, setLastAdaptationAt] = useState(0) // Track when last adaptation happened

  const currentProduct = recommendations[currentIndex]
  const nextProduct = recommendations[currentIndex + 1]
  const totalSwipes = likedProducts.length + passedProducts.length

  // Check if we need to fetch more recommendations - Every 3 swipes (but only once per milestone)
  useEffect(() => {
    const shouldFetchMore = (
      totalSwipes > 0 && // Only after user has provided some feedback
      totalSwipes % 3 === 0 && // Every 3rd swipe
      totalSwipes > lastAdaptationAt && // Only if we haven't adapted at this count yet
      !isFetchingNewRecommendations && // Don't fetch if already fetching
      userId // Only if we have a user ID
    )

    if (shouldFetchMore) {
      setLastAdaptationAt(totalSwipes) // Mark this adaptation point
      fetchAdaptiveRecommendations()
    }
  }, [totalSwipes, isFetchingNewRecommendations, userId, lastAdaptationAt])

  const fetchAdaptiveRecommendations = async () => {
    if (!userId || isFetchingNewRecommendations) return

    setIsFetchingNewRecommendations(true)
    
    try {
      console.log(`🧠 Fetching adaptive recommendations at ${totalSwipes} total swipes...`)
      
      // Smart exclusion: Only exclude items that have been disliked MULTIPLE times
      // or very recently (to avoid immediate repetition)
      const recentlyPassedIds = passedProducts.slice(-3).map(p => p.id) // Last 3 passed items
      
      // Count how many times each item was disliked
      const dislikeCount = passedProducts.reduce((count, product) => {
        count[product.id] = (count[product.id] || 0) + 1
        return count
      }, {} as Record<string, number>)
      
      // Only exclude items that were disliked 2+ times OR very recently passed
      const excludeItemIds = passedProducts
        .filter(p => dislikeCount[p.id] >= 2 || recentlyPassedIds.includes(p.id))
        .map(p => p.id)
      
      console.log(`🚫 Smart exclusion: ${excludeItemIds.length} items (heavily disliked or recent)`)
      console.log(`🔄 Adaptive: ${passedProducts.length - excludeItemIds.length} passed items may reappear for learning`)
      console.log(`❤️ Positive signals: ${likedProducts.length} liked items guide recommendations`)
      
      // Higher adaptation strength to show real-time learning
      const adaptationStrength = Math.min(0.9, 0.5 + (totalSwipes * 0.05)) // Increase with more feedback
      
      const newRecommendations = await getAdaptiveRecommendations(
        userId,
        excludeItemIds, // Pass excluded items
        adaptationStrength,
        5 // Fetch 5 new recommendations
      )
      
      // Convert backend recommendations to frontend format
      const newProducts = newRecommendations.map(convertRecommendationToProduct)
      
      // Add to existing recommendations
      addRecommendations(newProducts)
      
      // Show adaptation indicators
      setAdaptationCount(prev => prev + 1)
      setShowAdaptationBadge(true)
      setTimeout(() => setShowAdaptationBadge(false), 8000) // Increased from 3 to 8 seconds
      
      console.log(`✅ Added ${newProducts.length} NEW adaptive recommendations (adaptation #${adaptationCount + 1})`)
      
    } catch (error) {
      console.error('❌ Failed to fetch adaptive recommendations:', error)
    } finally {
      // Add a small delay before allowing next fetch
      setTimeout(() => {
        setIsFetchingNewRecommendations(false)
      }, 1000) // 1 second cooldown
    }
  }

  const handleSwipe = async (direction: 'like' | 'pass') => {
    if (!currentProduct || isAnimating || isSubmittingFeedback) return
    
    setIsAnimating(true)
    setIsSubmittingFeedback(true)
    
    // Submit feedback to the adaptive backend API
    if (userId) {
      try {
        const feedback = direction === 'like' ? 'like' : 'dislike'
        const response = await submitFeedback(userId, currentProduct.id, feedback)
        
        console.log('✅ Feedback submitted successfully:', {
          user: userId,
          item_id: currentProduct.id,
          feedback: feedback,
          userStats: response.user_stats
        })
        
        // Update personalization score for UI display
        if (response.user_stats.personalization_score !== undefined) {
          setUserPersonalizationScore(response.user_stats.personalization_score)
        }
        
        // Log user learning progress
        if (response.user_stats.personalization_score > 0) {
          console.log(`🧠 User personalization score: ${response.user_stats.personalization_score}`)
        }
        
      } catch (error) {
        console.error('❌ Error submitting feedback to fashion API:', error)
        
        if (error instanceof FashionAPIError) {
          console.error('Fashion API Error:', {
            message: error.message,
            status: error.status,
            response: error.response
          })
        }
        
        // Still proceed with local state update even if API fails
        // This ensures the UI doesn't get stuck
      }
    } else {
      console.warn('⚠️ No userId available for feedback submission')
    }
    
    // Also submit to existing Next.js API for compatibility
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId,
          productId: currentProduct.id,
          action: direction,
          score: direction === 'like' ? 1 : 0
        })
      })
    } catch (error) {
      console.error('Error logging feedback to Next.js API:', error)
    }
    
    // Update the local store
    swipeProduct(direction)
    
    // Reset animation states after a short delay
    setTimeout(() => {
      setIsAnimating(false)
      setIsSubmittingFeedback(false)
    }, 300)
  }

  if (!currentProduct) return null

  return (
    <div className="max-w-sm sm:max-w-md mx-auto relative">
      
      {/* Cards Area - Clean UI */}
      <div className="relative h-[500px] sm:h-[600px] mb-6">
        <AnimatePresence mode="wait">
        {/* Next card (background) */}
        {nextProduct && (
          <motion.div
            key={`next-${nextProduct.id}`}
            className="absolute inset-0 z-0"
            initial={{ scale: 0.95, opacity: 0.7 }}
            animate={{ scale: 0.95, opacity: 0.7 }}
            style={{ 
              transform: 'translateY(10px)',
              filter: 'blur(1px)'
            }}
          >
            <ProductCard product={nextProduct} />
          </motion.div>
        )}

        {/* Current card (foreground) */}
        <motion.div
          key={`current-${currentProduct.id}`}
          className="absolute inset-0 z-10 cursor-grab active:cursor-grabbing touch-pan-x"
          initial={{ scale: 1, opacity: 1, rotate: 0 }}
          animate={{ scale: 1, opacity: 1, rotate: 0 }}
          exit={{ 
            x: Math.random() > 0.5 ? 300 : -300,
            rotate: Math.random() > 0.5 ? 15 : -15,
            opacity: 0,
            transition: { duration: 0.3 }
          }}
          drag="x"
          dragConstraints={{ left: -300, right: 300 }}
          dragElastic={0.2}
          onDragEnd={(_, info: PanInfo) => {
            const swipeThreshold = 50
            const swipeVelocityThreshold = 300
            
            if (Math.abs(info.offset.x) > swipeThreshold || Math.abs(info.velocity.x) > swipeVelocityThreshold) {
              const direction = info.offset.x > 0 ? 'like' : 'pass'
              handleSwipe(direction)
            }
          }}
          whileDrag={{
            scale: 1.05
          }}
        >
          <ProductCard product={currentProduct} />
          
          {/* Swipe indicators */}
          <motion.div
            className="absolute top-4 sm:top-8 left-4 sm:left-8 bg-green-500 text-white px-3 py-1 sm:px-4 sm:py-2 rounded-full font-bold text-sm sm:text-base opacity-0"
          >
            LIKE
          </motion.div>
          
          <motion.div
            className="absolute top-4 sm:top-8 right-4 sm:right-8 bg-red-500 text-white px-3 py-1 sm:px-4 sm:py-2 rounded-full font-bold text-sm sm:text-base opacity-0"
          >
            PASS
          </motion.div>
        </motion.div>
      </AnimatePresence>

      {/* Action buttons */}
      <div className="absolute bottom-2 sm:bottom-4 left-1/2 transform -translate-x-1/2 flex gap-3 sm:gap-4 z-20">
        <Button
          variant="outline"
          size="lg"
          onClick={() => handleSwipe('pass')}
          disabled={isAnimating || isSubmittingFeedback}
          className="w-12 h-12 sm:w-14 sm:h-14 rounded-full border-2 border-red-300 hover:border-red-500 hover:bg-red-50 disabled:opacity-50"
        >
          <X className="w-5 h-5 sm:w-6 sm:h-6 text-red-500" />
        </Button>
        
        <Button
          size="lg"
          onClick={() => handleSwipe('like')}
          disabled={isAnimating || isSubmittingFeedback}
          className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-green-500 hover:bg-green-600 disabled:opacity-50"
        >
          <Heart className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
        </Button>
      </div>
      </div>

      {/* Adaptation Indicators Section - Below Cards */}
      <div className="space-y-4 mt-6">
        
        {/* Current Stats Display */}
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-4">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-4">
              <span className="font-medium text-gray-700">Progress:</span>
              <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-bold">
                ❤️ {likedProducts.length} liked
              </span>
              <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-bold">
                ➡️ {passedProducts.length} passed
              </span>
            </div>
            <div className="text-gray-600 font-medium">
              Total: {totalSwipes} interactions
            </div>
          </div>
        </div>

        {/* AI Learning Progress */}
        {userPersonalizationScore > 0 && (
          <div className="bg-gradient-to-r from-purple-100 to-blue-100 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-600" />
                <span className="font-medium text-purple-900">AI Learning Progress</span>
              </div>
              <div className="bg-purple-200 rounded-full px-3 py-1">
                <span className="text-sm font-bold text-purple-800">
                  {Math.round(userPersonalizationScore * 100)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Adaptation Status */}
        {adaptationCount > 0 && (
          <div className="bg-gradient-to-r from-green-100 to-blue-100 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                <span className="font-medium text-green-900">AI Adaptations Completed</span>
              </div>
              <div className="bg-green-200 rounded-full px-3 py-1">
                <span className="text-sm font-bold text-green-800">
                  {adaptationCount} times adapted
                </span>
              </div>
            </div>
            <div className="mt-2 text-xs text-green-700">
              Next adaptation after {3 - (totalSwipes % 3)} more swipes
            </div>
          </div>
        )}

        {/* Adaptation Success Banner */}
        {showAdaptationBadge && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg p-4 shadow-lg"
          >
            <div className="flex items-center justify-center">
              <Sparkles className="w-6 h-6 mr-3 animate-pulse" />
              <div className="text-center">
                <div className="font-bold text-lg">🎯 AI ADAPTED!</div>
                <div className="text-sm opacity-90">
                  New recommendations based on your preferences!
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Loading New Recommendations */}
        {isFetchingNewRecommendations && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4"
          >
            <div className="flex items-center justify-center">
              <div className="animate-spin w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full mr-3" />
              <span className="text-blue-700 font-medium">
                🧠 Finding better matches based on your preferences...
              </span>
            </div>
          </motion.div>
        )}

        {/* Manual Adaptation Trigger */}
        {totalSwipes > 2 && (
          <div className="text-center">
            <Button
              onClick={fetchAdaptiveRecommendations}
              disabled={isFetchingNewRecommendations}
              variant="outline"
              size="lg"
              className="bg-gradient-to-r from-purple-100 to-blue-100 border-purple-300 hover:from-purple-200 hover:to-blue-200 px-6 py-3"
            >
              {isFetchingNewRecommendations ? (
                <>
                  <div className="animate-spin w-4 h-4 border-2 border-purple-500 border-t-transparent rounded-full mr-2" />
                  AI Learning...
                </>
              ) : (
                <>
                  <Brain className="w-4 h-4 mr-2" />
                  🎯 Force AI Adaptation Now!
                </>
              )}
            </Button>
            <p className="text-xs text-gray-500 mt-2">
              Click to manually trigger AI learning & get new recommendations
            </p>
          </div>
        )}

        {/* Achievement Progress */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <div className="text-center">
            <div className="text-sm font-medium text-yellow-800 mb-1">
              🏆 Recommendation Goal: 45+ items
            </div>
            <div className="flex items-center justify-center gap-2">
              <div className="bg-yellow-200 rounded-full h-2 flex-1 max-w-xs">
                <div 
                  className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(100, (totalSwipes / 45) * 100)}%` }}
                ></div>
              </div>
              <span className="text-xs text-yellow-700 font-bold">
                {totalSwipes}/45
              </span>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}

export default SwipeDeck