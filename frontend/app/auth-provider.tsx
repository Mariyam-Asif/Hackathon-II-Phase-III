'use client';

// Better Auth v0.1.x doesn't require a provider wrapper in the layout
// The auth client is used directly with hooks
export function BetterAuthProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}