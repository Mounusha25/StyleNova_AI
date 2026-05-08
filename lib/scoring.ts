import { QuizAnswer, Product } from './validators'
import { catalogData } from './catalog'

export interface ScoredProduct extends Product {
  score: number
  reason: string[]
}

export function generateRecommendations(answers: QuizAnswer[], limit = 30): ScoredProduct[] {
  const userProfile = buildUserProfile(answers)
  
  // Debug: Log current catalog info with timestamp
  const timestamp = new Date().toISOString()
  console.log(`🔍 Catalog Debug Info (${timestamp}):`)
  console.log(`   - Total products in catalog: ${catalogData.length}`)
  console.log(`   - First product: ${catalogData[0]?.title} by ${catalogData[0]?.brand}`)
  console.log(`   - First product ID: ${catalogData[0]?.id}`)
  console.log(`   - Sample product IDs: ${catalogData.slice(0, 5).map(p => p.id).join(', ')}`)
  console.log(`   - Sample brands: ${catalogData.slice(0, 5).map(p => p.brand).join(', ')}`)
  
  // Check if we're getting the new CSV data
  const hasNewData = catalogData.some(p => p.brand === "ALTAR'D STATE" || p.brand === "EDIKTED")
  console.log(`   - Using NEW catalog data: ${hasNewData ? '✅ YES' : '❌ NO (still old data)'}`)
  
  const scoredProducts = catalogData.map(product => {
    const score = calculateProductScore(product, userProfile)
    const reason = getScoreReasons(product, userProfile)
    
    return {
      ...product,
      score,
      reason
    }
  })

  // Sort by score descending and return top N
  const recommendations = scoredProducts
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    
  console.log(`✅ Generated ${recommendations.length} recommendations from ${catalogData.length} products`)
  console.log(`   - Top recommendation: ${recommendations[0]?.title} by ${recommendations[0]?.brand} (score: ${recommendations[0]?.score})`)
  
  return recommendations
}

interface UserProfile {
  gender?: string
  ageRange?: string
  sizes: {
    top?: string
    bottom?: string
    shoe?: string
  }
  budgetTop?: number
  budgetBottom?: number
  occasions: string[]
  styles: string[]
  likedColors: string[]
  dislikedColors: string[]
  jeanFit?: string
  trendAdventure?: number
  bodyType?: string
}

function buildUserProfile(answers: QuizAnswer[]): UserProfile {
  const profile: UserProfile = {
    sizes: {},
    occasions: [],
    styles: [],
    likedColors: [],
    dislikedColors: []
  }

  answers.forEach(answer => {
    switch (answer.qid) {
      case 'q1':
        if (answer.type === 'single') {
          profile.gender = answer.value.toLowerCase()
        }
        break
      case 'q2':
        if (answer.type === 'single') {
          profile.ageRange = answer.value
        }
        break
      case 'q3':
        if (answer.type === 'size') {
          profile.sizes = answer.value
        }
        break
      case 'q4':
        if (answer.type === 'scale') {
          profile.budgetTop = answer.value
        }
        break
      case 'q5':
        if (answer.type === 'scale') {
          profile.budgetBottom = answer.value
        }
        break
      case 'q6':
        if (answer.type === 'multi') {
          profile.occasions = answer.value
        }
        break
      case 'q7':
        if (answer.type === 'multi') {
          profile.styles = answer.value
        }
        break
      case 'q8':
        if (answer.type === 'multi') {
          profile.likedColors = answer.value.map(c => c.toLowerCase())
        }
        break
      case 'q9':
        if (answer.type === 'multi') {
          profile.dislikedColors = answer.value.map(c => c.toLowerCase())
        }
        break
      case 'q10':
        if (answer.type === 'single') {
          profile.jeanFit = answer.value.toLowerCase()
        }
        break
      case 'q11':
        if (answer.type === 'scale') {
          profile.trendAdventure = answer.value
        }
        break
      case 'q12':
        if (answer.type === 'single') {
          profile.bodyType = answer.value.toLowerCase()
        }
        break
    }
  })

  return profile
}

