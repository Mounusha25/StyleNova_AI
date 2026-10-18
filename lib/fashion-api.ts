/**
 * Fashion API utilities for connecting to the adaptive recommendation backend
 * Backend runs on http://localhost:8004
 */

import type { Product, QuizAnswer } from './validators'

// Types matching the backend API
export interface QuizFeatures {
  size?: string
  preferred_categories: string[]
  preferred_colors: string[]
  max_price?: number
  preferred_brands: string[]
  preferred_styles: string[]
}

export interface AdaptiveSearchRequest {
  user_id: string
  quiz_features?: QuizFeatures
  image_url?: string
  brand_name?: string
  category?: string
  adaptation_strength?: number // 0-1, how much to adapt based on user feedback
  k?: number // number of recommendations
  exclude_items?: string[] // items to exclude from recommendations
}

export interface RecommendationResponse {
  rank: number
  id: string
  brand: string
  title: string
  price: number
  score: number
  base_score?: number
  image_url: string
  recommendation_type: string
  user_feedback?: unknown
  is_personalized: boolean
}

export interface FeedbackRequest {
  user_id: string
  item_id: string
  feedback: 'like' | 'dislike'
}

export interface UserStats {
  user_id: string
  total_feedback: number
  likes: number
  dislikes: number
  personalization_score: number
  last_feedback?: string
  feedback_history: unknown[]
}

export interface OutfitProduct {
  id: string
  title: string
  brand: string
  category: string
  price: number
  image_url: string
}

export interface OutfitItem {
  slot: string
  product: OutfitProduct
  compatibility_score: number
  signals: Record<string, number>
  reasons: string[]
}

export interface OutfitResponse {
  anchor: OutfitProduct
  items: OutfitItem[]
  outfit_score: number
  total_price: number
  complete: boolean
  latency_ms: number
}

// API Configuration
const FASHION_API_BASE_URL = process.env.NEXT_PUBLIC_FASHION_API_URL ?? 'http://localhost:8004'

class FashionAPIError extends Error {
  constructor(message: string, public status?: number, public response?: unknown) {
    super(message)
    this.name = 'FashionAPIError'
  }
}

