// app/api/candidate/report/route.js
import { db } from '@/firebase/config';
import { doc, getDoc, collection, getDocs, query, where, orderBy, limit } from 'firebase/firestore';
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
    
    // Get resume data - Use simple query first to avoid index requirements
    let resumeData = {};
    try {
      console.log(`Attempting to fetch resume for user: ${uid}`);
      
      // Use a simple query without ordering to avoid index requirements
      const simpleQuery = query(
        collection(db, "resumes"),
        where("user_id", "==", uid),
        limit(1)
      );
      let resumeSnapshot = await getDocs(simpleQuery);
      
      if (!resumeSnapshot.empty) {
        console.log("Found resume through simple query");
        const resumeDoc = resumeSnapshot.docs[0];
        resumeData = resumeDoc.data();
      } else {
        console.log("No resume found by user_id query, trying direct document lookup");
        const directResumeRef = doc(db, "resumes", uid);
        const directSnapshot = await getDoc(directResumeRef);
        
        if (directSnapshot.exists()) {
          console.log("Found resume through direct document lookup");
          resumeData = directSnapshot.data();
        } else {
          console.log("No resume found for this user");
        }
      }
      
      console.log(`Resume data fetched:`, Object.keys(resumeData).length > 0 ? 
        `Fields present: ${Object.keys(resumeData).join(', ')}` : 
        "No resume data found");
      
      // Check if extracted_content exists and is a string
      if (resumeData && resumeData.extracted_content && typeof resumeData.extracted_content === 'string') {
        console.log(`Resume content found, length: ${resumeData.extracted_content.length} chars`);
        // Process the markdown content into structured data
        try {
          resumeData = processResumeMarkdown(resumeData.extracted_content, resumeData);
        } catch (processingError) {
          console.error('Error processing resume markdown:', processingError);
          // Continue with the original resume data if processing fails
        }
      } else {
        console.log('No valid extracted_content found in resume data');
      }
    } catch (resumeError) {
      console.error('Error fetching resume data:', resumeError);
      // Continue with empty resume data
    }
    
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

// Helper function to process resume markdown content
function processResumeMarkdown(markdown, resumeData) {
  if (!markdown) return resumeData;
  
  const result = { 
    ...resumeData,
    skills: [],
    experience: [],
    education: []
  };

  try {
    // Extract Skills section
    const skillsMatch = markdown.match(/## Skills\n([\s\S]*?)(?=##|$)/);
    if (skillsMatch && skillsMatch[1]) {
      const skillsText = skillsMatch[1].trim();
      
      // Extract programming languages
      const programmingMatch = skillsText.match(/\*\*Programming Languages:\*\* (.*?)(?=\n|$)/);
      if (programmingMatch && programmingMatch[1]) {
        result.skills.push(...programmingMatch[1].split(', '));
      }
      
      // Extract frameworks
      const frameworksMatch = skillsText.match(/\*\*Frameworks:\*\* (.*?)(?=\n|$)/);
      if (frameworksMatch && frameworksMatch[1]) {
        result.skills.push(...frameworksMatch[1].split(', '));
      }
      
      // Extract databases
      const dbMatch = skillsText.match(/\*\*Databases:\*\* (.*?)(?=\n|$)/);
      if (dbMatch && dbMatch[1]) {
        result.skills.push(...dbMatch[1].split(', '));
      }
      
      // Extract tools
      const toolsMatch = skillsText.match(/\*\*Tools:\*\* (.*?)(?=\n|$)/);
      if (toolsMatch && toolsMatch[1]) {
        result.skills.push(...toolsMatch[1].split(', '));
      }
    }

    // Extract Experience section
    const experienceMatch = markdown.match(/## Experience\n([\s\S]*?)(?=##|$)/);
    if (experienceMatch && experienceMatch[1]) {
      const experienceText = experienceMatch[1].trim();
      const experienceEntries = experienceText.split(/\*\*/g).filter(Boolean);

      for (let i = 0; i < experienceEntries.length; i += 2) {
        if (experienceEntries[i] && experienceEntries[i+1]) {
          const titleParts = experienceEntries[i].trim().split(',');
          const title = titleParts[0].trim();
          const company = titleParts[1] ? titleParts[1].trim() : '';
          
          const descriptionParts = experienceEntries[i+1].split('\n');
          const duration = descriptionParts[0].trim();
          
          // Join the rest of the lines for description, remove bullet points
          const description = descriptionParts.slice(1)
            .join('\n')
            .replace(/^\*/gm, '')
            .trim();
          
          result.experience.push({
            title,
            company,
            duration,
            description
          });
        }
      }
    }

    // Extract Education section
    const educationMatch = markdown.match(/## Education\n([\s\S]*?)(?=##|$)/);
    if (educationMatch && educationMatch[1]) {
      const educationText = educationMatch[1].trim();
      const educationEntries = educationText.split(/\*\*/g).filter(Boolean);

      for (let i = 0; i < educationEntries.length; i += 2) {
        if (educationEntries[i] && educationEntries[i+1]) {
          const degree = educationEntries[i].trim();
          const detailsText = educationEntries[i+1].trim();
          
          const institutionMatch = detailsText.match(/(.*?)(?=\d|$)/);
          const institution = institutionMatch ? institutionMatch[1].trim() : '';
          
          const yearMatch = detailsText.match(/(\d{4}\s*-\s*\d{4}|\d{4})/);
          const year = yearMatch ? yearMatch[1].trim() : '';
          
          result.education.push({
            degree,
            institution,
            year
          });
        }
      }
    }

    return result;
  } catch (error) {
    console.error('Error processing resume markdown:', error);
    return resumeData;
  }
}