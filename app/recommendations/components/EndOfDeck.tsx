'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { motion } from 'framer-motion'
import { RotateCcw, Filter, Heart, Home } from 'lucide-react'
import Link from 'next/link'

interface EndOfDeckProps {
  likedCount: number
  totalSeen: number
  onRetakeQuiz: () => void
  onRefineFilters: () => void
}

export function EndOfDeck({ 
  likedCount, 
  totalSeen, 
  onRetakeQuiz, 
  onRefineFilters 
}: EndOfDeckProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-md w-full"
      >
        <Card className="border-0 shadow-2xl">
          <CardContent className="text-center p-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="mx-auto mb-6"
            >
              <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                <Heart className="w-10 h-10 text-white" />
              </div>
            </motion.div>

            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              You've seen it all! 🎉
            </h1>

            <p className="text-gray-600 mb-6">
              Great job exploring our recommendations! You looked at {totalSeen} items 
              and liked {likedCount} of them.
            </p>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-600">
                  {totalSeen}
                </div>
                <div className="text-sm text-purple-600">Items Seen</div>
              </div>
              <div className="bg-pink-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-pink-600">
                  {likedCount}
                </div>
                <div className="text-sm text-pink-600">Items Liked</div>
              </div>
            </div>

            {/* Liked percentage */}
            {totalSeen > 0 && (
              <div className="mb-6">
                <div className="text-sm text-gray-600 mb-2">
                  You liked {Math.round((likedCount / totalSeen) * 100)}% of what you saw
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${(likedCount / totalSeen) * 100}%` }}
                  />
                </div>
              </div>
            )}

            {/* Action buttons */}
            <div className="space-y-3">
              <Button
                onClick={onRetakeQuiz}
                size="lg"
                className="w-full flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Retake Style Quiz
              </Button>

              <Button
                variant="outline"
                onClick={onRefineFilters}
                size="lg"
                className="w-full flex items-center justify-center gap-2"
              >
                <Filter className="w-4 h-4" />
                Refine Filters
              </Button>

              <Button
                variant="ghost"
                asChild
                size="lg"
                className="w-full flex items-center justify-center gap-2"
              >
                <Link href="/">
                  <Home className="w-4 h-4" />
                  Back to Home
                </Link>
              </Button>
            </div>

            {/* Encouragement message */}
            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                {likedCount > 0 ? (
                  <>
                    💡 <strong>Pro tip:</strong> Your {likedCount} liked items are saved! 
                    Take the quiz again anytime to discover more pieces that match your evolving style.
                  </>
                ) : (
                  <>
                    😊 <strong>No worries!</strong> Style preferences are personal. 
                    Try retaking the quiz with different answers to see fresh recommendations.
                  </>
                )}
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}