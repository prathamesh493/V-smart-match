"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Header from "../../components/Header"

export default function SignIn() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const router = useRouter()

  const handleSubmit = (e) => {
    e.preventDefault()
    // Here you would typically handle the authentication logic
    console.log("Sign in attempt with:", email, password)
    // For this PoC, we'll just redirect to the candidate dashboard
    router.push("/candidate/dashboard")
  }

  return (
    (<div>
      <Header />
      <main className="container mx-auto mt-10 px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-[#c6269e]">Sign In</h1>
        <form onSubmit={handleSubmit} className="max-w-md mx-auto">
          <div className="mb-4">
            <label htmlFor="email" className="label">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="input" />
          </div>
          <div className="mb-6">
            <label htmlFor="password" className="label">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="input" />
          </div>
          <button type="submit" className="btn-primary w-full">
            Sign In
          </button>
        </form>
      </main>
    </div>)
  );
}

