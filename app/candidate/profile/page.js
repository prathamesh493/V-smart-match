"use client"

import { useState, useEffect } from "react"
import Header from "../../../components/Header"
import { Upload, Github, Code2, CheckCircle2, Brain, Trophy } from 'lucide-react'
import Notification from "../../../components/Notification"
import { ProfileCompletion } from "../../../components/ProfileCompletion"
import axios from "axios"
import { useAuth } from "../../../lib/useAuth"
import { useRouter } from 'next/navigation'

// Get API base URL from environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function CandidateProfile() {
  const { user, loading: authLoading } = useAuth() // Use authentication hook
  const router = useRouter() // Add router for redirects
  const [formData, setFormData] = useState({
    resume: null,
    github: "",
    leetcode: "",
    skills: [],
    experience: [],
    education: []
  })
  const [userId, setUserId] = useState(null)
  const [newSkill, setNewSkill] = useState("")
  const [fileName, setFileName] = useState("") // For displaying filename
  const [notification, setNotification] = useState(null) // For notifications
  const [isLoading, setIsLoading] = useState(false) // Loading state
  const [apiConnectionError, setApiConnectionError] = useState(false) // API connection error state
  const [profileData, setProfileData] = useState(null) // Profile data from backend
  const [isExtracting, setIsExtracting] = useState(false) // Extracting state
  const [uploadProgress, setUploadProgress] = useState(0) // For tracking upload progress

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
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        setNotification({
          type: 'error',
          message: 'File size exceeds 5MB limit'
        })
        e.target.value = null // Reset file input
        return
      }
      
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
      setUploadProgress(0);
      
      // Get auth token
      const token = await user.getIdToken();
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(
        `${API_BASE_URL}/api/resume/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percentCompleted);
          }
        }
      );
      
      console.log("Resume upload response:", response.data);
      setNotification({
        type: 'success',
        message: 'Resume uploaded successfully!'
      });
      
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
      setUploadProgress(0);
    }
  }

  const handleGitHubInputChange = (e) => {
    setFormData({ ...formData, github: e.target.value });
  }

  const handleLeetCodeInputChange = (e) => {
    setFormData({ ...formData, leetcode: e.target.value });
  }

  // Helper functions to extract usernames from URLs
  const extractGitHubUsername = (input) => {
    if (!input) return "";
    
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
    if (!input) return "";
    
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
    if (!formData.github || !user) {
      setNotification({
        type: 'error',
        message: 'Please enter a GitHub username'
      });
      return;
    }
    
    setIsExtracting(true);
    
    try {
      // Get auth token
      const token = await user.getIdToken();
      
      // Extract GitHub username from URL or use as is
      const githubUsername = extractGitHubUsername(formData.github);
      
      console.log('Extracting GitHub profile for:', githubUsername);
      
      // Call the correct GitHub API endpoint
      const response = await axios.get(
        `${API_BASE_URL}/api/github/${githubUsername}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      setNotification({
        type: 'success',
        message: 'GitHub profile linked successfully!'
      });
      
      // Refresh profile data after linking GitHub
      await fetchCandidateProfile();
      
    } catch (error) {
      console.error('Error extracting GitHub profile:', error);
      setNotification({
        type: 'error',
        message: error.response?.data?.message || 'Error linking GitHub profile. Please try again.'
      });
    } finally {
      setIsExtracting(false);
    }
  };

  const handleLeetcodeProfileExtract = async () => {
    if (!formData.leetcode || !user) {
      setNotification({
        type: 'error',
        message: 'Please enter a LeetCode username'
      });
      return;
    }
    
    setIsExtracting(true);
    
    try {
      // Get auth token
      const token = await user.getIdToken();
      
      // Extract LeetCode username from URL or use as is
      const leetcodeUsername = extractLeetCodeUsername(formData.leetcode);
      
      console.log('Extracting LeetCode profile for:', leetcodeUsername);
      
      // Call backend API to extract LeetCode profile with authentication
      const response = await axios.post(
        `${API_BASE_URL}/api/candidate/link-profiles`, 
        { 
          leetcode_username: leetcodeUsername 
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      setNotification({
        type: 'success',
        message: 'LeetCode profile linked successfully!'
      });
      
      // Refresh profile data after linking LeetCode
      await fetchCandidateProfile();
      
    } catch (error) {
      console.error('Error extracting LeetCode profile:', error);
      setNotification({
        type: 'error',
        message: error.response?.data?.message || 'Error linking LeetCode profile. Please try again.'
      });
    } finally {
      setIsExtracting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // Extract usernames from URLs or direct input
      const githubUsername = extractGitHubUsername(formData.github);
      const leetcodeUsername = extractLeetCodeUsername(formData.leetcode);
      
      // Initialize profile links object
      let resumeId = profileData?.resume?.id || null;
      
      // Step 1: Upload resume if provided
      if (formData.resume instanceof File) {
        try {
          console.log('Uploading resume...');
          const resumeData = await uploadResume(formData.resume);
          if (resumeData) {
            console.log('Resume upload success:', resumeData);
            resumeId = resumeData.doc_id;
          }
        } catch (error) {
          console.error('Resume upload failed:', error);
          throw new Error('Resume upload failed. Please try again.');
        }
      }
      
      // Step 2: Link profiles
      if (githubUsername || leetcodeUsername || resumeId) {
        try {
          // Get auth token
          const token = await user.getIdToken();
          
          const linkResponse = await axios.post(
            `${API_BASE_URL}/api/candidate/link-profiles`,
            {
              github_username: githubUsername || null,
              leetcode_username: leetcodeUsername || null,
              resume_id: resumeId || null
            },
            {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            }
          );
          
          console.log('Profile linking success:', linkResponse.data);
        } catch (error) {
          console.error('Error linking profiles:', error);
          throw new Error('Error linking profiles. Please try again.');
        }
      }
      
      // Show success notification
      setNotification({
        type: 'success',
        message: 'Your profile has been successfully updated. Our AI is analyzing your data to match you with the best opportunities.'
      });
      
      // Refresh profile data after update
      fetchCandidateProfile();
      
      // Redirect to candidate profile report after successful update
      setTimeout(() => {
        router.push('/candidate/report');
      }, 1500); // Small delay to allow the user to see the success notification
      
    } catch (error) {
      console.error("Error updating profile:", error);
      
      // Show error notification
      setNotification({
        type: 'error',
        message: error.response?.data?.detail || error.message || 'There was a problem updating your profile. Please try again.'
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Helper to close the notification
  const closeNotification = () => {
    setNotification(null);
  };

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
            {apiConnectionError && (
              <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4 mb-6">
                <p className="font-medium">Can't connect to the API server</p>
                <p className="text-sm mt-1">Please check that the backend is running and accessible.</p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Resume Upload */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Upload className="h-5 w-5 text-primary" />
                  Resume Upload
                </label>
                <div className="relative">
                  <input
                    type="file"
                    id="resume"
                    name="resume"
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx"
                    className="sr-only"
                  />
                  <label
                    htmlFor="resume"
                    className="relative flex items-center gap-3 bg-gray-50 hover:bg-gray-100 transition-colors rounded-md p-3 cursor-pointer border border-gray-300"
                  >
                    <Upload className="h-5 w-5 text-gray-500" />
                    <span className="text-gray-500">
                      {fileName ? fileName : "PDF, DOC, or DOCX (Max 5MB)"}
                    </span>
                  </label>
                </div>
                {uploadProgress > 0 && uploadProgress < 100 && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className="bg-blue-600 h-2.5 rounded-full"
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Uploading: {uploadProgress}%</p>
                  </div>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Our AI will extract your skills, experience, and education automatically
                </p>
              </div>

              {/* GitHub Profile */}
              <div className="col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Github className="h-5 w-5 text-primary" />
                  GitHub Profile
                </label>
                <div className="flex space-x-2">
                  <div className="flex-grow">
                    <input
                      type="text"
                      id="github"
                      name="github"
                      placeholder="Username or URL"
                      value={formData.github}
                      onChange={handleGitHubInputChange}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleGithubProfileExtract}
                    disabled={isExtracting || !formData.github}
                    className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isExtracting ? "Linking..." : "Link"}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Connect your GitHub to showcase your projects and contributions
                </p>
              </div>

              {/* LeetCode Profile */}
              <div className="col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Code2 className="h-5 w-5 text-primary" />
                  LeetCode Profile
                </label>
                <div className="flex space-x-2">
                  <div className="flex-grow">
                    <input
                      type="text"
                      id="leetcode"
                      name="leetcode"
                      placeholder="Username or URL"
                      value={formData.leetcode}
                      onChange={handleLeetCodeInputChange}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleLeetcodeProfileExtract}
                    disabled={isExtracting || !formData.leetcode}
                    className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isExtracting ? "Linking..." : "Link"}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Connect your LeetCode profile to highlight your coding skills
                </p>
              </div>

              {/* Skills */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-primary" />
                  Skills
                </label>
                <div className="flex space-x-2 mb-2">
                  <input
                    type="text"
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    placeholder="Add a skill (e.g., React, Python, AWS)"
                    className="flex-grow border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddSkill();
                      }
                    }}
                  />
                  <button
                    type="button"
                    onClick={handleAddSkill}
                    className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md text-sm font-medium"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {formData.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                    >
                      {skill}
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(skill)}
                        className="ml-1 text-blue-500 hover:text-blue-700"
                      >
                        &times;
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Submit Button */}
              <div className="md:col-span-2 mt-6">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-3 px-4 rounded-md text-base font-medium shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Updating Profile...' : 'Update Profile'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </main>
    </div>
  )
}