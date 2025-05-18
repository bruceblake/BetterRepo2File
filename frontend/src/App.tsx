import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WizardPage } from './pages/WizardPage';
import './App.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-900 text-gray-100">
        <WizardPage />
      </div>
    </QueryClientProvider>
  );
}

export default App;