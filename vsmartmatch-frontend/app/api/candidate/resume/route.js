// app/api/candidate/resume/route.js
import { NextResponse } from "next/server"
import { auth } from "@/firebase/config"

export async function POST(request) {
  try {
    const formData = await request.formData()
    const file = formData.get('resume')

    if (!file) {
      return NextResponse.json(
        { error: "No file uploaded" },
        { status: 400 }
      )
    }

    // In a real application, you would:
    // 1. Validate the file type
    // 2. Check file size
    // 3. Upload to storage (e.g., S3)
    // 4. Store the reference in the database

    return NextResponse.json({ 
      success: true,
      message: "Resume uploaded successfully",
      fileUrl: "https://example.com/resumes/filename.pdf" // Simulated URL
    })
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to upload resume" },
      { status: 400 }
    )
  }
}

export async function GET(request) {
  try {
    // Get the user ID from query parameters
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get("userId");
    
    if (!userId) {
      return NextResponse.json(
        { error: "User ID is required" },
        { status: 400 }
      );
    }

    // Fetch resume data from backend without authentication
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const response = await fetch(`${backendUrl}/resume/${userId}`);

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || "Failed to fetch resume" },
        { status: response.status }
      );
    }

    const resumeData = await response.json();
    return NextResponse.json(resumeData);
    
  } catch (error) {
    console.error("Error fetching resume:", error);
    return NextResponse.json(
      { error: "Failed to fetch resume data" },
      { status: 500 }
    );
  }
}