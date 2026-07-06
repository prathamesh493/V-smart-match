"use client"
import { useEffect, useState } from 'react'
import { onAuthStateChanged } from 'firebase/auth'
import { doc, getDoc } from 'firebase/firestore'
import { auth, db } from '@/firebase/config'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

export default function Home() {
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState(null)
  const router = useRouter()

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setUser(user)
        try {
          const userDocRef = doc(db, 'users', user.uid)
          const userDoc = await getDoc(userDocRef)

          if (userDoc.exists()) {
            const userData = userDoc.data()
            const firestoreUserType = userData.userType

            // Redirect based on userType from Firestore
            if (firestoreUserType === 'candidate') {
              router.push('/candidate')
            } else {
              router.push('/company')
            }
          } else {
            console.log("No user document found in Firestore. Redirecting to profile setup.")
            // Optional: Redirect to a profile setup page if the user document doesn't exist
            // router.push('/profile-setup')
            setLoading(false) // Stop loading as we are not redirecting to a dashboard
          }
        } catch (error) {
          console.error("Error fetching user data:", error)
          setLoading(false) // Stop loading on error
        }
      } else {
        setUser(null)
        setLoading(false)
      }
    })

    // Cleanup subscription on unmount
    return () => unsubscribe()
  }, [router])

  // Display a loading screen while checking for authentication and user data
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5] flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    )
  }

  // If a user is logged in, the redirection is in progress, so we render nothing.
  if (user) {
    return null
  }

  // Render the homepage content only if there is no authenticated user
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16 text-white">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          {/* Left Column - Text Content */}
          <div className="flex flex-col space-y-8">
            <h1 className="text-5xl md:text-7xl font-bold animate-fade-in-up">
              Welcome to vSmart Match
            </h1>
            <p className="text-xl md:text-2xl max-w-2xl animate-fade-in-up animation-delay-200">
              Precision hiring platform that matches candidates with job descriptions using automated skill extraction.
            </p>
            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-6 animate-fade-in-up animation-delay-400">
              <Link
                href="/signin?userType=employer"
                className="btn-primary group"
              >
                For Recruiters
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link
                href="/signin?userType=candidate"
                className="btn-secondary group"
              >
                For Candidates
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </div>

          {/* Right Column - Image */}
          <div className="flex justify-center lg:justify-end animate-float">
            <img
              src="vsmartmatch.svg"
              alt="vSmart Match Illustration"
              className="max-w-full h-auto rounded-lg shadow-2xl"
            />
          </div>
        </div>
      </main>
    </div>
  )
}