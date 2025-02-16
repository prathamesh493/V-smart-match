// app/api/job-suggestions/route.js
import { NextResponse } from 'next/server'

// This is our dummy database of job titles
const jobTitles = [
  { title: "Software Engineer" },
  { title: "Senior Software Engineer" },
  { title: "Full Stack Developer" },
  { title: "Frontend Developer" },
  { title: "Backend Developer" },
  { title: "DevOps Engineer" },
  { title: "Data Scientist" },
  { title: "Machine Learning Engineer" },
  { title: "UI/UX Designer" },
  { title: "Product Manager" },
  { title: "Project Manager" },
  { title: "QA Engineer" },
  { title: "Technical Writer" },
  { title: "Systems Administrator" },
  { title: "Database Administrator" },
  { title: "Cloud Architect" },
  { title: "Security Engineer" },
  { title: "Network Engineer" },
  { title: "Mobile Developer" },
  { title: "Android Developer" },
  { title: "iOS Developer" },
  { title: "Game Developer" },
  { title: "Blockchain Developer" },
  { title: "AR/VR Developer" },
]

export async function GET(request) {
  const { searchParams } = new URL(request.url)
  const query = searchParams.get('query') || ''
  
  // Filter job titles that include the query (case-insensitive)
  const filteredJobs = jobTitles.filter(job => 
    job.title.toLowerCase().includes(query.toLowerCase())
  )
  
  // Simulate a slight delay for real-world API behavior
  await new Promise(resolve => setTimeout(resolve, 200))
  
  return NextResponse.json(filteredJobs.slice(0, 10))  // Limit to 10 results
}