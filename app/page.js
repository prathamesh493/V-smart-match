import Link from "next/link"
import { ArrowRight } from 'lucide-react'
import Header from "@/components/Header"

export default function Home() {
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
                href="/company"
                className="btn-primary group"
              >
                For Recruiters
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link
                href="/candidate"
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