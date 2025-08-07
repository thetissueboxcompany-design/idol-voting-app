// ~/idol_voting/frontend/src/app/page.tsx

import LoginForm from '@/components/auth/LoginForm';

export default function HomePage() {
  return (
    <main>
      {/* HIGHLIGHT: The main page now simply renders the login form. */}
      <LoginForm />
    </main>
  );
}
