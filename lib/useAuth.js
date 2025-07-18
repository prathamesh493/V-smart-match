'use client';

import { useState, useEffect, createContext, useContext, useMemo } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import { doc, getDoc } from 'firebase/firestore';
import { auth, db } from '@/firebase/config';

// The context now provides a richer user object and a loading state.
const AuthContext = createContext({
  
  user: null, // This will be the combined auth and Firestore user data.

  firebaseUser: null, // The actual Firebase Auth user object
  loading: true,
});

// The provider component is the heart of our authentication logic.
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [firebaseUser, setFirebaseUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (authUser) => {
      if (authUser) {
        // Store the Firebase Auth user object
        setFirebaseUser(authUser);
        
        // Fetch custom data from Firestore
        const userDocRef = doc(db, 'users', authUser.uid);
        const userDoc = await getDoc(userDocRef);

        if (userDoc.exists()) {
          // Combine Firebase auth data with Firestore data
          const userData = {
            uid: authUser.uid,
            email: authUser.email,
            displayName: authUser.displayName,
            getIdToken: () => authUser.getIdToken(), // Preserve the getIdToken method
            ...userDoc.data(),
          };
          setUser(userData);
        } else {
          // Edge case: Auth user exists but no Firestore doc.
          // This can happen if signup is interrupted. Treat as logged out.
          setUser(null);
        }
      } else {
        // User is signed out.
        setUser(null);
        setFirebaseUser(null);
      }
      // Authentication check is complete.
      setLoading(false);
    });

    // Cleanup subscription on unmount to prevent memory leaks.
    return () => unsubscribe();
  }, []);

  // Memoize the context value to prevent unnecessary re-renders of consuming components.
  // This is a critical performance optimization.
  const value = useMemo(() => ({
    user,
    firebaseUser,
    loading,
  }), [user, firebaseUser, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// The custom hook that components will use to access the auth state.
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};