# AI Coding Guardrails

## Scope Management
- Only modify code directly related to the specified task
- Do not refactor unrelated code unless explicitly requested
- Preserve existing comments and docstrings unless updating them is part of the task

## Code Quality
- Follow existing code style and conventions
- Use meaningful variable and function names
- Add appropriate error handling for edge cases
- Include type hints/annotations where the codebase uses them

## Security Best Practices
- Never hardcode credentials, API keys, or secrets
- Validate all user inputs
- Use parameterized queries to prevent SQL injection
- Implement proper authentication and authorization checks
- Follow OWASP security guidelines

## Performance Considerations
- Optimize database queries to avoid N+1 problems
- Implement appropriate caching strategies
- Use async/await for I/O-bound operations where applicable
- Consider memory usage for large data processing

## Testing Requirements
- Write unit tests for new functions/methods
- Update existing tests when modifying functionality
- Ensure all tests pass before considering the task complete
- Include edge cases in test coverage

## Documentation
- Document complex algorithms or business logic
- Update README if adding new features or dependencies
- Include inline comments for non-obvious code sections
- Document API changes if applicable

## Version Control
- Make small, focused commits
- Write clear, descriptive commit messages
- Reference issue numbers in commits when applicable
- Don't commit debugging code or console.log statements