// app/api/job-suggestions/route.js
import { NextResponse } from 'next/server'
import axios from 'axios'

// Get API base URL from environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://mj.local:8000'

// Fallback job titles in case the API is not available
const fallbackJobTitles = [
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
  const userId = searchParams.get('userId') // Optional userId for personalized suggestions
  
  try {
    // Try to get job suggestions from backend API
    const response = await axios.get(`${API_BASE_URL}/job-description/suggestions`, {
      params: {
        query,
        user_id: userId // Pass userId if available for personalized suggestions
      },
      timeout: 3000 // Set timeout to prevent long waiting
    })
    
    return NextResponse.json(response.data)
  } catch (error) {
    console.warn('Error fetching job suggestions from API, using fallback data:', error)
    
    // Fallback to local suggestions if API fails
    const filteredJobs = fallbackJobTitles.filter(job => 
      job.title.toLowerCase().includes(query.toLowerCase())
    )
    
    return NextResponse.json(filteredJobs.slice(0, 10))  // Limit to 10 results
  }
}