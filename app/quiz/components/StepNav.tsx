'use client'

import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight, Save } from 'lucide-react'

interface StepNavProps {
  currentStep: number
  totalSteps: number
  canProceed: boolean
  isSubmitting: boolean
  onBack: () => void
  onNext: () => void
  onSaveAndExit: () => void
}

export function StepNav({
  currentStep,
  totalSteps,
  canProceed,
  isSubmitting,
  onBack,
  onNext,
  onSaveAndExit
}: StepNavProps) {
  const isFirstStep = currentStep === 1
  const isLastStep = currentStep === totalSteps

  return (
    <div className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-6 border-t">
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          onClick={onSaveAndExit}
          className="flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          Save & Exit
        </Button>
      </div>

      <div className="flex items-center gap-3">
        <Button
          variant="outline"
          onClick={onBack}
          disabled={isFirstStep}
          className="flex items-center gap-2"
        >
          <ChevronLeft className="w-4 h-4" />
          Back
        </Button>

        <Button
          onClick={onNext}
          disabled={!canProceed || isSubmitting}
          className="flex items-center gap-2 min-w-[120px]"
        >
          {isSubmitting ? (
            "Submitting..."
          ) : isLastStep ? (
            "Complete Quiz"
          ) : (
            <>
              Next
              <ChevronRight className="w-4 h-4" />
            </>
          )}
        </Button>
      </div>
    </div>
  )
}