import { create } from 'zustand'
import { QuizAnswer, Product } from './validators'

interface QuizState {
  currentStep: number
  answers: QuizAnswer[]
  isCompleted: boolean
  quizId?: string
  setCurrentStep: (step: number) => void
  setAnswer: (answer: QuizAnswer) => void
  setAnswers: (answers: QuizAnswer[]) => void
  markCompleted: (quizId: string) => void
  reset: () => void
}

interface RecommendationState {
  recommendations: Product[]
  currentIndex: number
  likedProducts: Product[]
  passedProducts: Product[]
  isLoading: boolean
  error: string | null
  setRecommendations: (products: Product[]) => void
  addRecommendations: (products: Product[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  swipeProduct: (direction: 'like' | 'pass') => void
  undoLastSwipe: () => void
  reset: () => void
}

interface UserState {
  userId?: string
  email?: string
  setUser: (userId: string, email?: string) => void
  clearUser: () => void
}

export const useQuizStore = create<QuizState>()((set, get) => ({
  currentStep: 1,
  answers: [],
  isCompleted: false,
  quizId: undefined,
  
  setCurrentStep: (step) => set({ currentStep: step }),
  
  setAnswer: (answer) => {
    const answers = get().answers
    const existingIndex = answers.findIndex(a => a.qid === answer.qid)
    
    if (existingIndex >= 0) {
      // Update existing answer
      const newAnswers = [...answers]
      newAnswers[existingIndex] = answer
      set({ answers: newAnswers })
    } else {
      // Add new answer
      set({ answers: [...answers, answer] })
    }
  },
  
  setAnswers: (answers) => set({ answers }),
  
  markCompleted: (quizId) => set({ 
    isCompleted: true, 
    quizId 
  }),
  
  reset: () => set({
    currentStep: 1,
    answers: [],
    isCompleted: false,
    quizId: undefined
  })
}))

export const useRecommendationStore = create<RecommendationState>()((set, get) => ({
  recommendations: [],
  currentIndex: 0,
  likedProducts: [],
  passedProducts: [],
  isLoading: false,
  error: null,
  
  setRecommendations: (products) => set({ 
    recommendations: products,
    currentIndex: 0,
    error: null
  }),
  
  addRecommendations: (products) => {
    const { recommendations } = get()
    set({ 
      recommendations: [...recommendations, ...products],
      error: null
    })
  },
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (error) => set({ error }),
  
  swipeProduct: (direction) => {
    const { recommendations, currentIndex, likedProducts, passedProducts } = get()
    const currentProduct = recommendations[currentIndex]
    
    if (!currentProduct) return
    
    if (direction === 'like') {
      set({
        likedProducts: [...likedProducts, currentProduct],
        currentIndex: currentIndex + 1
      })
    } else {
      set({
        passedProducts: [...passedProducts, currentProduct],
        currentIndex: currentIndex + 1
      })
    }
  },
  
  undoLastSwipe: () => {
    const { currentIndex, likedProducts, passedProducts } = get()
    
    if (currentIndex > 0) {
      // Remove the last product from either liked or passed
      const newLiked = [...likedProducts]
      const newPassed = [...passedProducts]
      
      if (newLiked.length > 0 && newLiked[newLiked.length - 1]) {
        newLiked.pop()
      } else if (newPassed.length > 0 && newPassed[newPassed.length - 1]) {
        newPassed.pop()
      }
      
      set({
        currentIndex: currentIndex - 1,
        likedProducts: newLiked,
        passedProducts: newPassed
      })
    }
  },
  
  reset: () => set({
    recommendations: [],
    currentIndex: 0,
    likedProducts: [],
    passedProducts: [],
    isLoading: false,
    error: null
  })
}))

export const useUserStore = create<UserState>()((set) => ({
  userId: undefined,
  email: undefined,
  
  setUser: (userId, email) => set({ userId, email }),
  clearUser: () => set({ userId: undefined, email: undefined })
}))