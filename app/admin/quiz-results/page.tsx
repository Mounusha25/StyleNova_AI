'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
// import { Input } from '@/components/ui/input'
import { Input } from '@/components/Input' // Update this path to the correct location of your Input component
import { Label } from '@/components/ui/label'
import { Search, Eye, Calendar, User } from 'lucide-react'
import { QuizAnswer } from '@/lib/validators'

interface QuizResult {
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

export default function QuizResultsPage() {
  const [quizId, setQuizId] = useState('')
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchQuizResult = async () => {
    if (!quizId.trim()) {
      setError('Please enter a Quiz ID')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/quiz/${quizId}`)
      
      if (!response.ok) {
        throw new Error('Quiz not found')
      }
      
      const data = await response.json()
      setQuizResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setQuizResult(null)
    } finally {
      setLoading(false)
    }
  }

  const renderAnswerValue = (answer: QuizAnswer) => {
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

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="w-5 h-5" />
              Quiz Results Viewer
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <Label htmlFor="quizId">Quiz ID</Label>
                <Input
                  id="quizId"
                  placeholder="Enter quiz ID (e.g., cmfsnjowp0001e84gl4pxmy7c)"
                  value={quizId}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuizId(e.target.value)}
                  onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && fetchQuizResult()}
                />
              </div>
              <div className="flex items-end">
                <Button onClick={fetchQuizResult} disabled={loading}>
                  {loading ? 'Loading...' : 'View Results'}
                </Button>
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600">{error}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {quizResult && (
          <div className="space-y-6">
            {/* Quiz Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="w-5 h-5" />
                  Quiz Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">User ID</p>
                      <p className="font-mono text-sm">{quizResult.user.id}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Completed</p>
                      <p className="text-sm">{new Date(quizResult.quiz.createdAt).toLocaleString()}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Total Answers</p>
                    <p className="text-2xl font-bold text-green-600">{quizResult.quiz.answers.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Last Answer (Special Requirement) */}
            <Card className="border-purple-200 bg-purple-50">
              <CardHeader>
                <CardTitle className="text-purple-700">🌟 Last Answer (Special Display)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-white p-4 rounded-lg">
                  <p className="text-sm text-purple-600 font-medium mb-2">
                    Question ID: {quizResult.quiz.lastAnswer.qid}
                  </p>
                  <div className="text-purple-900">
                    {renderAnswerValue(quizResult.quiz.lastAnswer)}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* All Answers */}
            <Card>
              <CardHeader>
                <CardTitle>All Quiz Answers ({quizResult.quiz.answers.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {quizResult.quiz.answers.map((answer, index) => (
                    <div key={answer.qid} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium">Question {answer.qid}</h4>
                        <Badge variant="outline">{answer.type}</Badge>
                      </div>
                      <div className="text-gray-700">
                        {renderAnswerValue(answer)}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Raw JSON */}
            <Card>
              <CardHeader>
                <CardTitle>Raw Data (JSON)</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto">
                  {JSON.stringify(quizResult, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}