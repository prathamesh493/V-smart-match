'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  signInWithEmailAndPassword,
  signInWithPopup,
  onAuthStateChanged,
  signOut,
} from 'firebase/auth';
import { doc, getDoc, setDoc } from 'firebase/firestore';
import { auth, db, googleProvider } from '../../firebase/config';
import Link from 'next/link';

// A simple Google Icon component - remains unchanged
const GoogleIcon = () => (
    <svg className="w-5 h-5" viewBox="0 0 48 48">
        <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12s5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24s8.955,20,20,20s20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"></path><path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"></path><path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"></path><path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571l6.19,5.238C42.022,35.244,44,30.038,44,24C44,22.659,43.862,21.35,43.611,20.083z"></path>
    </svg>
);

export default function SignIn() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [userType, setUserType] = useState('candidate');
  const [formState, setFormState] = useState({ status: 'loading', message: '' });
  const router = useRouter();
  
  // This ref is the key to fixing the race condition.
  // It tracks if a sign-in process is actively being handled.
  const isHandlingAuth = useRef(false);

  // This useEffect now only handles the INITIAL page load.
  // It will not interfere with our sign-in logic.
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      // If a sign-in/out process is currently running, do nothing.
      // Let the handler function take full control.
      if (isHandlingAuth.current) {
        return;
      }
      
      if (user) {
        const userDoc = await getDoc(doc(db, 'users', user.uid));
        if (userDoc.exists()) {
          router.push(userDoc.data().userType === 'candidate' ? '/candidate' : '/company');
        } else {
          await signOut(auth); // Clean up broken state.
        }
      } else {
        // No user, so we are clear to show the sign-in form.
        setFormState({ status: 'idle', message: '' });
      }
    });
    return () => unsubscribe();
  }, [router]);

  const checkUserAndRedirect = useCallback(async (user, isGoogleSignIn = false) => {
    const userDocRef = doc(db, 'users', user.uid);
    const userDoc = await getDoc(userDocRef);
    let userData;

    if (!userDoc.exists()) {
      if (isGoogleSignIn) {
        userData = { email: user.email, fullName: user.displayName, userType, createdAt: new Date(), updatedAt: new Date() };
        await setDoc(userDocRef, userData);
        const profileCollection = userType === 'candidate' ? 'candidates' : 'employers';
        await setDoc(doc(db, profileCollection, user.uid), { userId: user.uid, fullName: user.displayName, email: user.email, createdAt: new Date(), updatedAt: new Date() });
      } else {
        await signOut(auth);
        setFormState({ status: 'error', message: 'Account not found. Please sign up first.' });
        return;
      }
    } else {
      userData = userDoc.data();
    }
    
    // --- THIS IS THE CORRECTED LOGIC FOR THE "WRONG PORTAL" ERROR ---
    if (userData.userType !== userType) {
      const correctUserType = userData.userType;
      // 1. MUST sign out first to stop any potential redirects from the auth listener.
      await signOut(auth);
      // 2. Now that the state is stable, update the UI to show the error and fix the tab.
      setUserType(correctUserType);
      setFormState({ status: 'error', message: `This email is registered as a ${correctUserType}. We've switched the tab for you.` });
      return;
    }

    // Success!
    setFormState({ status: 'success', message: 'Success! Redirecting...' });
    router.push(userData.userType === 'candidate' ? '/candidate' : '/company');

  }, [router, userType]);

  const handleAuthAction = async (authPromise) => {
    // Set the "lock" to true before starting any auth process.
    isHandlingAuth.current = true;
    setFormState({ status: 'loading', message: '' });

    try {
      const userCredential = await authPromise;
      if (userCredential && userCredential.user) {
        await checkUserAndRedirect(userCredential.user, userCredential.providerId === 'google.com');
      }
    } catch (error) {
      if (error.code === 'auth/invalid-credential') {
        setFormState({ status: 'error', message: 'Invalid email or password.' });
      } else if (error.code === 'auth/popup-closed-by-user') {
        setFormState({ status: 'idle', message: '' }); // Not an error, user just cancelled.
      } else {
        console.error("Authentication error:", error);
        setFormState({ status: 'error', message: 'An unexpected error occurred. Please try again.' });
      }
    } finally {
      // ALWAYS release the lock when the process is finished.
      isHandlingAuth.current = false;
    }
  };
  
  if (formState.status === 'loading' && !formState.message) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5] flex items-center justify-center">
            <div className="text-white text-xl">Loading...</div>
        </div>
    );
  }

  const isLoading = formState.status === 'loading';

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Sign in to your account</h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="mb-6">
            <p className="text-center text-sm text-gray-600 mb-2">I am signing in as a:</p>
            <div className="flex justify-center space-x-4">
              <button type="button" onClick={() => setUserType('candidate')} disabled={isLoading} className={`px-4 py-2 rounded-md transition-colors duration-200 text-sm font-medium ${userType === 'candidate' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'} disabled:opacity-50`}>
                Candidate
              </button>
              <button type="button" onClick={() => setUserType('employer')} disabled={isLoading} className={`px-4 py-2 rounded-md transition-colors duration-200 text-sm font-medium ${userType === 'employer' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'} disabled:opacity-50`}>
                Employer
              </button>
            </div>
          </div>

          <form className="space-y-6" onSubmit={(e) => {e.preventDefault(); handleAuthAction(signInWithEmailAndPassword(auth, email, password));}}>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email address</label>
              <input id="email" name="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} disabled={isLoading} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100"/>
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
              <input id="password" name="password" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} disabled={isLoading} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100"/>
            </div>

            {formState.status === 'error' && (
              <div className="rounded-md bg-red-50 p-4">
                <p className="text-sm font-medium text-red-800">{formState.message}</p>
              </div>
            )}

            <div>
              <button type="submit" disabled={isLoading} className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-70 disabled:cursor-not-allowed">
                {isLoading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative"><div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-300"></div></div><div className="relative flex justify-center text-sm"><span className="px-2 bg-white text-gray-500">Or</span></div></div>
            <div className="mt-6">
              <button onClick={() => handleAuthAction(signInWithPopup(auth, googleProvider))} disabled={isLoading} type="button" className="w-full inline-flex justify-center items-center gap-x-2 py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-70 disabled:cursor-not-allowed">
                <GoogleIcon />
                Sign in with Google
              </button>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link href={`/signup?userType=${userType}`} className="font-medium text-blue-600 hover:text-blue-500">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}