/**
 * Generic API request handler
 */
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${FASHION_API_BASE_URL}${endpoint}`
  const headers = new Headers(options.headers)
  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const config: RequestInit = {
    ...options,
    headers,
  }

  try {
    const response = await fetch(url, config)
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`
      let errorData = null
      
      try {
        errorData = await response.json()
        errorMessage = errorData.detail || errorMessage
      } catch {
        // Response body might not be JSON
      }
      
      throw new FashionAPIError(errorMessage, response.status, errorData)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof FashionAPIError) {
      throw error
    }
    
    // Network or other errors
    throw new FashionAPIError(
      `API request failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      undefined,
      error
    )
  }
}

/**
 * Check if the fashion API server is running
 */
export async function checkFashionAPIHealth(): Promise<boolean> {
  try {
    await apiRequest('/health')
    return true
  } catch {
    return false
  }
}

/**
 * Get priority-based adaptive recommendations
 * Supports multiple input types with priority weighting:
 * 1. Image URL (Highest Priority - 60%)
 * 2. Brand Name (Medium Priority - 30%) 
 * 3. Category (Lower Priority - 10%)
 * 4. Quiz Features (Fallback)
 */
export async function getPriorityAdaptiveRecommendations(
  userId: string,
  options: {
    imageUrl?: string      // Highest priority
    brandName?: string     // Medium priority
    category?: string      // Lower priority
    quizFeatures?: QuizFeatures  // Fallback
    adaptationStrength?: number
    count?: number
    excludeItems?: string[]
  }
): Promise<RecommendationResponse[]> {
  const request: AdaptiveSearchRequest = {
    user_id: userId,
    image_url: options.imageUrl,
    brand_name: options.brandName,
    category: options.category,
    quiz_features: options.quizFeatures,
    adaptation_strength: options.adaptationStrength ?? 0.6,
    k: options.count ?? 10,
    exclude_items: options.excludeItems ?? [],
  }

  console.log('🎯 Priority Adaptive Request:', {
    userId,
    priorities: {
      image: !!options.imageUrl ? '🖼️ HIGHEST (60%)' : '❌',
      brand: !!options.brandName ? '🏷️ MEDIUM (30%)' : '❌', 
      category: !!options.category ? '📂 LOWER (10%)' : '❌',
      quiz: !!options.quizFeatures ? '📋 FALLBACK' : '❌'
    },
    adaptationStrength: request.adaptation_strength,
    excludeCount: options.excludeItems?.length ?? 0
  })

  return apiRequest<RecommendationResponse[]>('/recommend/adaptive', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

/**
 * Get adaptive recommendations based on quiz answers
 */
export async function getRecommendationsFromQuiz(
  userId: string,
  quizFeatures: QuizFeatures,
  adaptationStrength: number = 0.5,
  count: number = 10
): Promise<RecommendationResponse[]> {
  const request: AdaptiveSearchRequest = {
    user_id: userId,
    quiz_features: quizFeatures,
    adaptation_strength: adaptationStrength,
    k: count,
  }

  return apiRequest<RecommendationResponse[]>('/recommend/adaptive', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

/**
 * Get adaptive recommendations based on image URL
 */
export async function getRecommendationsFromImage(
  userId: string,
  imageUrl: string,
  adaptationStrength: number = 0.5,
  count: number = 10
): Promise<RecommendationResponse[]> {
  const request: AdaptiveSearchRequest = {
    user_id: userId,
    image_url: imageUrl,
    adaptation_strength: adaptationStrength,
    k: count,
  }

  return apiRequest<RecommendationResponse[]>('/recommend/adaptive', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

/**
 * Upload a local fashion photo and retrieve CLIP-ranked, personalized products.
 */
export async function getRecommendationsFromUploadedImage(
  userId: string,
  image: File,
  adaptationStrength: number = 0.5,
  count: number = 10
): Promise<RecommendationResponse[]> {
  const form = new FormData()
  form.append('image', image)
  form.append('user_id', userId)
  form.append('adaptation_strength', String(adaptationStrength))
  form.append('k', String(count))

  return apiRequest<RecommendationResponse[]>('/recommend/image-upload', {
    method: 'POST',
    body: form,
  })
}

/** Build a compatibility-ranked outfit around a catalog product. */
export async function getOutfit(itemId: string, maxTotal?: number): Promise<OutfitResponse> {
  const query = maxTotal ? `?max_total=${encodeURIComponent(maxTotal)}` : ''
  return apiRequest<OutfitResponse>(`/outfits/${encodeURIComponent(itemId)}${query}`)
}

/**
 * Get adaptive recommendations based on brand search
 */
export async function getRecommendationsFromBrand(
  userId: string,
  brandName: string,
  category?: string,
  adaptationStrength: number = 0.5,
  count: number = 10
): Promise<RecommendationResponse[]> {
  const request: AdaptiveSearchRequest = {
    user_id: userId,
    brand_name: brandName,
    category: category,
    adaptation_strength: adaptationStrength,
    k: count,
  }

  return apiRequest<RecommendationResponse[]>('/recommend/adaptive', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

/**
 * Submit user feedback (like/dislike) for a product
 */
export async function submitFeedback(
  userId: string,
  itemId: string,
  feedback: 'like' | 'dislike'
): Promise<{ status: string; message: string; user_stats: UserStats }> {
  const request: FeedbackRequest = {
    user_id: userId,
    item_id: itemId,
    feedback: feedback,
  }

  return apiRequest('/feedback', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

/**
 * Get user's learning statistics and preference profile
 */
export async function getUserStats(userId: string): Promise<UserStats> {
  return apiRequest<UserStats>(`/users/${userId}/stats`)
}

/**
 * Get user's feedback history
 */
export async function getUserFeedbackHistory(
  userId: string,
  limit: number = 50
): Promise<{
  user_id: string
  feedback_history: Array<{
    item_id: string
    feedback: string
    timestamp: string
    item_title: string
    item_brand: string
  }>
  total_feedback: number
}> {
  return apiRequest(`/users/${userId}/feedback?limit=${limit}`)
}

/**
 * Reset user's profile (for testing/debugging)
 */
export async function resetUserProfile(userId: string): Promise<{ status: string; message: string }> {
  return apiRequest(`/users/${userId}/reset`, {
    method: 'POST',
  })
}

/**
 * Helper function to convert quiz answers to QuizFeatures format
 */
export function convertQuizAnswersToFeatures(answers: QuizAnswer[]): QuizFeatures {
  const features: QuizFeatures = {
    preferred_categories: [],
    preferred_colors: [],
    preferred_brands: [],
    preferred_styles: [],
    size: 'M',
    max_price: 100,
  }

  // Process quiz answers and map them to backend format
  answers.forEach((answer) => {
    switch (answer.qid) {
      case 'categories':
        if (Array.isArray(answer.value)) {
          features.preferred_categories = answer.value
        }
        break
      case 'colors':
        if (Array.isArray(answer.value)) {
          features.preferred_colors = answer.value
        }
        break
      case 'brands':
        if (Array.isArray(answer.value)) {
          features.preferred_brands = answer.value
        }
        break
      case 'styles':
        if (Array.isArray(answer.value)) {
          features.preferred_styles = answer.value
        }
        break
      case 'size':
        if (typeof answer.value === 'string') {
          features.size = answer.value
        }
        break
      case 'budget':
        if (typeof answer.value === 'number') {
          features.max_price = answer.value
        }
        break
    }
  })

  return features
}

/**
 * Fetch adaptive recommendations for a user with higher adaptation strength 
 * to show real-time learning based on accumulated feedback
 */
export async function getAdaptiveRecommendations(
  userId: string,
  excludeItemIds: string[] = [], // Items to exclude (already seen/disliked)
  adaptationStrength: number = 0.8,
  count: number = 10
): Promise<RecommendationResponse[]> {
  
  // Use priority system with generic fashion query
  // This leverages the accumulated user feedback for personalization
  return getPriorityAdaptiveRecommendations(userId, {
    brandName: "fashion", // Generic brand search to let algorithm decide
    adaptationStrength: adaptationStrength, // Higher adaptation strength for real-time learning
    count: count,
    excludeItems: excludeItemIds,
  })
}

/**
 * Helper function to convert backend recommendation to frontend Product format
 */
export interface FrontendRecommendation extends Product {
  score: number
  baseScore?: number
  isPersonalized: boolean
  recommendationType: string
  userFeedback?: unknown
  rank: number
}

export function convertRecommendationToProduct(rec: RecommendationResponse): FrontendRecommendation {
  return {
    id: rec.id,
    title: rec.title,
    brand: rec.brand,
    price: rec.price,
    imageUrl: rec.image_url, // Note: frontend expects imageUrl, backend provides image_url
    tags: [], // Backend doesn't provide tags in recommendations
    fit: 'regular', // Default fit
    colors: [], // Backend doesn't provide colors array in recommendations
    gender: 'unisex', // Default gender
    sizes: [], // Backend doesn't provide sizes array in recommendations
    score: rec.score,
    baseScore: rec.base_score,
    isPersonalized: rec.is_personalized,
    recommendationType: rec.recommendation_type,
    userFeedback: rec.user_feedback,
    rank: rec.rank,
  }
}

/**
 * Fetch recommendations from backend based on quiz answers and update the store
 */
export async function fetchRecommendationsForUser(
  userId: string,
  quizAnswers: QuizAnswer[],
  adaptationStrength: number = 0.6,
  count: number = 20
): Promise<FrontendRecommendation[]> {
  try {
    // Convert quiz answers to backend format
    const quizFeatures = convertQuizAnswersToFeatures(quizAnswers)
    
    console.log('🎯 Fetching recommendations from backend:', {
      userId,
      quizFeatures,
      adaptationStrength,
      count
    })
    
    // Get recommendations from the adaptive backend
    const backendRecommendations = await getRecommendationsFromQuiz(
      userId,
      quizFeatures,
      adaptationStrength,
      count
    )
    
    console.log('✅ Received recommendations from backend:', backendRecommendations.length)
    
    // Convert to frontend format
    const frontendProducts = backendRecommendations.map(convertRecommendationToProduct)
    
    return frontendProducts
    
  } catch (error) {
    console.error('❌ Failed to fetch recommendations from backend:', error)
    
    if (error instanceof FashionAPIError) {
      if (error.status === 503) {
        throw new Error('Fashion recommendation service is not available. Please make sure the backend server is running on http://localhost:8004')
      }
    }
    
    throw error
  }
}

export { FashionAPIError }
