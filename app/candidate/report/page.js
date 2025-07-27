"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/useAuth"
import { FileText, Github, Code, GraduationCap, Award, Briefcase, ExternalLink, User } from "lucide-react"
import Header from "@/components/Header"
import Link from "next/link"
import ReactMarkdown from 'react-markdown'

export default function CandidateReport() {
  const [reportData, setReportData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()

  useEffect(() => {
    // Redirect if not authenticated
    if (!authLoading && !user) {
      router.push("/signin")
      return
    }

    const fetchReport = async () => {
      try {
        // Use a simple query parameter approach for authentication
        const response = await fetch(`/api/candidate/report?uid=${user.uid}`)
        const data = await response.json()

        if (data.error && data.redirectTo) {
          router.push(data.redirectTo)
          return
        }

        setReportData(data)
      } catch (err) {
        setError("Failed to fetch report data")
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    if (user) {
      fetchReport()
    }
  }, [user, authLoading, router])

  if (loading || authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
        <Header />
        <div className="container mx-auto px-4 py-16">
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
        <Header />
        <div className="container mx-auto px-4 py-16">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-white">
            <h2 className="text-2xl font-bold mb-4">Error</h2>
            <p>{error}</p>
            <button
              onClick={() => router.push("/candidate/profile")}
              className="mt-4 bg-white text-[#c6269e] px-4 py-2 rounded-lg font-medium"
            >
              Complete Your Profile
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!reportData) {
    return null
  }

  const { profile, resume, github, leetcode } = reportData

  // Helper function to extract sections from resume content
  const extractSection = (content, sectionHeader) => {
    if (!content) return ""
    
    const lines = content.split('\n')
    let sectionContent = []
    let inSection = false
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      
      // Check if we've reached the target section
      if (line.startsWith(`## ${sectionHeader}`)) {
        inSection = true
        sectionContent.push(line) // Include the header
        continue
      }
      
      // Check if we've reached another section (stop capturing)
      if (inSection && (line.startsWith('## ') || line.startsWith('# ')) && !line.startsWith(`## ${sectionHeader}`)) {
        break
      }
      
      // Add lines while in the target section
      if (inSection) {
        sectionContent.push(line)
      }
    }
    
    return sectionContent.join('\n')
  }

  // Extract sections from resume content
  const skillsContent = extractSection(resume?.extracted_content, 'Skills')
  const educationContent = extractSection(resume?.extracted_content, 'Education')
  const experienceContent = extractSection(resume?.extracted_content, 'Work Experience')

  // Extract GitHub languages
  const githubLanguages = github?.insights_data?.top_languages || {}
  const languageEntries = Object.entries(githubLanguages)
    .map(([name, bytes]) => ({
      name,
      percentage: Math.round((bytes / Object.values(githubLanguages).reduce((a, b) => a + b, 0)) * 100),
    }))
    .sort((a, b) => b.percentage - a.percentage)

  // Extract GitHub projects
  const githubProjects = github?.insights_data?.personal_projects || []

  // Extract LeetCode stats
  const leetcodeStats =
    leetcode?.profile_data?.userProblemsSolved?.matchedUser?.submitStatsGlobal?.acSubmissionNum || []
  const leetcodeSkillStats = leetcode?.profile_data?.skillStats?.matchedUser?.tagProblemCounts || {}

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <h1 className="text-4xl md:text-5xl font-bold text-white text-center mb-8 animate-fade-in-up">
          Your Professional Profile
        </h1>
        <p className="text-xl text-white/90 text-center mb-12 animate-fade-in-up animation-delay-200">
          This comprehensive report showcases your skills, experience, and coding abilities.
        </p>

        {/* Basic Profile */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
          <div className="lg:col-span-1">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 text-white h-full">
              <div className="flex items-center mb-6">
                <div className="bg-white/20 rounded-full p-3 mr-4">
                  <User className="h-8 w-8" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">{profile?.fullName || "Your Name"}</h2>
                  <p className="text-white/80">{profile?.email || "email@example.com"}</p>
                </div>
              </div>

              <div className="space-y-4">
                {profile?.github_username && (
                  <div className="flex items-center">
                    <Github className="h-5 w-5 mr-3 text-white/70" />
                    <span>{profile.github_username}</span>
                  </div>
                )}

                {profile?.leetcode_username && (
                  <div className="flex items-center">
                    <Code className="h-5 w-5 mr-3 text-white/70" />
                    <span>{profile.leetcode_username}</span>
                  </div>
                )}

                {resume?.metadata?.file_name && (
                  <div className="flex items-center">
                    <FileText className="h-5 w-5 mr-3 text-white/70" />
                    <span>Resume Uploaded</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 text-white h-full">
              <h2 className="text-2xl font-bold mb-4 flex items-center">
                <Award className="h-6 w-6 mr-2" />
                Skills & Expertise
              </h2>

              {skillsContent ? (
                <div className="prose prose-sm max-w-none text-white prose-headings:text-white prose-strong:text-white prose-ul:text-white prose-li:text-white">
                  <ReactMarkdown>{skillsContent}</ReactMarkdown>
                </div>
              ) : (
                <p className="text-white/60 italic">
                  No skills section found. Update your resume to showcase your abilities.
                </p>
              )}

              {github?.insights_data?.tech_preferences?.from_readme?.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-2">Technologies (from GitHub)</h3>
                  <div className="flex flex-wrap gap-2">
                    {github.insights_data.tech_preferences.from_readme.map((tech, index) => (
                      <span key={index} className="bg-purple-500/30 px-3 py-1 rounded-full text-sm font-medium">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Resume Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
          {/* Education */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 text-white">
            <h2 className="text-2xl font-bold mb-6 flex items-center">
              <GraduationCap className="h-6 w-6 mr-2" />
              Education
            </h2>

            {educationContent ? (
              <div className="prose prose-sm max-w-none text-white prose-headings:text-white prose-strong:text-white prose-ul:text-white prose-li:text-white max-h-80 overflow-y-auto">
                <ReactMarkdown>{educationContent}</ReactMarkdown>
              </div>
            ) : (
              <p className="text-white/60 italic">
                No education section found. Update your resume to add your educational background.
              </p>
            )}
          </div>

          {/* Experience */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 text-white">
            <h2 className="text-2xl font-bold mb-6 flex items-center">
              <Briefcase className="h-6 w-6 mr-2" />
              Experience
            </h2>

            {experienceContent ? (
              <div className="prose prose-sm max-w-none text-white prose-headings:text-white prose-strong:text-white prose-ul:text-white prose-li:text-white max-h-80 overflow-y-auto">
                <ReactMarkdown>{experienceContent}</ReactMarkdown>
              </div>
            ) : (
              <p className="text-white/60 italic">
                No work experience section found. Update your resume to add your work history.
              </p>
            )}
          </div>
        </div>

        {/* GitHub Section */}
        <div className="mb-12">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 text-white">
            <h2 className="text-2xl font-bold mb-6 flex items-center">
              <Github className="h-6 w-6 mr-2" />
              GitHub Profile
            </h2>

            {github ? (
              <div className="space-y-8">
                {/* Languages */}
                <div>
                  <h3 className="text-xl font-semibold mb-4">Programming Languages</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {languageEntries.slice(0, 6).map((lang, index) => (
                      <div key={index} className="bg-white/5 rounded-lg p-3">
                        <div className="flex justify-between mb-1">
                          <span>{lang.name}</span>
                          <span>{lang.percentage}%</span>
                        </div>
                        <div className="w-full bg-white/10 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-pink-500 to-purple-500 h-2 rounded-full"
                            style={{ width: `${lang.percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Projects */}
                <div>
                  <h3 className="text-xl font-semibold mb-4">Top Projects</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {githubProjects.slice(0, 4).map((project, index) => (
                      <div key={index} className="bg-white/5 rounded-lg p-4">
                        <h4 className="font-semibold text-lg mb-1">{project.name}</h4>
                        <p className="text-white/70 text-sm mb-3 line-clamp-2">
                          {project.description || "No description available"}
                        </p>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-white/60">{project.language || "N/A"}</span>
                          <a
                            href={project.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm flex items-center text-purple-300 hover:text-white transition-colors"
                          >
                            View <ExternalLink className="h-3 w-3 ml-1" />
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Activity */}
                <div>
                  <h3 className="text-xl font-semibold mb-2">Recent Activity</h3>
                  <div className="bg-white/5 rounded-lg p-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <p className="text-3xl font-bold text-purple-300">
                          {github.insights_data?.contribution_activity?.last_30_days || 0}
                        </p>
                        <p className="text-white/60 text-sm">Commits (Last 30 days)</p>
                      </div>
                      <div className="text-center">
                        <p className="text-3xl font-bold text-purple-300">
                          {github.insights_data?.contribution_activity?.last_90_days || 0}
                        </p>
                        <p className="text-white/60 text-sm">Commits (Last 90 days)</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <Github className="h-16 w-16 mx-auto mb-4 text-white/40" />
                <p className="text-white/60 mb-4">No GitHub profile connected</p>
                <Link
                  href="/candidate/profile"
                  className="inline-block bg-white/20 hover:bg-white/30 transition-colors px-4 py-2 rounded-lg text-white"
                >
                  Connect GitHub
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* LeetCode Section */}
        <div className="mb-12">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 text-white">
            <h2 className="text-2xl font-bold mb-6 flex items-center">
              <Code className="h-6 w-6 mr-2" />
              LeetCode Profile
            </h2>

            {leetcode ? (
              <div className="space-y-8">
                {/* Problem Solving Stats */}
                <div>
                  <h3 className="text-xl font-semibold mb-4">Problem Solving</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {leetcodeStats.map((stat, index) => {
                      if (stat.difficulty === "All") return null

                      let bgColor = "bg-green-500/30"
                      if (stat.difficulty === "Medium") bgColor = "bg-yellow-500/30"
                      if (stat.difficulty === "Hard") bgColor = "bg-red-500/30"

                      return (
                        <div key={index} className={`${bgColor} rounded-lg p-4 text-center`}>
                          <h4 className="font-medium mb-2">{stat.difficulty}</h4>
                          <p className="text-3xl font-bold">{stat.count}</p>
                          <p className="text-white/60 text-sm">Problems Solved</p>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Skill Tags */}
                <div>
                  <h3 className="text-xl font-semibold mb-4">Top Skills</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {leetcodeSkillStats.fundamental && (
                      <div>
                        <h4 className="font-medium mb-3 text-purple-300">Fundamental</h4>
                        <div className="flex flex-wrap gap-2">
                          {leetcodeSkillStats.fundamental.slice(0, 8).map((skill, index) => (
                            <span key={index} className="bg-white/20 px-3 py-1 rounded-full text-sm">
                              {skill.tagName} ({skill.problemsSolved})
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {leetcodeSkillStats.intermediate && (
                      <div>
                        <h4 className="font-medium mb-3 text-purple-300">Intermediate</h4>
                        <div className="flex flex-wrap gap-2">
                          {leetcodeSkillStats.intermediate.slice(0, 8).map((skill, index) => (
                            <span key={index} className="bg-white/20 px-3 py-1 rounded-full text-sm">
                              {skill.tagName} ({skill.problemsSolved})
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Languages */}
                <div>
                  <h3 className="text-xl font-semibold mb-4">Languages Used</h3>
                  {leetcode?.profile_data?.languageStats?.matchedUser?.languageProblemCount ? (
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                      {leetcode.profile_data.languageStats.matchedUser.languageProblemCount.map((lang, index) => (
                        <div key={index} className="bg-white/5 rounded-lg p-3 text-center">
                          <p className="font-medium">{lang.languageName}</p>
                          <p className="text-2xl font-bold text-purple-300">{lang.problemsSolved}</p>
                          <p className="text-white/60 text-sm">Problems</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-white/80">No LeetCode language data available.</p>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <Code className="h-16 w-16 mx-auto mb-4 text-white/40" />
                <p className="text-white/60 mb-4">No LeetCode profile connected</p>
                <Link
                  href="/candidate/profile"
                  className="inline-block bg-white/20 hover:bg-white/30 transition-colors px-4 py-2 rounded-lg text-white"
                >
                  Connect LeetCode
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Resume Content */}
        <div className="mb-12">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 text-white">
            <h2 className="text-2xl font-bold mb-6 flex items-center">
              <FileText className="h-6 w-6 mr-2" />
              Resume Content
            </h2>

            {resume?.extracted_content ? (
              <div className="bg-white/5 rounded-lg p-6 overflow-auto max-h-96">
                <div className="prose prose-sm max-w-none text-white prose-headings:text-white prose-strong:text-white prose-ul:text-white prose-li:text-white prose-p:text-white prose-a:text-purple-300 hover:prose-a:text-purple-200">
                  <ReactMarkdown>{resume.extracted_content}</ReactMarkdown>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText className="h-16 w-16 mx-auto mb-4 text-white/40" />
                <p className="text-white/60 mb-4">No resume content available</p>
                <Link
                  href="/candidate/profile"
                  className="inline-block bg-white/20 hover:bg-white/30 transition-colors px-4 py-2 rounded-lg text-white"
                >
                  Upload Resume
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-center">
          <Link
            href="/candidate/profile"
            className="bg-white text-[#c6269e] px-6 py-3 rounded-lg font-semibold hover:bg-white/90 transition-colors"
          >
            Update Your Profile
          </Link>
        </div>
      </main>
    </div>
  )
}
