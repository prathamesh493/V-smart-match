"use client"

import { useState, useEffect } from "react"
import Header from "../../../components/Header"
import { Upload, Github, Code2, CheckCircle2, Brain, Trophy } from 'lucide-react'
import Notification from "../../../components/Notification"
import { ProfileCompletion } from "../../../components/ProfileCompletion"
import axios from "axios"
import { useAuth } from "../../../lib/useAuth"

// Get API base URL from environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://mj.local:8000'

export default function CandidateProfile() {
  const { user, loading: authLoading } = useAuth() // Use authentication hook
  const [formData, setFormData] = useState({
    resume: null,
    github: "",
    leetcode: "",
    skills: [],
    experience: [],
    education: []
  })
  const [userId, setUserId] = useState(null) // Initialize as null instead of demo_user
  const [newSkill, setNewSkill] = useState("")
  const [fileName, setFileName] = useState("") // For displaying filename
  const [notification, setNotification] = useState(null) // For notifications
  const [isLoading, setIsLoading] = useState(false) // Loading state
  const [apiConnectionError, setApiConnectionError] = useState(false) // API connection error state
  const [profileData, setProfileData] = useState(null) // Profile data from backend
  const [isExtracting, setIsExtracting] = useState(false) // Extracting state

  // Get userId from authentication
  useEffect(() => {
    if (user) {
      console.log('Setting userId from auth:', user.uid)
      setUserId(user.uid)
    }
  }, [user])

  // Move fetchCandidateProfile outside the useEffect so it can be called from other functions
  const fetchCandidateProfile = async () => {
    if (!userId || !user) return
    
    setIsLoading(true)
    setApiConnectionError(false)
    
    try {
      // Get auth token
      const token = await user.getIdToken()
      
      // Fetch unified candidate profile from backend with auth token
      const response = await axios.get(`${API_BASE_URL}/api/candidate/profile/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      console.log('Profile data received:', response.data)
      
      const profileData = response.data
      
      // Update form data with profile information
      setFormData({
        resume: null, // File object will be set on upload
        github: profileData.github?.username ? profileData.github.username : "",
        leetcode: profileData.leetcode?.username ? profileData.leetcode.username : "",
        skills: profileData.skills || [],
        experience: profileData.experience || [],
        education: profileData.education || []
      })
      
      // Set profile data for other components
      setProfileData(profileData)
      
      // Set filename if resume exists
      if (profileData.resume && profileData.resume.file_name) {
        setFileName(profileData.resume.file_name)
      }
    } catch (error) {
      console.error('Error fetching candidate profile:', error)
      
      if (error.message && error.message.includes('Network Error')) {
        setApiConnectionError(true)
      } else if (error.response?.status === 404) {
        // No profile found - this is okay for new users
        console.log('No profile found for user, creating a new one')
      } else {
        setNotification({
          type: 'error',
          message: 'Error loading profile. Please try again later.'
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  // Fetch profile data when userId changes
  useEffect(() => {
    fetchCandidateProfile()
  }, [userId, user])

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

  // Handle resume upload
  const uploadResume = async (file) => {
    if (!user) {
      setNotification({
        type: 'error',
        message: 'You must be logged in to upload a resume'
      });
      return null;
    }
    
    try {
      setIsLoading(true);
      
      // Get auth token
      const token = await user.getIdToken();
      
      const formData = new FormData();
      formData.append('file', file);
      // Backend gets user_id from authentication token
      
      const response = await axios.post(
        `${API_BASE_URL}/api/resume/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      console.log("Resume upload response:", response.data);
      setNotification({
        type: 'success',
        message: 'Resume uploaded successfully!'
      });
      
      // Refresh candidate profile after upload
      fetchCandidateProfile();
      
      return response.data; // Return the response data for further processing
      
    } catch (error) {
      console.error("Error uploading resume:", error);
      setNotification({
        type: 'error',
        message: error.response?.data?.detail || 'Failed to upload resume. Please try again.'
      });
      return null;
    } finally {
      setIsLoading(false);
    }
  }

  const fetchGitHubProfile = async (githubUsername) => {
    if (!githubUsername) return null
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/github/${githubUsername}`)
      return response.data
    } catch (error) {
      console.warn('Error fetching GitHub profile:', error)
      return null
    }
  }

  const fetchLeetCodeProfile = async (leetcodeUsername) => {
    if (!leetcodeUsername) return null
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/leetcode/${leetcodeUsername}`)
      return response.data
    } catch (error) {
      console.warn('Error fetching LeetCode profile:', error)
      return null
    }
  }

  // Link GitHub and LeetCode profiles
  const linkProfiles = async (formData) => {
    try {
      setIsLoading(true)
      
      // Get auth token
      const token = await user.getIdToken()
      
      const response = await axios.post(
        `${API_BASE_URL}/api/candidate/link-profiles`,
        {
          github_username: formData.github,
          leetcode_username: formData.leetcode
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      )
      
      console.log("Link profiles response:", response.data)
      setNotification({
        type: 'success',
        message: 'Profiles linked successfully!'
      })
      
      // Refresh candidate profile after linking
      fetchCandidateProfile()
      
    } catch (error) {
      console.error("Error linking profiles:", error)
      setNotification({
        type: 'error',
        message: error.response?.data?.message || 'Failed to link profiles. Please try again.'
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Helper functions to extract usernames from URLs
  const extractGitHubUsername = (input) => {
    // If it's already just a username, return it
    if (!input.includes('/') && !input.includes('.')) {
      return input.trim();
    }
    
    // Handle full GitHub URLs or variations
    try {
      // Remove trailing slash if present
      const cleaned = input.replace(/\/$/, '');
      
      // Handle github.com URLs
      if (cleaned.includes('github.com/')) {
        return cleaned.split('github.com/')[1].split('/')[0];
      }
      
      // Handle direct usernames or other URL formats
      const parts = cleaned.split('/');
      return parts[parts.length - 1];
    } catch (e) {
      // If parsing fails, return original input
      return input;
    }
  };
  
  const extractLeetCodeUsername = (input) => {
    // If it's already just a username, return it
    if (!input.includes('/') && !input.includes('.')) {
      return input.trim();
    }
    
    // Handle full LeetCode URLs or variations
    try {
      // Remove trailing slash if present
      const cleaned = input.replace(/\/$/, '');
      
      // Handle leetcode.com URLs
      if (cleaned.includes('leetcode.com/')) {
        return cleaned.split('leetcode.com/')[1].split('/')[0];
      }
      
      // Handle direct usernames or other URL formats
      const parts = cleaned.split('/');
      return parts[parts.length - 1];
    } catch (e) {
      // If parsing fails, return original input
      return input;
    }
  };

  const handleGithubProfileExtract = async () => {
    if (!formData.github || !user) return
    
    setIsExtracting(true)
    
    try {
      // Get auth token
      const token = await user.getIdToken()
      
      // Extract GitHub username from URL
      const githubUrl = formData.github.trim()
      const githubUsername = githubUrl.endsWith('/') 
        ? githubUrl.split('/').slice(-2)[0] 
        : githubUrl.split('/').pop()
      
      console.log('Extracting GitHub profile for:', githubUsername)
      
      // Call backend API to extract GitHub profile with authentication
      await axios.post(
        `${API_BASE_URL}/api/candidate/link-profiles`, 
        { github_username: githubUsername },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      
      setNotification({
        type: 'success',
        message: 'GitHub profile linked successfully!'
      })
      
      // Refresh profile data after linking GitHub
      await fetchCandidateProfile()
      
    } catch (error) {
      console.error('Error extracting GitHub profile:', error)
      setNotification({
        type: 'error',
        message: error.response?.data?.message || 'Error linking GitHub profile. Please try again.'
      })
    } finally {
      setIsExtracting(false)
    }
  }

  const handleLeetcodeProfileExtract = async () => {
    if (!formData.leetcode || !user) return
    
    setIsExtracting(true)
    
    try {
      // Get auth token
      const token = await user.getIdToken()
      
      // Extract LeetCode username from URL
      const leetcodeUrl = formData.leetcode.trim()
      const leetcodeUsername = leetcodeUrl.endsWith('/') 
        ? leetcodeUrl.split('/').slice(-2)[0] 
        : leetcodeUrl.split('/').pop()
      
      console.log('Extracting LeetCode profile for:', leetcodeUsername)
      
      // Call backend API to extract LeetCode profile with authentication
      await axios.post(
        `${API_BASE_URL}/api/candidate/link-profiles`, 
        { leetcode_username: leetcodeUsername },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      
      setNotification({
        type: 'success',
        message: 'LeetCode profile linked successfully!'
      })
      
      // Refresh profile data after linking LeetCode
      await fetchCandidateProfile()
      
    } catch (error) {
      console.error('Error extracting LeetCode profile:', error)
      setNotification({
        type: 'error',
        message: error.response?.data?.message || 'Error linking LeetCode profile. Please try again.'
      })
    } finally {
      setIsExtracting(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      // Extract usernames from URLs or direct input
      const githubUsername = extractGitHubUsername(formData.github);
      const leetcodeUsername = extractLeetCodeUsername(formData.leetcode);
      
      // Initialize profile links object
      const profileLinks = {
        user_id: userId,
        resume_id: profileData?.resume?.id || null,
        github_username: githubUsername || null,
        leetcode_username: leetcodeUsername || null,
        skills: formData.skills
      }
      
      // Step 1: Upload resume if provided
      if (formData.resume instanceof File) {
        try {
          console.log('Uploading resume...')
          const resumeData = await uploadResume(formData.resume)
          console.log('Resume upload success:', resumeData)
          
          // Update the resume ID in profile links
          profileLinks.resume_id = resumeData.doc_id
        } catch (error) {
          console.error('Resume upload failed:', error)
          throw new Error('Resume upload failed. Please try again.')
        }
      }
      
      // Step 2: Link profiles
      console.log('Linking profiles with data:', profileLinks)
      const linkResponse = await linkProfiles(profileLinks)
      console.log('Profile linking success:', linkResponse)
      
      // Show success notification
      setNotification({
        type: 'success',
        message: 'Your profile has been successfully updated. Our AI is analyzing your data to match you with the best opportunities.'
      })
      
      // Refresh profile data after update
      setTimeout(() => {
        window.location.reload()
      }, 2000)
      
    } catch (error) {
      console.error("Error updating profile:", error)
      
      // Show error notification
      setNotification({
        type: 'error',
        message: error.response?.data?.detail || error.message || 'There was a problem updating your profile. Please try again.'
      })
    } finally {
      setIsLoading(false)
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
                    type="text"
                    value={formData.github}
                    onChange={(e) => setFormData({...formData, github: e.target.value})}
                    className="input pl-10"
                    placeholder="Username or https://github.com/username"
                  />
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Enter your GitHub username or full profile URL.
                </p>
              </div>
              
              <div>
                <label className="label flex items-center gap-2">
                  <Code2 className="h-5 w-5 text-primary" />
                  LeetCode Profile
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={formData.leetcode}
                    onChange={(e) => setFormData({...formData, leetcode: e.target.value})}
                    className="input pl-10"
                    placeholder="Username or https://leetcode.com/username"
                  />
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Enter your LeetCode username or full profile URL.
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