'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { QuizQuestion } from '@/lib/catalog'
import { QuizAnswer } from '@/lib/validators'
import { useState, useEffect } from 'react'

interface QuestionCardProps {
  question: QuizQuestion
  value?: QuizAnswer
  onChange: (answer: QuizAnswer) => void
}

export function QuestionCard({ question, value, onChange }: QuestionCardProps) {
  const [selectedValue, setSelectedValue] = useState<any>(value?.value)

  useEffect(() => {
    setSelectedValue(value?.value)
  }, [value])

  const handleSingleChoice = (newValue: string) => {
    setSelectedValue(newValue)
    onChange({
      qid: question.id,
      type: 'single',
      value: newValue
    })
  }

  const handleMultiChoice = (option: string, checked: boolean) => {
    const currentValues = Array.isArray(selectedValue) ? selectedValue : []
    let newValues: string[]
    
    if (checked) {
      newValues = [...currentValues, option]
    } else {
      newValues = currentValues.filter((v: string) => v !== option)
    }
    
    setSelectedValue(newValues)
    onChange({
      qid: question.id,
      type: 'multi',
      value: newValues
    })
  }

  const handleScaleChange = (newValue: number[]) => {
    const value = newValue[0]
    setSelectedValue(value)
    onChange({
      qid: question.id,
      type: 'scale',
      value: value
    })
  }

  const handleSizeChange = (sizeType: string, size: string) => {
    const currentSizes = typeof selectedValue === 'object' && selectedValue !== null ? selectedValue : {}
    const newSizes = { ...currentSizes, [sizeType]: size }
    
    setSelectedValue(newSizes)
    onChange({
      qid: question.id,
      type: 'size',
      value: newSizes
    })
  }

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {question.label}
          {question.required && (
            <Badge variant="destructive" className="text-xs">Required</Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {question.type === 'single' && question.options && (
          <RadioGroup 
            value={selectedValue || ''} 
            onValueChange={handleSingleChoice}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {question.options.map((option) => (
                <div key={option} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-gray-50 cursor-pointer">
                  <RadioGroupItem value={option} id={`${question.id}-${option}`} />
                  <Label 
                    htmlFor={`${question.id}-${option}`}
                    className="cursor-pointer font-medium flex-1"
                  >
                    {option}
                  </Label>
                </div>
              ))}
            </div>
          </RadioGroup>
        )}

        {question.type === 'multi' && question.options && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {question.options.map((option) => (
              <div key={option} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-gray-50">
                <Checkbox
                  id={`${question.id}-${option}`}
                  checked={Array.isArray(selectedValue) && selectedValue.includes(option)}
                  onCheckedChange={(checked) => handleMultiChoice(option, checked as boolean)}
                />
                <Label 
                  htmlFor={`${question.id}-${option}`}
                  className="cursor-pointer font-medium flex-1"
                >
                  {option}
                </Label>
              </div>
            ))}
          </div>
        )}

        {question.type === 'scale' && (
          <div className="space-y-4">
            <div className="px-2">
              <Slider
                value={[selectedValue || question.min || 0]}
                onValueChange={handleScaleChange}
                min={question.min || 0}
                max={question.max || 100}
                step={question.stepSize || 1}
                className="w-full"
              />
            </div>
            <div className="flex justify-between text-sm text-gray-500">
              <span>${question.min || 0}</span>
              <span className="font-semibold text-lg text-gray-900">
                ${selectedValue || question.min || 0}
              </span>
              <span>${question.max || 100}</span>
            </div>
          </div>
        )}

        {question.type === 'size' && question.sizeTypes && (
          <div className="space-y-4">
            {question.sizeTypes.map((sizeType) => (
              <div key={sizeType} className="space-y-2">
                <Label className="text-sm font-medium capitalize">{sizeType} Size</Label>
                <div className="flex flex-wrap gap-2">
                  {getSizeOptions(sizeType).map((size) => (
                    <Button
                      key={size}
                      variant={
                        selectedValue?.[sizeType] === size ? "default" : "outline"
                      }
                      size="sm"
                      onClick={() => handleSizeChange(sizeType, size)}
                      className="min-w-[60px]"
                    >
                      {size}
                    </Button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function getSizeOptions(sizeType: string): string[] {
  switch (sizeType) {
    case 'top':
      return ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL']
    case 'bottom':
      return ['24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '36']
    case 'shoe':
      return ['5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11']
    default:
      return []
  }
}