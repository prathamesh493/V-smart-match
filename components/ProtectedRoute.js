'use client';

// components/ProtectedRoute.js
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, userType }) => {
  const { currentUser, userProfile, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If not loading and no user is logged in, redirect to sign in
    if (!loading && !currentUser) {
      router.push('/signin');
      return;
    }

    // If user is logged in but profile doesn't match required userType
    if (!loading && currentUser && userProfile && userType && userProfile.userType !== userType) {
      // Redirect to appropriate dashboard based on user type
      if (userProfile.userType === 'candidate') {
        router.push('/candidate/dashboard');
      } else if (userProfile.userType === 'employer') {
        router.push('/employer/dashboard');
      } else {
        // Fallback
        router.push('/signin');
      }
    }
  }, [currentUser, loading, router, userProfile, userType]);

  // Show loading or nothing while checking auth
  if (loading || !currentUser) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // If no userType is specified or userType matches, render children
  if (!userType || (userProfile && userProfile.userType === userType)) {
    return <>{children}</>;
  }

  // Otherwise render nothing while redirecting
  return null;
};

export default ProtectedRoute;