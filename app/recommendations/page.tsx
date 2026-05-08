'use client'

import { useEffect, useState } from 'react'
import { SwipeDeck } from './components/SwipeDeck'
import { EndOfDeck } from './components/EndOfDeck'
import { useRecommendationStore } from '@/lib/store'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ArrowLeft, RotateCcw } from 'lucide-react'
import Link from 'next/link'
import { motion } from 'framer-motion'

export default function RecommendationsPage() {
  const { 
    recommendations, 
    currentIndex, 
    likedProducts, 
    passedProducts,
    isLoading,
    error,
    undoLastSwipe,
    reset
  } = useRecommendationStore()
  
  const [hasStarted, setHasStarted] = useState(false)
  
  useEffect(() => {
    if (recommendations.length > 0) {
      setHasStarted(true)
    }
  }, [recommendations])

  const isFinished = currentIndex >= recommendations.length
  const canUndo = currentIndex > 0

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="text-center p-8">
            <div className="animate-spin w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Getting Your Recommendations
            </h2>
            <p className="text-gray-600">
              Our AI is analyzing your style preferences and finding the perfect matches...
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="text-center p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Oops! Something went wrong
            </h2>
            <p className="text-gray-600 mb-6">
              {error}
            </p>
            <div className="space-y-3">
              <Button onClick={() => window.location.reload()}>
                Try Again
              </Button>
              <Button variant="outline" asChild>
                <Link href="/quiz">Retake Quiz</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!hasStarted || recommendations.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="text-center p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              No Recommendations Yet
            </h2>
            <p className="text-gray-600 mb-6">
              Take our style quiz first to get personalized clothing recommendations.
            </p>
            <Button asChild>
              <Link href="/quiz">Take Style Quiz</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (isFinished) {
    return (
      <EndOfDeck 
        likedCount={likedProducts.length}
        totalSeen={currentIndex}
        onRetakeQuiz={() => reset()}
        onRefineFilters={() => {
          // TODO: Implement filter refinement
          console.log('Refine filters')
        }}
      />
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/quiz/success" className="flex items-center gap-2">
                  <ArrowLeft className="w-4 h-4" />
                  Back to Results
                </Link>
              </Button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Your Style Recommendations
                </h1>
                <p className="text-sm text-gray-600">
                  {currentIndex + 1} of {recommendations.length} • {likedProducts.length} liked
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  reset()
                  window.location.href = '/quiz/success'
                }}
                className="flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Reload Catalog
              </Button>
              {canUndo && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={undoLastSwipe}
                  className="flex items-center gap-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  Undo
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Swipe Deck */}
      <div className="flex-1 p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <SwipeDeck />
        </motion.div>
      </div>

      {/* Progress indicator */}
      <div className="bg-white border-t p-4">
        <div className="max-w-md mx-auto">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{Math.round((currentIndex / recommendations.length) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-pink-500 to-purple-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentIndex / recommendations.length) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}