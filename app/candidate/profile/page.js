"use client"

import { useState, useEffect } from "react"
import Header from "../../../components/Header"
import { Upload, Github, Code2, CheckCircle2, Brain, Trophy } from 'lucide-react'
import Notification from "../../../components/Notification"

export default function CandidateProfile() {
  const [formData, setFormData] = useState({
    resume: null,
    github: "",
    leetcode: "",
    skills: [],
    experience: [],
    education: []
  })
  const [newSkill, setNewSkill] = useState("")
  const [fileName, setFileName] = useState("") // New state for displaying filename
  const [notification, setNotification] = useState(null) // For success/error notifications

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch("/api/candidate/profile")
        const data = await response.json()
        setFormData(data)
        // Set filename if resume exists in fetched data
        if (data.resume && data.resume.name) {
          setFileName(data.resume.name)
        }
      } catch (error) {
        console.error("Error fetching profile:", error)
      }
    }
    fetchProfile()
  }, [])

  const handleAddSkill = () => {
    if (newSkill.trim() && !formData.skills.includes(newSkill.trim())) {
      setFormData({
        ...formData,
        skills: [...formData.skills, newSkill.trim()]
      })
      setNewSkill("")
    }
  }

  const handleRemoveSkill = (skillToRemove) => {
    setFormData({
      ...formData,
      skills: formData.skills.filter(skill => skill !== skillToRemove)
    })
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setFormData({...formData, resume: file})
      setFileName(file.name) // Update the filename state
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch("/api/candidate/profile", {
        method: "PUT",
        body: JSON.stringify(formData)
      })
      if (response.ok) {
        // Show success notification
        setNotification({
          type: 'success',
          message: 'Your profile has been successfully updated. Our AI is analyzing your data to match you with the best opportunities.'
        })
      } else {
        // Show error notification for unsuccessful response
        setNotification({
          type: 'error',
          message: 'There was a problem updating your profile. Please check your information and try again.'
        })
      }
    } catch (error) {
      console.error("Error updating profile:", error)
      // Show error notification for exception
      setNotification({
        type: 'error',
        message: 'Connection error. Please check your internet connection and try again.'
      })
    }
  }
  
  // Helper to close the notification
  const closeNotification = () => {
    setNotification(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      {notification && (
        <Notification
          type={notification.type}
          message={notification.message}
          onClose={closeNotification}
        />
      )}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto">
          {/* Add the animation classes to the global styles in your app */}
          <style jsx global>{`
            @keyframes slideInRight {
              from {
                transform: translateX(100%);
                opacity: 0;
              }
              to {
                transform: translateX(0);
                opacity: 1;
              }
            }
            .animate-slide-in-right {
              animation: slideInRight 0.3s ease-out forwards;
            }
          `}</style>
          <h1 className="text-4xl md:text-5xl font-bold text-white text-center mb-4 animate-fade-in-up">
            Build Your Professional Profile
          </h1>
          <p className="text-xl text-white/90 text-center mb-8 animate-fade-in-up animation-delay-200">
            Let AI analyze your experience and skills to match you with the perfect opportunities.
          </p>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 animate-fade-in-up animation-delay-300">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <Upload className="h-8 w-8 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Smart Resume Analysis</h3>
              <p className="text-white/80 text-sm">Our AI extracts your skills and experience automatically from your resume.</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <Brain className="h-8 w-8 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Skills Enhancement</h3>
              <p className="text-white/80 text-sm">Add additional skills and certifications to showcase your full potential.</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <Trophy className="h-8 w-8 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Code Profile Integration</h3>
              <p className="text-white/80 text-sm">Connect your GitHub and LeetCode to highlight your practical skills.</p>
            </div>
          </div>

          {/* Main Form */}
          <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-xl p-8 animate-fade-in-up animation-delay-400">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="label flex items-center gap-2">
                  <Upload className="h-5 w-5 text-primary" />
                  Resume Upload
                </label>
                <div className="relative flex items-center gap-3 bg-gray-50 hover:bg-gray-100 transition-colors rounded-md p-3 cursor-pointer">
                  <span className="text-gray-500">
                    {fileName ? fileName : "PDF, DOC, or DOCX (Max 5MB)"}
                  </span>
                  <label className="ml-auto cursor-pointer bg-gray-200 hover:bg-gray-300 py-1 px-3 rounded-md text-sm">
                    Browse
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Our AI will analyze your resume to extract skills and experience automatically.
                </p>
              </div>
              
              <div>
                <label className="label flex items-center gap-2">
                  <Github className="h-5 w-5 text-primary" />
                  GitHub Profile
                </label>
                <div className="relative">
                  <input
                    type="url"
                    value={formData.github}
                    onChange={(e) => setFormData({...formData, github: e.target.value})}
                    className="input pl-10"
                    placeholder="https://github.com/yourusername"
                  />
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  We'll analyze your repositories to highlight your coding expertise.
                </p>
              </div>
              
              <div>
                <label className="label flex items-center gap-2">
                  <Code2 className="h-5 w-5 text-primary" />
                  LeetCode Profile
                </label>
                <div className="relative">
                  <input
                    type="url"
                    value={formData.leetcode}
                    onChange={(e) => setFormData({...formData, leetcode: e.target.value})}
                    className="input pl-10"
                    placeholder="https://leetcode.com/yourusername"
                  />
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Your problem-solving abilities will boost your match scores.
                </p>
              </div>
              
              <div className="md:col-span-2">
                <label className="label flex items-center gap-2">
                  <Brain className="h-5 w-5 text-primary" />
                  Additional Skills
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    className="input"
                    placeholder="Add a skill..."
                  />
                  <button
                    type="button"
                    onClick={handleAddSkill}
                    className="btn-primary whitespace-nowrap"
                  >
                    Add Skill
                  </button>
                </div>
                <p className="text-sm text-gray-500 mb-3">
                  Add any skills not mentioned in your resume to improve job matches.
                </p>
                <div className="flex flex-wrap gap-2">
                  {formData.skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-3 py-1 bg-gray-100 rounded-full flex items-center gap-2 hover:bg-gray-200 transition-colors"
                    >
                      {skill}
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(skill)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="mt-8">
              <button
                type="submit"
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <CheckCircle2 className="h-5 w-5" />
                Complete Profile
              </button>
              <p className="text-center text-sm text-gray-500 mt-2">
                Your profile will be automatically matched with relevant job opportunities.
              </p>
            </div>
          </form>
        </div>
      </main>
    </div>
  )
}