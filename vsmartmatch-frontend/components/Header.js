'use client';

import { useMemo, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { signOut } from 'firebase/auth';
import { useAuth } from '@/lib/useAuth'; // Your custom hook for authentication
import { auth } from '@/firebase/config';
import { Button } from '@/components/ui/button';
import { LogOut, Loader2 } from 'lucide-react';

/**
 * AuthButton Component
 *
 * Handles the display logic for the authentication button based on user status.
 * This separation of concerns keeps the main Header component clean.
 */
const AuthButton = ({ user, loading, onSignOut }) => {
  if (loading) {
    return (
      <Button variant="ghost" className="text-white" disabled>
        <Loader2 className="h-4 w-4 animate-spin" />
      </Button>
    );
  }

  if (user) {
    return (
      <Button
        variant="ghost"
        className="text-white bg-transparent hover:bg-white/10 hover:text-white backdrop-blur-sm transition-all duration-200 flex items-center gap-2"
        onClick={onSignOut}
      >
        <LogOut className="h-4 w-4" />
        Sign Out
      </Button>
    );
  }

  return (
    <Link href="/signin">
      <Button
        variant="ghost"
        className="text-white bg-transparent hover:bg-white/10 hover:text-white backdrop-blur-sm transition-all duration-200"
      >
        Sign In
      </Button>
    </Link>
  );
};

/**
 * Main Header Component
 */
export default function Header() {
  const { user, loading } = useAuth(); // Assuming useAuth provides { user, loading }
  const router = useRouter();

  // Memoize the dashboard URL to prevent recalculation on every render.
  // It only recomputes when the `user` object changes.
  const logoHref = useMemo(() => {
    if (!user) {
      return '/'; // Default for logged-out users
    }
    // Redirects to the appropriate dashboard based on userType.
    return user.userType === 'candidate' ? '/candidate' : '/company';
  }, [user]);

  // Memoize the sign-out handler to ensure function stability across renders.
  const handleSignOut = useCallback(async () => {
  try {
    await signOut(auth);
    router.push('/'); // This correctly sends the user to the homepage.
  } catch (error) {
    console.error('Sign-out error:', error);
  }
}, [router]);

  return (
    <header className="bg-transparent py-6">
      <div className="container mx-auto px-4 flex justify-between items-center">
        <Link href={logoHref} className="text-2xl font-bold text-white hover:opacity-80 transition-opacity">
          vSmart Match
        </Link>
        <nav>
          <ul className="flex space-x-4 items-center">
            <li>
              <Link href="/about">
                <Button
                  variant="ghost"
                  className="text-white bg-transparent hover:bg-white/10 hover:text-white backdrop-blur-sm transition-all duration-200"
                >
                  About
                </Button>
              </Link>
            </li>
            <li>
              <Link href="/features">
                <Button
                  variant="ghost"
                  className="text-white bg-transparent hover:bg-white/10 hover:text-white backdrop-blur-sm transition-all duration-200"
                >
                  Features
                </Button>
              </Link>
            </li>
            <li>
              <AuthButton user={user} loading={loading} onSignOut={handleSignOut} />
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}