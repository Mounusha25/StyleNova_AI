'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { QuestionCard } from './QuestionCard'
import { StepNav } from './StepNav'
import { quizQuestions } from '@/lib/catalog'
import { useQuizStore, useUserStore } from '@/lib/store'
import { QuizAnswer } from '@/lib/validators'
import { useRouter } from 'next/navigation'

const quizFormSchema = z.object({
  answers: z.array(z.any()).min(1, "Please answer at least one question")
})

type QuizFormData = z.infer<typeof quizFormSchema>

export function QuizWizard() {
  const router = useRouter()
  const { answers, currentStep, setCurrentStep, setAnswer, markCompleted } = useQuizStore()
  const { userId, setUser } = useUserStore()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const totalSteps = Math.max(...quizQuestions.map(q => q.step))
  const currentQuestions = quizQuestions.filter(q => q.step === currentStep)
  const progress = (currentStep / totalSteps) * 100

  const form = useForm<QuizFormData>({
    resolver: zodResolver(quizFormSchema),
    defaultValues: {
      answers: answers
    }
  })

  const handleAnswerChange = (questionId: string, answer: QuizAnswer) => {
    setAnswer(answer)
  }

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    } else {
      handleSubmit()
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    
    try {
      // Generate a user ID if we don't have one
      const currentUserId = userId || `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      if (!userId) {
        setUser(currentUserId)
      }

      // Submit quiz to API
      const response = await fetch('/api/quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: currentUserId,
          answers: answers,
          completedAt: new Date().toISOString()
        })
      })

      if (!response.ok) {
        throw new Error('Failed to submit quiz')
      }

      const result = await response.json()
      markCompleted(result.quizId)
      
      // Navigate to success page
      router.push(`/quiz/success?quizId=${result.quizId}`)
    } catch (error) {
      console.error('Error submitting quiz:', error)
      // TODO: Show error message to user
    } finally {
      setIsSubmitting(false)
    }
  }

  const canProceed = () => {
    // Check if all required questions in current step are answered
    const requiredQuestions = currentQuestions.filter(q => q.required)
    return requiredQuestions.every(q => 
      answers.some(a => a.qid === q.id)
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">Style Quiz</h1>
            <div className="text-sm text-gray-600">
              Step {currentStep} of {totalSteps}
            </div>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Questions */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
            className="mb-8"
          >
            <div className="space-y-6">
              {currentQuestions.map((question) => (
                <QuestionCard
                  key={question.id}
                  question={question}
                  value={answers.find(a => a.qid === question.id)}
                  onChange={(answer) => handleAnswerChange(question.id, answer)}
                />
              ))}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <StepNav
          currentStep={currentStep}
          totalSteps={totalSteps}
          canProceed={canProceed()}
          isSubmitting={isSubmitting}
          onBack={handleBack}
          onNext={handleNext}
          onSaveAndExit={() => {
            // TODO: Implement save and exit
            router.push('/')
          }}
        />
      </div>
    </div>
  )
}