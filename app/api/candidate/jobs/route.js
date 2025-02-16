// app/api/candidate/jobs/route.js
import { NextResponse } from "next/server"

// Enhanced version of your existing jobs data
const jobs = [
  {
    id: 1,
    title: "Frontend Developer",
    company: "TechCorp",
    location: "San Francisco, CA",
    description: "Exciting opportunity for a skilled frontend developer",
    matchScore: 85,
    skills: ["React", "TypeScript", "CSS"],
    postedDate: "2024-02-01",
    applied: false
  },
  {
    id: 2,
    title: "Backend Engineer",
    company: "DataSystems",
    location: "New York, NY",
    description: "Join our team of backend experts",
    matchScore: 92,
    skills: ["Node.js", "Python", "PostgreSQL"],
    postedDate: "2024-02-05",
    applied: false
  },
  {
    id: 3,
    title: "Full Stack Developer",
    company: "WebSolutions",
    location: "Remote",
    description: "Looking for a versatile developer to join our team",
    matchScore: 78,
    skills: ["JavaScript", "React", "MongoDB"],
    postedDate: "2024-02-10",
    applied: false
  }
]

export async function GET(request) {
  const { searchParams } = new URL(request.url)
  const search = searchParams.get('search')?.toLowerCase()
  const filter = searchParams.get('filter')
  
  let filteredJobs = [...jobs]
  
  // Apply search filter
  if (search) {
    filteredJobs = filteredJobs.filter(job => 
      job.title.toLowerCase().includes(search) ||
      job.company.toLowerCase().includes(search) ||
      job.description.toLowerCase().includes(search)
    )
  }
  
  // Apply status filter
  if (filter === 'applied') {
    filteredJobs = filteredJobs.filter(job => job.applied)
  } else if (filter === 'matched') {
    filteredJobs = filteredJobs.filter(job => job.matchScore >= 80)
  }
  
  return NextResponse.json(filteredJobs)
}