"use client"

import { useState, useEffect, useRef } from "react"
import { FileText, Briefcase, Users, Info } from 'lucide-react'
import Header from "@/components/Header"

export default function JobListingUpload() {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [requirements, setRequirements] = useState("")
  const [showDropdown, setShowDropdown] = useState(false)
  const [jobOptions, setJobOptions] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const dropdownRef = useRef(null)

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

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log("Job listing upload:", { title, description, requirements })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12 animate-fade-in-up">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Create Job Listing
            </h1>
            <p className="text-lg text-white/80">
              Let our AI find the perfect candidates for your role
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-xl animate-fade-in-up animation-delay-200">
            <div className="mb-6 p-4 bg-blue-500/20 rounded-lg flex items-start">
              <Info className="w-5 h-5 text-blue-300 mr-3 mt-1 flex-shrink-0" />
              <p className="text-white text-sm">
                <strong>Pro tip:</strong> Start typing a job title to see suggestions. 
                Selecting a suggestion will automatically populate the description and requirements,
                which you can then customize as needed.
              </p>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-8">
              <div className="space-y-6">
                <div className="relative">
                  <label htmlFor="title" className="flex items-center text-white text-lg font-medium mb-2">
                    <Briefcase className="w-5 h-5 mr-2" />
                    Job Title
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
                  <label htmlFor="description" className="flex items-center text-white text-lg font-medium mb-2">
                    <FileText className="w-5 h-5 mr-2" />
                    Job Description
                  </label>
                  <textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    required
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
                    required
                    placeholder="List required skills, experience, and qualifications..."
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/20 transition-all h-40"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-pink-500 to-violet-500 text-white py-4 px-6 rounded-lg font-semibold hover:from-pink-600 hover:to-violet-600 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Post Job Listing
              </button>
            </form>
          </div>
        </div>
      </main>
    </div>
  )
}