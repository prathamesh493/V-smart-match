// app/api/candidate/report/route.js
import { db } from '@/firebase/config';
import { doc, getDoc, collection, getDocs } from 'firebase/firestore';
import { NextResponse } from 'next/server';

export async function GET(request) {
  try {
    // Get the user ID from the URL query parameters
    const { searchParams } = new URL(request.url);
    const uid = searchParams.get('uid');
    
    if (!uid) {
      return new Response(JSON.stringify({ 
        error: 'Authentication required',
        redirectTo: '/signin' 
      }), {
        status: 401,
        headers: {
          'Content-Type': 'application/json',
        }
      });
    }
    
    // Check if user profile is completed
    const userDocRef = doc(db, "candidates", uid);
    const userSnapshot = await getDoc(userDocRef);
    
    if (!userSnapshot.exists() || !isProfileComplete(userSnapshot.data())) {
      return new Response(JSON.stringify({
        error: 'Profile is incomplete',
        message: 'Please complete your profile to view your report',
        redirectTo: '/candidate/profile',
        profileStatus: 'incomplete'
      }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
        }
      });
    }
    
    // Fetch data from different sources in Firestore
    const userData = userSnapshot.data();
    
    // Get resume data
    const resumeDocRef = doc(db, "resumes", uid);
    const resumeSnapshot = await getDoc(resumeDocRef);
    const resumeData = resumeSnapshot.exists() ? resumeSnapshot.data() : {};
    
    // Get GitHub profile data
    const githubDocRef = doc(db, "github_profiles", uid);
    const githubSnapshot = await getDoc(githubDocRef);
    const githubData = githubSnapshot.exists() ? githubSnapshot.data() : {};
    
    // Get LeetCode profile data
    const leetcodeDocRef = doc(db, "leetcode_profiles", uid);
    const leetcodeSnapshot = await getDoc(leetcodeDocRef);
    const leetcodeData = leetcodeSnapshot.exists() ? leetcodeSnapshot.data() : {};
    
    // Get skill assessments if any
    const skillAssessmentsRef = collection(db, "candidates", uid, "skill_assessments");
    const skillAssessmentsSnapshot = await getDocs(skillAssessmentsRef);
    const skillAssessments = [];
    skillAssessmentsSnapshot.forEach(doc => {
      skillAssessments.push({
        id: doc.id,
        ...doc.data()
      });
    });
    
    // Aggregate all data
    const reportData = {
      profile: userData,
      resume: resumeData,
      github: githubData,
      leetcode: leetcodeData,
      skillAssessments: skillAssessments,
      profileStatus: 'complete'
    };
    
    return new Response(JSON.stringify(reportData), {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
  } catch (error) {
    console.error('Error fetching candidate report:', error);
    
    // Return error response
    return new Response(JSON.stringify({ error: 'Failed to fetch report data' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
      }
    });
  }
}

// Helper function to check if user profile is complete
function isProfileComplete(profileData) {
  if (!profileData) return false;
  
  // Define required fields for a complete profile
  const requiredFields = [
    'fullName', 
    'email'
  ];
  
  return requiredFields.every(field => !!profileData[field]);
}