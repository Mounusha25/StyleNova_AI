import { z } from 'zod'

// Quiz Answer Types
export type QuizAnswer =
  | { qid: string; type: "single"; value: string }
  | { qid: string; type: "multi"; value: string[] }
  | { qid: string; type: "scale"; value: number }
  | { qid: string; type: "size"; value: { top?: string; bottom?: string; shoe?: string } }

export type QuizPayload = {
  userId: string
  answers: QuizAnswer[]
  completedAt?: string
}

// Product Types
export interface Product {
  id: string
  brand: string
  title: string
  price: number
  tags: string[]
  fit: string
  colors: string[]
  gender: string
  sizes: string[]
  imageUrl: string
  category?: string
  pattern?: string
}

// Quiz Question Types
export interface QuizQuestion {
  id: string
  step: number
  type: 'single' | 'multi' | 'scale' | 'size'
  required: boolean
  label: string
  options?: string[]
  min?: number
  max?: number
  stepSize?: number
  sizeTypes?: string[]
  imageChoices?: boolean
}

// Zod Validation Schemas
export const QuizAnswerSchema = z.discriminatedUnion('type', [
  z.object({
    qid: z.string(),
    type: z.literal('single'),
    value: z.string()
  }),
  z.object({
    qid: z.string(),
    type: z.literal('multi'),
    value: z.array(z.string())
  }),
  z.object({
    qid: z.string(),
    type: z.literal('scale'),
    value: z.number()
  }),
  z.object({
    qid: z.string(),
    type: z.literal('size'),
    value: z.object({
      top: z.string().optional(),
      bottom: z.string().optional(),
      shoe: z.string().optional()
    })
  })
])

export const QuizPayloadSchema = z.object({
  userId: z.string(),
  answers: z.array(QuizAnswerSchema),
  completedAt: z.string().optional()
})

export const FeedbackSchema = z.object({
  userId: z.string(),
  productId: z.string(),
  action: z.enum(['like', 'pass']),
  score: z.number().optional()
})