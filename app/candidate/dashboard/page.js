"use client"

import { useState, useEffect } from "react"
import Header from "../../../components/Header"
import { Search, Briefcase, CheckCircle, Star, Trophy, Zap, Building2 } from 'lucide-react'

export default function CandidateDashboard() {
  const [jobs, setJobs] = useState([])
  const [profile, setProfile] = useState({})
  const [searchTerm, setSearchTerm] = useState("")
  const [filter, setFilter] = useState("all")

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [jobsResponse, profileResponse] = await Promise.all([
          fetch("/api/candidate/jobs"),
          fetch("/api/candidate/profile")
        ])
        const jobsData = await jobsResponse.json()
        const profileData = await profileResponse.json()
        setJobs(jobsData)
        setProfile(profileData)
      } catch (error) {
        console.error("Error fetching data:", error)
      }
    }
    fetchData()
  }, [])

  const handleApply = async (jobId) => {
    try {
      await fetch("/api/candidate/apply", {
        method: "POST",
        body: JSON.stringify({ jobId }),
      })
      setJobs(jobs.map(job => 
        job.id === jobId ? { ...job, applied: true } : job
      ))
    } catch (error) {
      console.error("Error applying to job:", error)
    }
  }

  const filteredJobs = jobs
    .filter(job => 
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.company.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .filter(job => {
      if (filter === "applied") return job.applied
      if (filter === "matched") return job.matchScore >= 80
      return true
    })


  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold text-white text-center mb-4 animate-fade-in-up">
            Your Job Matches
          </h1>
          <p className="text-xl text-white/90 text-center mb-12 animate-fade-in-up animation-delay-200">
            Our AI has analyzed your profile and found these perfectly matched opportunities.
          </p>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 animate-fade-in-up animation-delay-300">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <Trophy className="h-8 w-8 mb-4" />
              <h3 className="text-3xl font-bold mb-2">94%</h3>
              <p className="text-white/80">Average Match Score</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <Zap className="h-8 w-8 mb-4" />
              <h3 className="text-3xl font-bold mb-2">12</h3>
              <p className="text-white/80">New Matches Today</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <Building2 className="h-8 w-8 mb-4" />
              <h3 className="text-3xl font-bold mb-2">5</h3>
              <p className="text-white/80">Companies Interested</p>
            </div>
          </div>

          {/* Main Content */}
          <div className="bg-white rounded-2xl shadow-xl p-8 animate-fade-in-up animation-delay-400">
            {/* Search and Filter */}
            <div className="flex flex-col md:flex-row gap-4 mb-8">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by job title, company, or skills..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input pl-10"
                />
              </div>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="input md:w-48"
              >
                <option value="all">All Matches</option>
                <option value="applied">Applied Jobs</option>
                <option value="matched">Best Matches</option>
              </select>
            </div>

            {/* Jobs Grid */}
            <div className="grid gap-6">
              {filteredJobs.map((job) => (
                <div key={job.id} className="card hover:shadow-lg transition-shadow">
                  <div className="flex flex-col md:flex-row justify-between gap-6">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="text-xl font-semibold">{job.title}</h3>
                        {job.matchScore >= 80 && (
                          <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full flex items-center gap-1">
                            <Star className="w-4 h-4" />
                            {job.matchScore}% Match
                          </span>
                        )}
                        {job.applied && (
                          <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full flex items-center gap-1">
                            <CheckCircle className="w-4 h-4" />
                            Confirmed Participation
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                        <span className="flex items-center gap-1">
                          <Building2 className="w-4 h-4" />
                          {job.company}
                        </span>
                        <span>{job.location}</span>
                        <span>{job.type}</span>
                      </div>
                      <p className="text-gray-700 mb-4">{job.description}</p>
                      
                      {/* Skill Match Section */}
                      <div className="mb-4">
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Matching Skills</h4>
                        <div className="flex flex-wrap gap-2">
                          {job.matchingSkills?.map((skill) => (
                            <span key={skill} className="px-2 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex flex-col items-stretch gap-3 md:w-48">
                      {!job.applied ? (
                        <button
                          onClick={() => handleApply(job.id)}
                          className="btn-primary flex items-center justify-center gap-2"
                        >
                          <Briefcase className="w-5 h-5" />
                          Next Step
                        </button>
                      ) : (
                        <button
                          disabled
                          className="btn-secondary flex items-center justify-center gap-2 opacity-75"
                        >
                          <CheckCircle className="w-5 h-5" />
                          Confirmed Participation
                        </button>
                      )}
                      <button className="text-sm text-gray-600 hover:text-gray-800">
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}