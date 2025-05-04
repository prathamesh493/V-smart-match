// app/api/candidate/profile/route.js
import { NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://mj.local:8000";

export async function GET(request) {
  try {
    // Get user session for authentication
    const session = await getServerSession();
    
    if (!session || !session.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    
    const userId = session.user.id;
    
    // Make request to backend API
    const response = await fetch(`${API_BASE_URL}/candidate/profile/${userId}`, {
      headers: {
        "Authorization": `Bearer ${session.accessToken}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`Backend API error: ${response.statusText}`);
    }
    
    const profileData = await response.json();
    return NextResponse.json(profileData);
  } catch (error) {
    console.error("Error fetching profile:", error);
    return NextResponse.json(
      { error: "Failed to fetch profile data" },
      { status: 500 }
    );
  }
}

export async function PUT(request) {
  try {
    // Get user session for authentication
    const session = await getServerSession();
    
    if (!session || !session.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    
    const userId = session.user.id;
    const profileData = await request.json();
    
    // Make request to backend API
    const response = await fetch(`${API_BASE_URL}/candidate/profile/${userId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session.accessToken}`
      },
      body: JSON.stringify(profileData)
    });
    
    if (!response.ok) {
      throw new Error(`Backend API error: ${response.statusText}`);
    }
    
    const updatedProfile = await response.json();
    return NextResponse.json(updatedProfile);
  } catch (error) {
    console.error("Error updating profile:", error);
    return NextResponse.json(
      { error: "Failed to update profile data" },
      { status: 500 }
    );
  }
}