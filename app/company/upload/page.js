"use client"

import { useState } from "react"
import { FileText, Briefcase, Users } from 'lucide-react'
import Header from "@/components/Header"

export default function JobListingUpload() {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [requirements, setRequirements] = useState("")

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
            <form onSubmit={handleSubmit} className="space-y-8">
              <div className="space-y-6">
                <div>
                  <label htmlFor="title" className="flex items-center text-white text-lg font-medium mb-2">
                    <Briefcase className="w-5 h-5 mr-2" />
                    Job Title
                  </label>
                  <input
                    type="text"
                    id="title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                    placeholder="e.g. Senior Full Stack Developer"
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/20 transition-all"
                  />
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