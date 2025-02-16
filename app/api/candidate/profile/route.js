// app/api/candidate/profile/route.js
import { NextResponse } from "next/server"

// Simulated profile data store
let profileData = {
  resume: null,
  github: "https://github.com/johndoe",
  leetcode: "https://leetcode.com/johndoe",
  skills: ["JavaScript", "React", "Node.js"],
  experience: [
    {
      title: "Frontend Developer",
      company: "TechCorp",
      startDate: "2022-01",
      endDate: "Present",
      description: "Developing modern web applications"
    }
  ],
  education: [
    {
      degree: "BS Computer Science",
      school: "Tech University",
      graduationYear: "2021"
    }
  ]
}

export async function GET() {
  return NextResponse.json(profileData)
}

export async function PUT(request) {
  try {
    const newData = await request.json()
    // In a real application, validate the data here
    profileData = { ...profileData, ...newData }
    return NextResponse.json(profileData)
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to update profile" },
      { status: 400 }
    )
  }
}