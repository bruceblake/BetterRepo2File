import { useWizardStore } from '../lib/store';
import type { Stage } from '../types';

interface StageSelectorProps {
  onSelect: () => void;
}

export function StageSelector({ onSelect }: StageSelectorProps) {
  const { stage, updateStage } = useWizardStore();

  const stages: { id: Stage; title: string; description: string; icon: string }[] = [
    {
      id: 'A',
      title: 'Plan',
      description: 'Fresh start - Need context for AI Planner',
      icon: '💡'
    },
    {
      id: 'B',
      title: 'Code',
      description: 'Have a plan from AI Planner',
      icon: '💻'
    },
    {
      id: 'C', 
      title: 'Iterate',
      description: 'Have results from AI Coder',
      icon: '🔄'
    }
  ];

  const handleSelect = (stageId: Stage) => {
    updateStage(stageId);
    onSelect();
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {stages.map((s) => (
        <button
          key={s.id}
          onClick={() => handleSelect(s.id)}
          className={`p-6 rounded-lg border-2 transition-all ${
            stage === s.id
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-gray-700 hover:border-blue-500'
          }`}
        >
          <div className="text-4xl mb-2">{s.icon}</div>
          <h3 className="text-xl font-semibold mb-2">{s.title}</h3>
          <p className="text-gray-400">{s.description}</p>
        </button>
      ))}
    </div>
  );
}