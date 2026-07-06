'use client';

// app/signup/page.js
import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { createUserWithEmailAndPassword, signInWithPopup } from 'firebase/auth';
import { doc, setDoc, getDoc } from 'firebase/firestore';
import { auth, db, googleProvider } from '../../firebase/config';
import Link from 'next/link';
import { onAuthStateChanged } from 'firebase/auth';

// A simple Google Icon component
const GoogleIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 48 48">
    <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12s5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24s8.955,20,20,20s20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"></path>
    <path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"></path>
    <path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"></path>
    <path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571l6.19,5.238C42.022,35.244,44,30.038,44,24C44,22.659,43.862,21.35,43.611,20.083z"></path>
  </svg>
);

export default function SignUp() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const [userType, setUserType] = useState('candidate'); // default
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    const type = searchParams.get('userType');
    if (type === 'employer' || type === 'candidate') {
      setUserType(type);
    }
  }, [searchParams]);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        const userDocRef = doc(db, 'users', user.uid);
        const userDoc = await getDoc(userDocRef);
        
        if (userDoc.exists()) {
          const userData = userDoc.data();
          router.push(userData.userType === 'candidate' ? '/candidate' : '/company');
          return;
        }
      }
      setAuthLoading(false);
    });

    return () => unsubscribe();
  }, [router]);
  
  if (authLoading) {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-gray-600 text-xl">Loading...</div>
    </div>
  );
}

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    setLoading(true);

    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      await createFirestoreUser(user.uid, user.email, fullName);
      
      // Redirect based on userType instead of going to signin
      router.push(userType === 'candidate' ? '/candidate' : '/company');

    } catch (error) {
      console.error('Error signing up:', error);
      let friendlyMessage = 'Failed to sign up. Please try again.';
      if (error.code === 'auth/email-already-in-use') {
        friendlyMessage = 'An account with this email already exists. Please sign in.';
      } else if (error.code === 'auth/weak-password') {
        friendlyMessage = 'Password should be at least 6 characters.';
      }
      setError(friendlyMessage);
    } finally {
        setLoading(false);
    }
  };

  const handleGoogleSignUp = async () => {
    setError('');
    setLoading(true);
    try {
        const result = await signInWithPopup(auth, googleProvider);
        const user = result.user;

        const userDocRef = doc(db, 'users', user.uid);
        const userDoc = await getDoc(userDocRef);

        if (userDoc.exists()) {
            setError('This account already exists. Please proceed to sign in.');
            await auth.signOut();
            setLoading(false);
            return;
        }

        await createFirestoreUser(user.uid, user.email, user.displayName);
        
        // Redirect based on userType instead of going to signin
        router.push(userType === 'candidate' ? '/candidate' : '/company');

    } catch (error) {
        console.error('Error with Google sign-up:', error);
        let friendlyMessage = 'Failed to sign up with Google.';
        if (error.code === 'auth/popup-closed-by-user') {
            friendlyMessage = 'The sign-up process was cancelled.';
        } else if (error.code === 'auth/account-exists-with-different-credential') {
            friendlyMessage = 'An account with this email already exists with a different sign-in method.';
        } else if (error.code === 'auth/operation-not-allowed') {
            friendlyMessage = 'Sign-in with Google is not enabled. Please contact support.';
        }
        setError(friendlyMessage);
    } finally {
        setLoading(false);
    }
  }

  // Helper function to create user documents in Firestore
  const createFirestoreUser = async (uid, email, name) => {
    await setDoc(doc(db, 'users', uid), {
      email,
      fullName: name,
      userType,
      createdAt: new Date(),
      updatedAt: new Date()
    });

    if (userType === 'candidate') {
      await setDoc(doc(db, 'candidates', uid), {
        userId: uid,
        fullName: name,
        email,
        skills: [], experience: [], education: [], resumeUrl: '',
        createdAt: new Date(), updatedAt: new Date()
      });
    } else { // 'employer'
      await setDoc(doc(db, 'employers', uid), {
        userId: uid,
        companyName: name,
        email,
        industry: '', companySize: '', location: '', companyDescription: '',
        createdAt: new Date(), updatedAt: new Date()
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="mb-6">
            <p className="text-center text-sm text-gray-600 mb-2">I am signing up as a:</p>
            <div className="flex justify-center space-x-4">
              <button
                type="button" onClick={() => setUserType('candidate')}
                className={`px-4 py-2 rounded-md transition-colors duration-200 ${ userType === 'candidate' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300' }`}
              >
                Candidate
              </button>
              <button
                type="button" onClick={() => setUserType('employer')}
                className={`px-4 py-2 rounded-md transition-colors duration-200 ${ userType === 'employer' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300' }`}
              >
                Employer
              </button>
            </div>
          </div>
          <form className="space-y-6" onSubmit={handleSignUp}>
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-gray-700">
                {userType === 'candidate' ? 'Full Name' : 'Company Name'}
              </label>
              <input id="fullName" name="fullName" type="text" required value={fullName} onChange={(e) => setFullName(e.target.value)}
                className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email address</label>
              <input id="email" name="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
              <input id="password" name="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">Confirm Password</label>
              <input id="confirmPassword" name="confirmPassword" type="password" required value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
                className="mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <p className="text-sm font-medium text-red-800">{error}</p>
              </div>
            )}
            <div>
              <button type="submit" disabled={loading} className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}>
                {loading ? 'Creating account...' : 'Sign up'}
              </button>
            </div>
          </form>
            
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-300"></div></div>
              <div className="relative flex justify-center text-sm"><span className="px-2 bg-white text-gray-500">Or sign up with</span></div>
            </div>
            <div className="mt-6">
                <button onClick={handleGoogleSignUp} disabled={loading} type="button" className="w-full inline-flex justify-center items-center gap-x-2 py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-70 disabled:cursor-not-allowed">
                    <GoogleIcon />
                    Google
                </button>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link href={`/signin?userType=${userType}`} className="font-medium text-blue-600 hover:text-blue-500">Sign in</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}