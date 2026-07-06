// app/api/candidate/apply/route.js
import { NextResponse } from "next/server"

// Simulated applications store
const applications = new Set()

export async function POST(request) {
  try {
    const { jobId } = await request.json()
    
    // Check if already applied
    if (applications.has(jobId)) {
      return NextResponse.json(
        { error: "Already applied to this job" },
        { status: 400 }
      )
    }

    // Store the application
    applications.add(jobId)

    return NextResponse.json({ 
      success: true, 
      message: "Application submitted successfully" 
    })
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to submit application" },
      { status: 400 }
    )
  }
}

export async function GET() {
  return NextResponse.json(Array.from(applications))
}