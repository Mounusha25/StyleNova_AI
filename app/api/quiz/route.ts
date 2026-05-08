import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { QuizPayloadSchema } from '@/lib/validators'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate the request body
    const validatedData = QuizPayloadSchema.parse(body)
    
    // Create or find the user
    let user = await prisma.user.findUnique({
      where: { id: validatedData.userId }
    })
    
    if (!user) {
      user = await prisma.user.create({
        data: {
          id: validatedData.userId,
          email: `${validatedData.userId}@temp.com` // Temporary email
        }
      })
    }
    
    // Create the quiz
    const quiz = await prisma.quiz.create({
      data: {
        userId: user.id,
        answers: JSON.stringify(validatedData.answers),
        completed: true,
      }
    })
    
    // Get the last answer for the special requirement
    const lastAnswer = validatedData.answers[validatedData.answers.length - 1]
    
    return NextResponse.json({
      success: true,
      quizId: quiz.id,
      answers: validatedData.answers,
      lastAnswer: lastAnswer
    })
    
  } catch (error) {
    console.error('Error creating quiz:', error)
    
    if (error instanceof Error && error.name === 'ZodError') {
      return NextResponse.json(
        { error: 'Invalid quiz data', details: error },
        { status: 400 }
      )
    }
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json(
    { message: 'Use POST to submit quiz or GET /api/quiz/[id] to fetch a specific quiz' },
    { status: 405 }
  )
}