import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { FeedbackSchema } from '@/lib/validators'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate the request body
    const validatedData = FeedbackSchema.parse(body)
    
    // Ensure user exists
    const user = await prisma.user.findUnique({
      where: { id: validatedData.userId }
    })
    
    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }
    
    // Create the feedback record
    const feedback = await prisma.feedback.create({
      data: {
        userId: validatedData.userId,
        productId: validatedData.productId,
        action: validatedData.action,
        score: validatedData.score || (validatedData.action === 'like' ? 1 : 0),
      }
    })
    
    return NextResponse.json({
      success: true,
      feedback: {
        id: feedback.id,
        userId: feedback.userId,
        productId: feedback.productId,
        action: feedback.action,
        score: feedback.score,
        createdAt: feedback.createdAt
      }
    })
    
  } catch (error) {
    console.error('Error creating feedback:', error)
    
    if (error instanceof Error && error.name === 'ZodError') {
      return NextResponse.json(
        { error: 'Invalid feedback data', details: error },
        { status: 400 }
      )
    }
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get('userId')
    
    if (!userId) {
      return NextResponse.json(
        { error: 'userId parameter is required' },
        { status: 400 }
      )
    }
    
    const feedback = await prisma.feedback.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' }
    })
    
    return NextResponse.json({
      success: true,
      feedback
    })
    
  } catch (error) {
    console.error('Error fetching feedback:', error)
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}