function calculateProductScore(product: Product, profile: UserProfile): number {
  let score = 0
  const maxScore = 100

  // Gender match (20 points)
  if (profile.gender && (product.gender === profile.gender || product.gender === 'unisex')) {
    score += 20
  }

  // Budget compatibility (15 points)
  const budget = getRelevantBudget(product, profile)
  if (budget && product.price <= budget) {
    score += 15
  } else if (budget && product.price > budget * 1.2) {
    score -= 10 // penalty for being too expensive
  }

  // Style match (15 points)
  const styleMatches = product.tags.filter(tag => 
    profile.styles.some(style => 
      style.toLowerCase().includes(tag.toLowerCase()) ||
      tag.toLowerCase().includes(style.toLowerCase())
    )
  ).length
  score += Math.min(styleMatches * 5, 15)

  // Occasion match (15 points)
  const occasionMatches = product.tags.filter(tag =>
    profile.occasions.some(occasion =>
      mapOccasionToTags(occasion).includes(tag.toLowerCase())
    )
  ).length
  score += Math.min(occasionMatches * 5, 15)

  // Color preference (10 points)
  const colorMatches = product.colors.filter(color =>
    profile.likedColors.some(liked => 
      color.toLowerCase().includes(liked) ||
      liked.includes(color.toLowerCase())
    )
  ).length
  score += Math.min(colorMatches * 3, 10)

  // Color dislikes (penalty)
  const colorDislikes = product.colors.filter(color =>
    profile.dislikedColors.some(disliked =>
      color.toLowerCase().includes(disliked) ||
      disliked.includes(color.toLowerCase())
    )
  ).length
  score -= colorDislikes * 5

  // Trend adventure factor (10 points)
  if (profile.trendAdventure !== undefined) {
    const trendiness = getTrendinessScore(product)
    const adventureAlignment = 1 - Math.abs(trendiness - (profile.trendAdventure / 5)) / 1
    score += adventureAlignment * 10
  }

  // Size availability (10 points)
  if (hasMatchingSizes(product, profile)) {
    score += 10
  }

  // Jean fit specificity (5 points bonus for jeans)
  if (product.tags.includes('jeans') && profile.jeanFit) {
    if (product.fit.toLowerCase().includes(profile.jeanFit) ||
        product.tags.some(tag => tag.includes(profile.jeanFit!))) {
      score += 5
    }
  }

  return Math.max(0, Math.min(score, maxScore))
}

function getRelevantBudget(product: Product, profile: UserProfile): number | undefined {
  if (product.tags.includes('top') || product.tags.includes('shirt') || 
      product.tags.includes('blouse') || product.tags.includes('sweater') ||
      product.tags.includes('blazer')) {
    return profile.budgetTop
  }
  if (product.tags.includes('bottom') || product.tags.includes('jeans') ||
      product.tags.includes('pants') || product.tags.includes('skirt') ||
      product.tags.includes('trousers')) {
    return profile.budgetBottom
  }
  // Default to top budget for dresses and other items
  return profile.budgetTop
}

function mapOccasionToTags(occasion: string): string[] {
  const mapping: Record<string, string[]> = {
    'Work/Professional': ['work', 'professional', 'blazer', 'formal'],
    'Casual/Weekend': ['casual', 'comfort', 'relaxed'],
    'Date Night': ['date', 'party', 'elegant', 'dress'],
    'Social Events': ['party', 'social', 'dressy'],
    'Travel': ['comfortable', 'versatile', 'wrinkle-free'],
    'Exercise/Athletic': ['sport', 'athletic', 'gym', 'active']
  }
  return mapping[occasion] || []
}

function getTrendinessScore(product: Product): number {
  const trendyTags = ['trendy', 'statement', 'bold', 'fashion-forward', 'puffy-sleeves']
  const classicTags = ['classic', 'timeless', 'basic', 'essential']
  
  const trendyCount = product.tags.filter(tag => trendyTags.includes(tag)).length
  const classicCount = product.tags.filter(tag => classicTags.includes(tag)).length
  
  if (trendyCount > classicCount) return 0.8 // trendy
  if (classicCount > trendyCount) return 0.2 // classic
  return 0.5 // neutral
}

function hasMatchingSizes(product: Product, profile: UserProfile): boolean {
  // This is a simplified check - in reality you'd want more sophisticated size matching
  return product.sizes.length > 0 // For now, just check if sizes are available
}

function getScoreReasons(product: Product, profile: UserProfile): string[] {
  const reasons: string[] = []
  
  if (profile.gender && (product.gender === profile.gender || product.gender === 'unisex')) {
    reasons.push('Matches your gender preference')
  }
  
  const budget = getRelevantBudget(product, profile)
  if (budget && product.price <= budget) {
    reasons.push('Within your budget')
  }
  
  const styleMatches = product.tags.filter(tag => 
    profile.styles.some(style => 
      style.toLowerCase().includes(tag.toLowerCase()) ||
      tag.toLowerCase().includes(style.toLowerCase())
    )
  )
  if (styleMatches.length > 0) {
    reasons.push(`Matches your ${styleMatches.join(', ')} style`)
  }
  
  const colorMatches = product.colors.filter(color =>
    profile.likedColors.some(liked => 
      color.toLowerCase().includes(liked) ||
      liked.includes(color.toLowerCase())
    )
  )
  if (colorMatches.length > 0) {
    reasons.push(`Available in your favorite colors: ${colorMatches.join(', ')}`)
  }
  
  return reasons
}