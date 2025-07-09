'use client';

import { useState, useEffect } from 'react';
import { auth } from '../firebase/config'; // Adjust path to your firebase/config.js
import { onAuthStateChanged } from 'firebase/auth';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setLoading(false);
      if (currentUser) {
        // Log user details
        console.log('Current user details:', {
          uid: currentUser.uid,
          email: currentUser.email,
          emailVerified: currentUser.emailVerified,
          displayName: currentUser.displayName,
          photoURL: currentUser.photoURL,
          creationTime: currentUser.metadata.creationTime,
          lastSignInTime: currentUser.metadata.lastSignInTime,
          providerData: currentUser.providerData,
        });
        console.log('User ID Token:', currentUser.getIdToken());
        setUser(currentUser);
      } else {
        console.log('No user signed in');
        setUser(null);
      }
    }, (error) => {
      console.error('Auth state error:', error);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  return { user, loading };
};