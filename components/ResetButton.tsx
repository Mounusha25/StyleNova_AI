'use client'

import { Button } from "@/components/ui/button"
import { useQuizStore, useRecommendationStore, useUserStore } from "@/lib/store"
import { clearAppStorage } from "@/lib/reset-storage"
import { RotateCcw } from "lucide-react"

export function ResetButton() {
  const resetQuiz = useQuizStore(state => state.reset)
  const resetRecommendations = useRecommendationStore(state => state.reset)
  const clearUser = useUserStore(state => state.clearUser)
  
  const handleReset = () => {
    // Reset all stores
    resetQuiz()
    resetRecommendations()
    clearUser()
    
    // Clear localStorage
    clearAppStorage()
    
    // Reload page to ensure complete reset
    window.location.href = '/'
  }
  
  return (
    <Button 
      variant="outline" 
      size="sm"
      onClick={handleReset}
      className="fixed top-4 right-4 z-50 bg-white/90 hover:bg-white"
    >
      <RotateCcw className="w-4 h-4 mr-2" />
      New Session
    </Button>
  )
}