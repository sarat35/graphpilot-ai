import { Progress } from "@/components/ui/progress"
import { WIZARD_STEPS } from "@/components/search/wizard-config"

export function StepProgress({ currentIndex }: { currentIndex: number }) {
  const total = WIZARD_STEPS.length
  const percent = ((currentIndex + 1) / total) * 100

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between text-xs font-medium text-muted-foreground">
        <span>
          Step {currentIndex + 1} of {total}
        </span>
        <span>{WIZARD_STEPS[currentIndex].title}</span>
      </div>
      <Progress value={percent} aria-label={`Step ${currentIndex + 1} of ${total}`} />
    </div>
  )
}
