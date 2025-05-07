// app/api/candidate/report/route.js
import { db } from '@/firebase/config';
import { doc, getDoc, collection, getDocs, query, where, limit } from 'firebase/firestore';
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
    
    // Check if user profile exists
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
    
    // Get the user data
    const userData = userSnapshot.data();
    
    // Initialize the report data with the user profile
    const reportData = {
      profile: userData,
      resume: {},
      github: {},
      leetcode: {},
      skillAssessments: [],
      profileStatus: 'complete'
    };
    
    // Fetch all related data in parallel to improve performance
    const fetchPromises = [];
    
    // Get resume data if the user has a resume
    if (userData.has_resume) {
      fetchPromises.push(
        (async () => {
          try {
            // If we have a latest_resume_id, use that directly
            if (userData.latest_resume_id) {
              const resumeDocRef = doc(db, "resumes", userData.latest_resume_id);
              const resumeSnapshot = await getDoc(resumeDocRef);
              if (resumeSnapshot.exists()) {
                reportData.resume = resumeSnapshot.data();
                return;
              }
            }
            
            // Fallback to query if direct lookup fails
            const resumeQuery = query(
              collection(db, "resumes"),
              where("user_id", "==", uid),
              limit(1)
            );
            const resumeSnapshot = await getDocs(resumeQuery);
            
            if (!resumeSnapshot.empty) {
              reportData.resume = resumeSnapshot.docs[0].data();
            }
          } catch (error) {
            console.error('Error fetching resume data:', error);
          }
        })()
      );
    }
    
    // Get GitHub profile data if the user has a GitHub profile
    if (userData.has_github_profile) {
      fetchPromises.push(
        (async () => {
          try {
            let githubData = null;
            
            // Try fetching by github_profile_id first if available
            if (userData.github_profile_id) {
              const githubDocRef = doc(db, "github_profiles", userData.github_profile_id);
              const githubSnapshot = await getDoc(githubDocRef);
              if (githubSnapshot.exists()) {
                githubData = githubSnapshot.data();
              }
            }
            
            // If not found by ID and username is available, try by username
            if (!githubData && userData.github_username) {
              const githubUsernameRef = doc(db, "github_profiles", userData.github_username);
              const githubUsernameSnapshot = await getDoc(githubUsernameRef);
              if (githubUsernameSnapshot.exists()) {
                githubData = githubUsernameSnapshot.data();
              }
            }
            
            // Fallback to user ID lookup if still not found
            if (!githubData) {
              const githubDocRef = doc(db, "github_profiles", uid);
              const githubSnapshot = await getDoc(githubDocRef);
              if (githubSnapshot.exists()) {
                githubData = githubSnapshot.data();
              }
            }
            
            // If we found data, ensure it's properly serialized
            if (githubData) {
              reportData.github = JSON.parse(JSON.stringify(githubData));
            }
          } catch (error) {
            console.error('Error fetching GitHub profile data:', error);
          }
        })()
      );
    }
    
    // Get LeetCode profile data if the user has a LeetCode profile
    if (userData.has_leetcode_profile && userData.leetcode_username) {
      fetchPromises.push(
        (async () => {
          try {
            // Use leetcode_username for fetching data, as per the requirement
            const leetcodeDocRef = doc(db, "leetcode_profiles", userData.leetcode_username);
            const leetcodeSnapshot = await getDoc(leetcodeDocRef);
            
            if (leetcodeSnapshot.exists()) {
              // Get the raw data
              const leetcodeData = leetcodeSnapshot.data();
              
              // Ensure all nested objects are properly serialized (not [Object])
              reportData.leetcode = JSON.parse(JSON.stringify(leetcodeData));
            } else {
              console.log(`No LeetCode profile found for username: ${userData.leetcode_username}`);
              // Fallback to user ID if username fetch fails
              const fallbackDocRef = doc(db, "leetcode_profiles", uid);
              const fallbackSnapshot = await getDoc(fallbackDocRef);
              
              if (fallbackSnapshot.exists()) {
                const leetcodeData = fallbackSnapshot.data();
                reportData.leetcode = JSON.parse(JSON.stringify(leetcodeData));
              }
            }
          } catch (error) {
            console.error('Error fetching LeetCode profile data:', error);
          }
        })()
      );
    }
    
    // Get skill assessments
    fetchPromises.push(
      (async () => {
        try {
          const skillAssessmentsRef = collection(db, "candidates", uid, "skill_assessments");
          const skillAssessmentsSnapshot = await getDocs(skillAssessmentsRef);
          
          skillAssessmentsSnapshot.forEach(doc => {
            reportData.skillAssessments.push({
              id: doc.id,
              ...doc.data()
            });
          });
        } catch (error) {
          console.error('Error fetching skill assessments:', error);
        }
      })()
    );
    
    // Wait for all data fetching to complete
    await Promise.all(fetchPromises);
    
    // Convert Firestore Timestamps and ensure deep objects are properly serialized
    const serializedData = JSON.parse(JSON.stringify(reportData, (key, value) => {
      // Handle Firestore Timestamps
      if (value && typeof value === 'object' && value.seconds !== undefined && value.nanoseconds !== undefined) {
        return {
          _seconds: value.seconds,
          _nanoseconds: value.nanoseconds,
          _isTimestamp: true
        };
      }
      return value;
    }));
    
    console.log('Serialized report data:', serializedData);
    
    return new Response(JSON.stringify(serializedData), {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
  } catch (error) {
    console.error('Error fetching candidate report:', error);
    
    // Return error response
    return new Response(JSON.stringify({ 
      error: 'Failed to fetch report data',
      message: error.message 
    }), {
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
  
  // Define minimum required fields for a complete profile
  const requiredFields = [
    'fullName', 
    'email'
  ];
  
  return requiredFields.every(field => !!profileData[field]);
}