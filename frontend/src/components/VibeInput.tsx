import { useWizardStore } from '../lib/store';

export function VibeInput() {
  const { vibe, updateVibe } = useWizardStore();

  return (
    <div>
      <textarea
        value={vibe}
        onChange={(e) => updateVibe(e.target.value)}
        className="w-full h-32 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
        placeholder="Describe what you want to build, your style, or any preferences..."
      />
      <p className="text-sm text-gray-400 mt-2">
        {vibe.length} characters
      </p>
    </div>
  );
}