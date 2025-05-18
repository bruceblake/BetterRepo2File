import { useState } from 'react';
import { useWizardStore } from '../lib/store';
import { RepoDropZone } from '../components/RepoDropZone';
import { VibeInput } from '../components/VibeInput';
import { StageSelector } from '../components/StageSelector';
import { WizardStepper } from '../components/WizardStepper';

export function WizardPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const { vibe, stage, repoFile } = useWizardStore();

  const steps = [
    'Upload Repository',
    'Describe Your Vibe',
    'Select Stage',
    'Additional Input',
    'Generate Context'
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-center mb-8">
        Repo2File Vibe Coder Assistant
      </h1>
      
      <WizardStepper steps={steps} currentStep={currentStep} />
      
      <div className="max-w-2xl mx-auto mt-8">
        {currentStep === 0 && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Upload Repository</h2>
            <RepoDropZone onFileSelected={() => setCurrentStep(1)} />
          </div>
        )}
        
        {currentStep === 1 && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">What's Your Vibe?</h2>
            <VibeInput />
            <button 
              className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg"
              onClick={() => setCurrentStep(2)}
            >
              Next
            </button>
          </div>
        )}
        
        {currentStep === 2 && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Pick Your Stage</h2>
            <StageSelector onSelect={() => setCurrentStep(3)} />
          </div>
        )}
        
        {currentStep === 3 && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Additional Input</h2>
            {/* Stage-specific inputs will go here */}
            <button 
              className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg"
              onClick={() => setCurrentStep(4)}
            >
              Next
            </button>
          </div>
        )}
        
        {currentStep === 4 && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Review & Generate</h2>
            <div className="bg-gray-800 p-4 rounded-lg mb-4">
              <p><strong>Vibe:</strong> {vibe}</p>
              <p><strong>Stage:</strong> {stage}</p>
              <p><strong>Repository:</strong> {repoFile?.name || 'None'}</p>
            </div>
            <button 
              className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold"
              onClick={() => {/* Start analysis */}}
            >
              Generate Context
            </button>
          </div>
        )}
      </div>
    </div>
  );
}