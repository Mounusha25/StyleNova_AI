import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const quizId = params.id
    
    const quiz = await prisma.quiz.findUnique({
      where: { id: quizId },
      include: {
        user: {
          select: {
            id: true,
            email: true
          }
        }
      }
    })
    
    if (!quiz) {
      return NextResponse.json(
        { error: 'Quiz not found' },
        { status: 404 }
      )
    }
    
    // Parse the answers JSON
    const answers = JSON.parse(quiz.answers)
    const lastAnswer = answers[answers.length - 1]
    
    return NextResponse.json({
      success: true,
      quiz: {
        id: quiz.id,
        userId: quiz.userId,
        answers: answers,
        completed: quiz.completed,
        createdAt: quiz.createdAt,
        lastAnswer: lastAnswer
      },
      user: quiz.user
    })
    
  } catch (error) {
    console.error('Error fetching quiz:', error)
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}