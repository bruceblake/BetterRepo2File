# Next.js + Supabase + Tailwind Best Practices

## Next.js Patterns
- Use Server Components by default, Client Components only when needed
- Implement proper error.tsx and loading.tsx for each route
- Use dynamic imports for heavy components
- Follow app directory structure conventions
- Implement metadata for SEO in layout.tsx or page.tsx

## Supabase Integration
- Use Supabase client-side SDK for browser operations
- Use Supabase server-side SDK for server components
- Implement Row Level Security (RLS) policies
- Handle auth state changes properly with useEffect
- Use prepared statements for complex queries

## Authentication Flow
- Store auth tokens securely in httpOnly cookies
- Implement proper session management
- Handle token refresh automatically
- Protect routes with middleware.ts
- Show appropriate UI states during auth loading

## Data Fetching
- Use React Server Components for initial data load
- Implement optimistic updates for better UX
- Use SWR or React Query for client-side caching
- Handle loading and error states consistently
- Implement proper pagination for large datasets

## Tailwind CSS Guidelines
- Use utility classes, avoid inline styles
- Create component classes for repeated patterns
- Follow mobile-first responsive design
- Use CSS variables for dynamic theming
- Leverage Tailwind's built-in animations

## Component Architecture
- Keep components small and focused
- Use composition over inheritance
- Implement proper prop validation with TypeScript
- Extract reusable logic into custom hooks
- Follow naming conventions (PascalCase for components)

## Performance Optimization
- Use Next.js Image component for images
- Implement lazy loading for below-fold content
- Minimize client-side JavaScript bundles
- Use static generation where possible
- Implement proper caching headers

## Error Handling
- Create custom error boundaries
- Log errors to a service (e.g., Sentry)
- Show user-friendly error messages
- Implement retry mechanisms for failed requests
- Handle offline scenarios gracefully

## Testing Strategy
- Write integration tests for API routes
- Test Supabase RLS policies
- Use React Testing Library for components
- Mock external services in tests
- Implement E2E tests for critical flows