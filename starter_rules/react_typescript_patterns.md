# React TypeScript Patterns & Best Practices

## TypeScript Configuration
- Use strict mode in tsconfig.json
- Enable all strict type-checking options
- Configure path aliases for cleaner imports
- Use .tsx extension for React components
- Define proper module resolution strategy

## Component Typing
```typescript
// Function components with props
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ label, onClick, variant = 'primary', disabled = false }) => {
  // Component implementation
};
```

## State Management Types
```typescript
// useState with proper typing
const [user, setUser] = useState<User | null>(null);

// useReducer with discriminated unions
type Action = 
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_DATA'; payload: User[] }
  | { type: 'SET_ERROR'; payload: string };
```

## Custom Hook Patterns
```typescript
// Typed custom hooks
function useApi<T>(url: string): {
  data: T | null;
  error: Error | null;
  loading: boolean;
} {
  // Implementation
}
```

## Event Handler Types
```typescript
// Properly typed event handlers
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value);
};

const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  // Handle form submission
};
```

## Props with Children
```typescript
// Components accepting children
interface LayoutProps {
  children: React.ReactNode;
  className?: string;
}
```

## Generic Components
```typescript
// Reusable generic components
interface SelectProps<T> {
  options: T[];
  value: T;
  onChange: (value: T) => void;
  getLabel: (option: T) => string;
}

function Select<T>({ options, value, onChange, getLabel }: SelectProps<T>) {
  // Implementation
}
```

## Context API Types
```typescript
// Typed context
interface AuthContextType {
  user: User | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);
```

## Ref Types
```typescript
// Properly typed refs
const inputRef = useRef<HTMLInputElement>(null);
const componentRef = useRef<MyComponentHandle>(null);
```

## Async Operations
```typescript
// Type async operations
interface ApiResponse<T> {
  data: T;
  error?: string;
  status: number;
}

async function fetchData<T>(url: string): Promise<ApiResponse<T>> {
  // Implementation
}
```

## Error Boundaries
- Implement typed error boundaries
- Create fallback UI components
- Log errors to monitoring service
- Provide error recovery mechanisms

## Performance Types
```typescript
// Memoization with types
const MemoizedComponent = React.memo<ComponentProps>(Component);

const memoizedValue = useMemo<ExpensiveCalculationType>(
  () => expensiveCalculation(input),
  [input]
);
```

## Form Handling
- Use proper form libraries (react-hook-form, formik)
- Define form schemas with zod or yup
- Type form values and errors
- Implement proper validation