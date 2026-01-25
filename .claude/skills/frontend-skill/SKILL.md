---
name: frontend-skill
description: Build pages, components, and layout styling for responsive and modern web applications using Next.js.
---

# Frontend Skill

## Instructions

1. **Page and Layout Structure**
   - Organize pages and layouts using Next.js App Router
   - Use server components by default, client components only when needed
   - Maintain consistent and reusable layout patterns

2. **Component Design**
   - Build reusable UI components (buttons, cards, forms)
   - Ensure responsiveness across devices and screen sizes
   - Implement proper accessibility (ARIA attributes, keyboard navigation)

3. **Styling**
   - Use Tailwind CSS or chosen CSS framework
   - Avoid inline styles; follow design system conventions
   - Apply consistent color, spacing, and typography

4. **Data Integration**
   - Connect components to backend APIs through centralized API client
   - Handle async data and loading states gracefully
   - Validate and display backend data correctly

## Best Practices
- Keep components single-purpose and modular
- Use descriptive names for pages and components
- Test responsiveness and accessibility regularly
- Follow mobile-first design approach
- Optimize rendering and minimize unnecessary re-renders

## Example Component
```tsx
export default function TaskCard({ title, completed }: { title: string; completed: boolean }) {
  return (
    <div className={`p-4 rounded shadow ${completed ? 'bg-green-100' : 'bg-white'}`}>
      <h3 className="text-lg font-bold">{title}</h3>
      <p>{completed ? "Completed" : "Pending"}</p>
    </div>
  );
}
