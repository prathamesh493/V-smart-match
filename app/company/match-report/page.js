"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { UserCircle, AlertCircle, Search, ArrowLeft } from "lucide-react"
import Header from "@/components/Header"
import Link from "next/link"
import { useAuth } from "@/lib/useAuth"

export default function MatchReport() {
  const [candidates, setCandidates] = useState([])
  const [jobDetails, setJobDetails] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [threshold, setThreshold] = useState(47)
  const [searchTerm, setSearchTerm] = useState("")
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user, loading: authLoading } = useAuth()
  const jobId = searchParams.get("jobId")

  // Track authentication loading separately from data loading
  const [isDataLoading, setIsDataLoading] = useState(false)

  // Handle authentication and initial redirect
  useEffect(() => {
    // Only redirect if we're sure the user is not authenticated (after auth loading completes)
    if (!user && !authLoading) {
      router.push("/signin")
    }
  }, [user, authLoading, router])

  // Handle data fetching separately, only when auth is complete and we have a user
  useEffect(() => {
    // Only fetch data if we have a user and jobId and auth loading is complete
    if (user && jobId && !authLoading) {
      const fetchData = async () => {
        setIsDataLoading(true)
        setError("")

        try {
          // Fetch job details
          const jobResponse = await fetch(`http://localhost:8000/api/job-description/${jobId}`)
          if (!jobResponse.ok) {
            throw new Error("Failed to fetch job details")
          }
          const jobData = await jobResponse.json()
          setJobDetails(jobData)

          // Fetch matches for this job
          const matchesResponse = await fetch(`http://localhost:8000/api/match/job/${jobId}`)
          if (!matchesResponse.ok) {
            throw new Error("Failed to fetch candidate matches")
          }
          const matchesData = await matchesResponse.json()
          setCandidates(matchesData)
        } catch (error) {
          console.error("Error fetching data:", error)
          setError(error.message || "Failed to load data")
        } finally {
          setIsDataLoading(false)
        }
      }

      fetchData()
    }
  }, [jobId, user, authLoading]) // Remove isLoading from dependencies

  const filteredCandidates = candidates
    .filter((candidate) => candidate.overallScore >= threshold)
    .filter((candidate) => {
      if (!searchTerm) return true
      // This is a simplified search - in a real app, you'd have more candidate data to search through
      return (
        candidate.matchId.toLowerCase().includes(searchTerm.toLowerCase()) ||
        candidate.candidateId.toLowerCase().includes(searchTerm.toLowerCase())
      )
    })
    .sort((a, b) => b.overallScore - a.overallScore)

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <Link href="/company/listing" className="text-white/80 hover:text-white flex items-center">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Job Listings
            </Link>
          </div>

          {authLoading || isDataLoading ? (
            <div className="flex justify-center items-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
            </div>
          ) : error ? (
            <div className="bg-red-500/20 backdrop-blur-sm rounded-lg p-6 text-center">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-white" />
              <p className="text-white text-lg">{error}</p>
              <Link
                href="/company/listing"
                className="mt-4 px-6 py-2 bg-white text-purple-700 rounded-lg font-medium inline-block"
              >
                Return to Listings
              </Link>
            </div>
          ) : (
            <>
              <h1 className="text-4xl md:text-5xl font-bold text-white text-center mb-4">Candidate Matches</h1>
              {jobDetails && (
                <div className="text-center mb-8">
                  <h2 className="text-2xl text-white/90 mb-2">{jobDetails.job_title}</h2>
                  <p className="text-xl text-white/80">{jobDetails.company}</p>
                </div>
              )}

              <div className="mb-8">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-white/50" />
                  <input
                    type="text"
                    placeholder="Search candidates..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-12 py-4 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30"
                  />
                </div>
              </div>

              <div className="backdrop-blur-lg bg-white/10 rounded-xl p-6 mb-12 border border-white/20">
                <h2 className="text-lg font-semibold mb-4 text-white">Minimum Qualification Threshold: {threshold}%</h2>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={threshold}
                  onChange={(e) => setThreshold(Number(e.target.value))}
                  className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer"
                  style={{
                    background: `linear-gradient(to right, rgba(255,255,255,0.8) ${threshold}%, rgba(255,255,255,0.2) ${threshold}%)`,
                  }}
                />
              </div>

              {filteredCandidates.length === 0 ? (
                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-12 text-center">
                  <UserCircle className="h-16 w-16 mx-auto mb-4 text-white/70" />
                  <h2 className="text-2xl font-bold text-white mb-2">No Matching Candidates Found</h2>
                  <p className="text-white/70 mb-6">
                    {threshold > 0
                      ? `Try lowering the qualification threshold below ${threshold}%`
                      : "There are no candidate matches for this job listing yet."}
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredCandidates.map((candidate) => (
                    <div
                      key={candidate.matchId}
                      className="backdrop-blur-lg bg-white/10 rounded-xl p-6 border border-white/20 hover:shadow-xl transition-all duration-300 hover:scale-105 group"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-4">
                          <div className="p-2 rounded-full bg-white/20 group-hover:bg-white/30 transition-colors">
                            <UserCircle className="h-8 w-8 text-white" />
                          </div>
                          <div>
                            <h3 className="text-xl font-bold text-white">
                              Candidate {candidate.candidateId.substring(0, 6)}
                            </h3>
                            <p className="text-sm text-white/75">Match ID: {candidate.matchId.substring(0, 10)}...</p>
                          </div>
                        </div>
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                            candidate.overallScore >= 80
                              ? "bg-green-500/30 text-green-100"
                              : candidate.overallScore >= 60
                                ? "bg-yellow-500/30 text-yellow-100"
                                : "bg-red-500/30 text-red-100"
                          }`}
                        >
                          {candidate.overallScore}% Match
                        </span>
                      </div>

                      <div className="mb-6">
                        <h4 className="font-medium mb-2 text-white/90">Key Skills</h4>
                        <div className="flex flex-wrap gap-2">
                          {candidate.categoryScores?.skillsMatch?.keyMatches?.map((skill, index) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-white/20 rounded-full text-sm text-white/90 hover:bg-white/30 transition-colors"
                            >
                              {skill.skill} ({skill.relevance}%)
                            </span>
                          )) || <span className="text-white/60">No skills data available</span>}
                        </div>
                      </div>

                      <Link
                        href={`/company/report/${candidate.matchId}`}
                        className="block w-full py-3 px-6 bg-white/20 text-white text-center rounded-full font-semibold hover:bg-white/30 transition-colors border border-white/20"
                      >
                        View Profile
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  )
}
