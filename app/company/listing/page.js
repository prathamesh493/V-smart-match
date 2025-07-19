"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Briefcase, Building2, Calendar, FileText, Search, Users, AlertCircle } from "lucide-react"
import Header from "@/components/Header"
import { useAuth } from "@/lib/useAuth"
import Link from "next/link"
import CompanyNavBar from '@/components/CompanyNavBar';

// Get API base URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function JobListings() {
  const [jobListings, setJobListings] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [searchTerm, setSearchTerm] = useState("")
  const { user } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Redirect if not logged in
    if (!user && !isLoading) {
      router.push("/signin")
      return
    }

    if (user) {
      fetchJobListings()
    }
  }, [user])

  const fetchJobListings = async () => {
    setIsLoading(true)
    setError("")

    try {
      const response = await fetch(`${API_URL}/api/job-description/user/${user.uid}`)

      if (!response.ok) {
        throw new Error("Failed to fetch job listings")
      }

      const data = await response.json()
      console.log("Job Listings:", data) // Debugging line
      setJobListings(data)
    } catch (error) {
      console.error("Error fetching job listings:", error)
      setError("Failed to load job listings. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  const filteredListings = jobListings.filter(
    (job) =>
      job.job_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.company?.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <div className="container mx-auto px-4">
        <CompanyNavBar />
        <main className="py-16">
          <div className="max-w-5xl mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-center mb-12">
              <div className="mb-6 md:mb-0">
                <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">Your Job Listings</h1>
                <p className="text-lg text-white/80">Manage your active job postings and view candidate matches</p>
              </div>
              <Link
                href="/company/upload"
                className="bg-white text-purple-700 hover:bg-white/90 transition-colors px-6 py-3 rounded-lg font-semibold shadow-lg"
              >
                Post New Job
              </Link>
            </div>

            {/* Search Bar */}
            <div className="mb-8">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-white/50" />
                <input
                  type="text"
                  placeholder="Search job listings..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-12 py-4 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30"
                />
              </div>
            </div>

            {isLoading ? (
              <div className="flex justify-center items-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
              </div>
            ) : error ? (
              <div className="bg-red-500/20 backdrop-blur-sm rounded-lg p-6 text-center">
                <AlertCircle className="h-12 w-12 mx-auto mb-4 text-white" />
                <p className="text-white text-lg">{error}</p>
                <button
                  onClick={fetchJobListings}
                  className="mt-4 px-6 py-2 bg-white text-purple-700 rounded-lg font-medium"
                >
                  Try Again
                </button>
              </div>
            ) : filteredListings.length === 0 ? (
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-12 text-center">
                <Briefcase className="h-16 w-16 mx-auto mb-4 text-white/70" />
                <h2 className="text-2xl font-bold text-white mb-2">No Job Listings Found</h2>
                <p className="text-white/70 mb-6">
                  {searchTerm
                    ? "No job listings match your search criteria."
                    : "You haven't posted any job listings yet."}
                </p>
                <Link
                  href="/company/upload"
                  className="inline-block px-6 py-3 bg-gradient-to-r from-pink-500 to-violet-500 text-white rounded-lg font-semibold"
                >
                  Post Your First Job
                </Link>
              </div>
            ) : (
              <div className="grid gap-6">
                {filteredListings.map((job) => (
                  <div
                    key={job.doc_id || job.file_name}
                    className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20 hover:bg-white/15 transition-colors"
                  >
                    <div className="flex flex-col md:flex-row justify-between">
                      <div className="mb-4 md:mb-0">
                        <h2 className="text-2xl font-bold text-white mb-2">{job.job_title}</h2>
                        <div className="flex flex-wrap gap-4 text-white/80">
                          <div className="flex items-center">
                            <Building2 className="h-4 w-4 mr-2" />
                            {job.company}
                          </div>
                          <div className="flex items-center">
                            <Calendar className="h-4 w-4 mr-2" />
                            {formatDate(job.timestamp)}
                          </div>
                          <div className="flex items-center">
                            <FileText className="h-4 w-4 mr-2" />
                            {job.file_name?.split("_").pop().substring(0, 8) || "No file"}
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-col sm:flex-row gap-3">
                        <Link
                          href={`/company/match-report?jobId=${job.doc_id}`}
                          className="px-5 py-2 bg-gradient-to-r from-pink-500 to-violet-500 text-white rounded-lg font-medium text-center hover:from-pink-600 hover:to-violet-600 transition-colors"
                        >
                          <Users className="h-4 w-4 inline mr-2" />
                          View Matches
                        </Link>
                      </div>
                    </div>

                    {job.extracted_content && (
                      <div className="mt-4">
                        <div className="bg-white/5 rounded-lg p-4 max-h-40 overflow-y-auto text-white/80 text-sm">
                          {job.extracted_content.substring(0, 300)}
                          {job.extracted_content.length > 300 && "..."}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
