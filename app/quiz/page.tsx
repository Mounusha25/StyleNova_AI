'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { motion } from 'framer-motion'
import { CheckCircle, Clock, Star } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'
import { QuizWizard } from './components/QuizWizard'

export default function QuizPage() {
  const [hasStarted, setHasStarted] = useState(false)

  if (hasStarted) {
    return <QuizWizard />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-2xl w-full"
      >
        <Card className="border-0 shadow-2xl">
          <CardHeader className="text-center pb-6">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="mx-auto mb-4"
            >
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                <Star className="w-8 h-8 text-white" />
              </div>
            </motion.div>
            <CardTitle className="text-3xl font-bold text-gray-900 mb-2">
              Discover Your Perfect Style
            </CardTitle>
            <p className="text-lg text-gray-600">
              Take our 5-minute style quiz to get personalized recommendations from 1,000s of brands
            </p>
          </CardHeader>

          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="text-center p-4 rounded-lg bg-gray-50"
              >
                <Clock className="w-6 h-6 text-purple-500 mx-auto mb-2" />
                <p className="font-semibold text-gray-900">5 Minutes</p>
                <p className="text-sm text-gray-600">Quick & easy</p>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                className="text-center p-4 rounded-lg bg-gray-50"
              >
                <CheckCircle className="w-6 h-6 text-green-500 mx-auto mb-2" />
                <p className="font-semibold text-gray-900">12 Questions</p>
                <p className="text-sm text-gray-600">Personalized results</p>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="text-center p-4 rounded-lg bg-gray-50"
              >
                <Star className="w-6 h-6 text-yellow-500 mx-auto mb-2" />
                <p className="font-semibold text-gray-900">Free Forever</p>
                <p className="text-sm text-gray-600">No subscription</p>
              </motion.div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">What we'll ask you:</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Your size preferences and fit</li>
                <li>• Budget and style preferences</li>
                <li>• Favorite colors and occasions</li>
                <li>• Lifestyle and body type</li>
              </ul>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <motion.div
                className="flex-1"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button 
                  onClick={() => setHasStarted(true)}
                  size="lg" 
                  className="w-full text-lg py-6 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                >
                  Start Your Style Quiz
                </Button>
              </motion.div>
              <Button variant="outline" size="lg" className="px-6" asChild>
                <Link href="/">
                  Back to Home
                </Link>
              </Button>
            </div>

            <p className="text-center text-xs text-gray-500">
              By taking the quiz, you agree to our Privacy Policy. No payment required.
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}