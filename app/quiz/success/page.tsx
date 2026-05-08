'use client'

import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { motion } from 'framer-motion'
import { CheckCircle, Sparkles, ArrowRight, ChevronDown, ChevronUp, RotateCcw } from 'lucide-react'
import { QuizAnswer } from '@/lib/validators'
import { generateRecommendations } from '@/lib/scoring'
import { useRecommendationStore, useUserStore } from '@/lib/store'
import { fetchRecommendationsForUser, checkFashionAPIHealth } from '@/lib/fashion-api'
import { ResetButton } from '@/components/ResetButton'

interface QuizData {
  quiz: {
    id: string
    userId: string
    answers: QuizAnswer[]
    completed: boolean
    createdAt: string
    lastAnswer: QuizAnswer
  }
  user: {
    id: string
    email: string
  }
}

export default function QuizSuccessPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const quizId = searchParams.get('quizId')
  const { setRecommendations, setLoading: setRecommendationLoading, setError: setRecommendationError } = useRecommendationStore()
  const { userId } = useUserStore()
  
  const [quizData, setQuizData] = useState<QuizData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showLastAnswerDetails, setShowLastAnswerDetails] = useState(false)
  const [isGeneratingRecommendations, setIsGeneratingRecommendations] = useState(false)
  const [useBackendAPI, setUseBackendAPI] = useState(true)

  useEffect(() => {
    if (!quizId) {
      setError('No quiz ID provided')
      setLoading(false)
      return
    }

    fetchQuizData()
  }, [quizId])

  const fetchQuizData = async () => {
    try {
      const response = await fetch(`/api/quiz/${quizId}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch quiz data')
      }
      
      const data = await response.json()
      setQuizData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const handleGoToRecommendations = async () => {
    if (!quizData) return
    
    setIsGeneratingRecommendations(true)
    setRecommendationLoading(true)
    setRecommendationError(null)
    
    try {
      let recommendations = []
      
      if (useBackendAPI) {
        // Try to use the adaptive backend API first
        try {
          console.log('🧠 Checking backend API availability...')
          const isBackendAvailable = await checkFashionAPIHealth()
          
          if (isBackendAvailable && userId) {
            console.log('🎯 Using BACKEND API for adaptive recommendations...')
            recommendations = await fetchRecommendationsForUser(
              userId, 
              quizData.quiz.answers, 
              0.6, // adaptation strength
              10   // return 10 recommendations from backend
            )
            console.log(`✅ Got ${recommendations.length} recommendations from backend API`)
          } else {
            throw new Error('Backend API not available or no userId')
          }
        } catch (backendError) {
          console.warn('⚠️ Backend API failed, falling back to local catalog:', backendError)
          throw backendError // This will trigger the fallback below
        }
      }
      
      // Fallback to local catalog if backend fails or is disabled
      if (recommendations.length === 0) {
        console.log('📦 Using LOCAL catalog recommendations as fallback...')
        recommendations = generateRecommendations(quizData.quiz.answers, 30)
        console.log(`📦 Generated ${recommendations.length} local recommendations from updated catalog`)
      }
      
      // Store recommendations in the global store
      setRecommendations(recommendations)
      
      // Navigate to recommendations page
      router.push('/recommendations')
      
    } catch (err) {
      console.error('❌ Error generating recommendations:', err)
      setRecommendationError(err instanceof Error ? err.message : 'Failed to generate recommendations')
      
      // Final fallback - still try to navigate to recommendations page with local catalog
      try {
        console.log('🆘 Final fallback: generating local recommendations...')
        const fallbackRecommendations = generateRecommendations(quizData.quiz.answers, 30)
        setRecommendations(fallbackRecommendations)
        router.push('/recommendations')
      } catch (fallbackError) {
        console.error('❌ Even fallback recommendations failed:', fallbackError)
      }
    } finally {
      setIsGeneratingRecommendations(false)
      setRecommendationLoading(false)
    }
  }

  const renderLastAnswerValue = (answer: QuizAnswer) => {
    switch (answer.type) {
      case 'single':
        return <span className="font-medium">{answer.value}</span>
      case 'multi':
        return (
          <div className="flex flex-wrap gap-1">
            {answer.value.map((val) => (
              <Badge key={val} variant="secondary">{val}</Badge>
            ))}
          </div>
        )
      case 'scale':
        return <span className="font-medium">${answer.value}</span>
      case 'size':
        return (
          <div className="flex flex-wrap gap-2">
            {Object.entries(answer.value).map(([key, val]) => (
              <Badge key={key} variant="outline">
                {key}: {val}
              </Badge>
            ))}
          </div>
        )
      default:
        return <span>Unknown answer type</span>
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your quiz results...</p>
        </div>
      </div>
    )
  }

  if (error || !quizData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="text-center p-6">
            <p className="text-red-600 mb-4">{error || 'Failed to load quiz data'}</p>
            <Button onClick={() => router.push('/quiz')}>
              Take Quiz Again
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
      <ResetButton />
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-2xl w-full space-y-6"
      >
        {/* Success Header */}
        <Card className="border-0 shadow-2xl">
          <CardContent className="text-center p-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="mx-auto mb-6"
            >
              <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                <CheckCircle className="w-10 h-10 text-white" />
              </div>
            </motion.div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              🎉 Quiz Complete!
            </h1>
            <p className="text-lg text-gray-600 mb-6">
              Amazing! We've captured your style preferences and are ready to show you 
              personalized recommendations {useBackendAPI ? 'from our AI-powered adaptive system' : 'from our curated collection'}.
            </p>
            
            <div className="flex items-center justify-center gap-4 text-sm text-gray-500">
              <span>✨ {quizData.quiz.answers.length} answers captured</span>
              <span>•</span>
              <span>{useBackendAPI ? '🧠 AI-powered recommendations' : '📦 Curated recommendations'}</span>
            </div>
          </CardContent>
        </Card>

        {/* Last Answer Display - Special Requirement */}
        <Card className="border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-500" />
                Your Last Answer Captured
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowLastAnswerDetails(!showLastAnswerDetails)}
              >
                {showLastAnswerDetails ? <ChevronUp /> : <ChevronDown />}
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="bg-purple-50 rounded-lg p-4">
                <p className="text-sm text-purple-600 font-medium mb-2">
                  Question ID: {quizData.quiz.lastAnswer.qid}
                </p>
                <div className="text-purple-900">
                  {renderLastAnswerValue(quizData.quiz.lastAnswer)}
                </div>
              </div>
              
              {showLastAnswerDetails && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  transition={{ duration: 0.3 }}
                >
                  <Card className="bg-gray-50">
                    <CardHeader>
                      <CardTitle className="text-sm">Raw JSON Data</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <pre className="text-xs bg-gray-100 p-3 rounded overflow-x-auto">
                        {JSON.stringify(quizData.quiz.lastAnswer, null, 2)}
                      </pre>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Call to Action */}
        <Card className="border-0 shadow-lg">
          <CardContent className="p-6">
            <div className="text-center space-y-4">
              <h3 className="text-xl font-semibold text-gray-900">
                Ready to see your personalized recommendations?
              </h3>
              <p className="text-gray-600">
                Based on your {quizData.quiz.answers.length} answers, we'll show you clothes 
                that match your style, budget, and preferences.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <Button
                  onClick={handleGoToRecommendations}
                  disabled={isGeneratingRecommendations}
                  size="lg"
                  className="flex-1 flex items-center justify-center gap-2"
                >
                  {isGeneratingRecommendations ? (
                    <>
                      <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                      Generating Recommendations...
                    </>
                  ) : (
                    <>
                      Go to Recommendations
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </Button>
                
                <Button
                  variant="outline"
                  onClick={() => router.push('/quiz')}
                  size="lg"
                >
                  Retake Quiz
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}