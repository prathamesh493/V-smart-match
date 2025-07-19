"use client"

import { useState, useEffect, useRef } from "react"
import { FileText, Briefcase, Users, Info, Upload, Building } from "lucide-react"
import Header from "@/components/Header"
import CompanyNavBar from '@/components/CompanyNavBar';
import { useAuth } from "@/lib/useAuth"
import { useApiClient } from "@/lib/clientApiClient"
import { useRouter } from "next/navigation"

export default function JobListingUpload() {
  const { user } = useAuth()
  const api = useApiClient(user)
  const [title, setTitle] = useState("")
  const [numMatches, setNumMatches] = useState(10)
  const [description, setDescription] = useState("")
  const [requirements, setRequirements] = useState("")
  const [companyName, setCompanyName] = useState("")
  const [file, setFile] = useState(null)
  const [fileName, setFileName] = useState("")
  const [showDropdown, setShowDropdown] = useState(false)
  const [jobOptions, setJobOptions] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState("")
  const dropdownRef = useRef(null)
  const router = useRouter()

  useEffect(() => {
    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleTitleChange = async (e) => {
    const newTitle = e.target.value
    setTitle(newTitle)

    if (newTitle.length > 2) {
      setIsLoading(true)
      try {
        const response = await fetch(`/api/job-suggestions?query=${encodeURIComponent(newTitle)}`)
        const data = await response.json()
        setJobOptions(data)
        setShowDropdown(true)
      } catch (error) {
        console.error("Error fetching job suggestions:", error)
      } finally {
        setIsLoading(false)
      }
    } else {
      setShowDropdown(false)
    }
  }

  const selectJobOption = async (jobTitle) => {
    setTitle(jobTitle)
    setShowDropdown(false)

    try {
      const response = await fetch(`/api/job-template?title=${encodeURIComponent(jobTitle)}`)
      const data = await response.json()

      if (data.description) setDescription(data.description)
      if (data.requirements) setRequirements(data.requirements)
    } catch (error) {
      console.error("Error fetching job template:", error)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (selectedFile.type !== "application/pdf") {
        setError("Please upload a PDF file")
        setFile(null)
        setFileName("")
        return
      }

      if (selectedFile.size > 5 * 1024 * 1024) {
        // 5MB limit
        setError("File size exceeds 5MB limit")
        setFile(null)
        setFileName("")
        return
      }

      setFile(selectedFile)
      setFileName(selectedFile.name)
      setError("")
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")

    if (!user) {
      setError("You must be logged in to post a job listing")
      return
    }

    if (!title) {
      setError("Job title is required")
      return
    }

    if (!companyName) {
      setError("Company name is required")
      return
    }

    if (!numMatches || numMatches < 1) {
      setError("Please specify a valid number of matches to generate.");
      return;
    }

    if (!file && !description) {
      setError("Either a job description PDF or text description is required")
      return
    }

    setIsSubmitting(true)

    try {
      const formData = new FormData()

      // Add required fields to FormData
      if (file) {
        formData.append("file", file)
      }

      formData.append("user_id", user.uid)
      formData.append("job_title", title)
      formData.append("company", companyName)

      // If there's a text description, add it too
      if (description) {
        formData.append("description", description)
      }

      if (requirements) {
        formData.append("requirements", requirements)
      }

      formData.append("num_matches", numMatches)

      // Make API call to upload job description with automatic auth
      const response = await api.client.post("/api/job-description/upload", formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Redirect to listings page on success
      router.push("/company/listing")
    } catch (error) {
      console.error("Error uploading job listing:", error)
      setError(error.userMessage || "Failed to upload job listing. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <div className="container mx-auto px-4">
        <CompanyNavBar />
        <main className="py-16">
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-12 animate-fade-in-up">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">Create Job Listing</h1>
              <p className="text-lg text-white/80">Let our AI find the perfect candidates for your role</p>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-xl animate-fade-in-up animation-delay-200">
              <div className="mb-6 p-4 bg-blue-500/20 rounded-lg flex items-start">
                <Info className="w-5 h-5 text-blue-300 mr-3 mt-1 flex-shrink-0" />
                <p className="text-white text-sm">
                  <strong>Pro tip:</strong> You can either upload a PDF job description or fill in the details manually.
                  Start typing a job title to see suggestions that will auto-fill the description fields.
                </p>
              </div>

              {error && (
                <div className="mb-6 p-4 bg-red-500/20 rounded-lg">
                  <p className="text-white text-sm">{error}</p>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-8">
                <div className="space-y-6">
                  <div className="relative">
                    <label htmlFor="title" className="flex items-center text-white text-lg font-medium mb-2">
                      <Briefcase className="w-5 h-5 mr-2" />
                      Job Title*
                    </label>
                    <input
                      type="text"
                      id="title"
                      value={title}
                      onChange={handleTitleChange}
                      required
                      placeholder="e.g. Senior Full Stack Developer"
                      className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/20 transition-all"
                    />

                    {showDropdown && (
                      <div
                        ref={dropdownRef}
                        className="absolute z-10 mt-1 w-full bg-white/10 backdrop-blur-xl rounded-lg shadow-xl border border-white/20 max-h-60 overflow-auto"
                      >
                        {isLoading ? (
                          <div className="p-4 text-white/70 text-center">Loading suggestions...</div>
                        ) : jobOptions.length > 0 ? (
                          <ul>
                            {jobOptions.map((job, index) => (
                              <li
                                key={index}
                                onClick={() => selectJobOption(job.title)}
                                className="px-4 py-3 hover:bg-white/10 cursor-pointer text-white transition-colors"
                              >
                                {job.title}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <div className="p-4 text-white/70 text-center">No matching job titles found</div>
                        )}
                      </div>
                    )}
                  </div>

                  <div>
                    <label htmlFor="companyName" className="flex items-center text-white text-lg font-medium mb-2">
                      <Building className="w-5 h-5 mr-2" />
                      Company Name*
                    </label>
                    <input
                      type="text"
                      id="companyName"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      required
                      placeholder="e.g. Acme Corporation"
                      className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/20 transition-all"
                    />
                  </div>

                  <div>
                    <label htmlFor="numMatches" className="flex items-center text-white text-lg font-medium mb-2">
                      <Users className="w-5 h-5 mr-2" />
                      Number of Candidates to Match*
                    </label>
                    <input
                      type="number"
                      id="numMatches"
                      value={numMatches}
                      onChange={(e) => setNumMatches(parseInt(e.target.value, 10))}
                      required
                      min="1"
                      max="50"
                      placeholder="e.g. 10"
                      className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/20 transition-all"
                    />
                  </div>

                  <div>
                    <label htmlFor="file" className="flex items-center text-white text-lg font-medium mb-2">
                      <Upload className="w-5 h-5 mr-2" />
                      Upload Job Description (PDF)
                    </label>
                    <div className="relative">
                      <input
                        type="file"
                        id="file"
                        onChange={handleFileChange}
                        accept="application/pdf"
                        className="sr-only"
                      />
                      <label
                        htmlFor="file"
                        className="flex items-center justify-center w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white/70 cursor-pointer hover:bg-white/10 transition-all"
                      >
                        <Upload className="w-5 h-5 mr-2" />
                        {fileName ? fileName : "Choose PDF file (Max 5MB)"}
                      </label>
                    </div>
                  </div>

                  <div className="relative pt-6">
                    <div className="absolute inset-0 flex items-center" aria-hidden="true">
                      <div className="w-full border-t border-white/10"></div>
                    </div>
                    <div className="relative flex justify-center">
                      <span className="bg-[#4f46e5]/20 backdrop-blur-sm px-3 text-white/70 text-sm">
                        Or enter details manually
                      </span>
                    </div>
                  </div>

                  <div>
                    <label htmlFor="description" className="flex items-center text-white text-lg font-medium mb-2">
                      <FileText className="w-5 h-5 mr-2" />
                      Job Description
                    </label>
                    <textarea
                      id="description"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Describe the role, responsibilities, and opportunities..."
                      className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/20 transition-all h-40"
                    />
                  </div>

                  <div>
                    <label htmlFor="requirements" className="flex items-center text-white text-lg font-medium mb-2">
                      <Users className="w-5 h-5 mr-2" />
                      Requirements
                    </label>
                    <textarea
                      id="requirements"
                      value={requirements}
                      onChange={(e) => setRequirements(e.target.value)}
                      placeholder="List required skills, experience, and qualifications..."
                      className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/20 transition-all h-40"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-gradient-to-r from-pink-500 to-violet-500 text-white py-4 px-6 rounded-lg font-semibold hover:from-pink-600 hover:to-violet-600 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-70 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? "Posting Job Listing..." : "Post Job Listing"}
                </button>
              </form>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
