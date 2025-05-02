'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { LogOut } from 'lucide-react';
import { useAuth } from '@/lib/useAuth'; // Adjust path
import { auth } from '@/firebase/config'; // Adjust path
import { signOut } from 'firebase/auth';
import { useRouter } from 'next/navigation';

export default function Header() {
  const { user } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      console.log('User signed out');
      router.push('/signin');
    } catch (error) {
      console.error('Sign-out error:', error);
    }
  };

  return (
    <header className="bg-transparent py-6">
      <div className="container mx-auto px-4 flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-white hover:opacity-80 transition-opacity">
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
              {user ? (
                <Button
                  variant="ghost"
                  className="text-white bg-transparent hover:bg-white/10 hover:text-white backdrop-blur-sm transition-all duration-200 flex items-center gap-2"
                  onClick={handleSignOut}
                >
                  <LogOut className="h-4 w-4" />
                  Sign Out
                </Button>
              ) : (
                <Link href="/signin">
                  <Button
                    variant="ghost"
                    className="text-white bg-transparent hover:bg-white/10 hover:text-white backdrop-blur-sm transition-all duration-200"
                  >
                    Sign In
                  </Button>
                </Link>
              )}
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}