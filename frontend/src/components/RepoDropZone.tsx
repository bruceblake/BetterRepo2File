import { useCallback } from 'react';
import { useWizardStore } from '../lib/store';

interface RepoDropZoneProps {
  onFileSelected: () => void;
}

export function RepoDropZone({ onFileSelected }: RepoDropZoneProps) {
  const setRepoFile = useWizardStore((state) => state.setRepoFile);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.zip')) {
      setRepoFile(file);
      onFileSelected();
    }
  }, [setRepoFile, onFileSelected]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setRepoFile(file);
      onFileSelected();
    }
  };

  return (
    <div
      className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-blue-500 transition-colors"
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
    >
      <p className="mb-4">Drop a .zip file here or click to browse</p>
      <input
        type="file"
        accept=".zip"
        onChange={handleFileSelect}
        className="hidden"
        id="file-upload"
      />
      <label
        htmlFor="file-upload"
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded cursor-pointer"
      >
        Choose File
      </label>
    </div>
  );
}