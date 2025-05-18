interface WizardStepperProps {
  steps: string[];
  currentStep: number;
}

export function WizardStepper({ steps, currentStep }: WizardStepperProps) {
  return (
    <div className="flex justify-center mb-8">
      <div className="flex items-center space-x-4">
        {steps.map((_, index) => (
          <div key={index} className="flex items-center">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                index <= currentStep
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-400'
              }`}
            >
              {index + 1}
            </div>
            {index < steps.length - 1 && (
              <div
                className={`w-16 h-1 ml-4 ${
                  index < currentStep ? 'bg-blue-600' : 'bg-gray-700'
                }`}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}