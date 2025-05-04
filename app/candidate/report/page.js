"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

const CandidateReport = () => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter();
  const { currentUser } = useAuth();

  useEffect(() => {
    const fetchReport = async () => {
      try {
        // Use a simple query parameter approach instead of token-based auth
        const response = await fetch(`/api/candidate/report?uid=${currentUser.uid}`);
        const data = await response.json();

        if (data.error && data.redirectTo) {
          router.push(data.redirectTo);
          return;
        }

        setReportData(data);
      } catch (err) {
        setError('Failed to fetch report data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchReport();
    } else {
      setLoading(false);  // Make sure to set loading to false even if there's no user
    }
  }, [currentUser, router]);

  if (loading) {
    return (
      <div className="container mx-auto p-8">
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-8">
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!reportData) {
    return null;
  }

  const { profile, resume, github, leetcode, skillAssessments } = reportData;

  return (
      <div className="container mx-auto p-8">
        <h1 className="text-3xl font-bold mb-8">Your Profile Report</h1>
        
        {/* Basic Profile */}
        <section className="mb-8 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Personal Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p><span className="font-medium">Name:</span> {profile?.fullName}</p>
              <p><span className="font-medium">Email:</span> {profile?.email}</p>
              <p><span className="font-medium">Phone:</span> {profile?.phone || 'Not specified'}</p>
            </div>
            <div>
              <p><span className="font-medium">Location:</span> {profile?.location || 'Not specified'}</p>
              <p><span className="font-medium">Current Position:</span> {profile?.currentPosition || 'Not specified'}</p>
              <p><span className="font-medium">Years of Experience:</span> {profile?.yearsOfExperience || 'Not specified'}</p>
            </div>
          </div>
        </section>

        {/* Resume Section */}
        <section className="mb-8 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Resume Information</h2>
          
          {!resume || Object.keys(resume).length === 0 ? (
            <p className="text-gray-500 italic">No resume information available</p>
          ) : (
            <div className="space-y-4">
              {/* Skills */}
              <div>
                <h3 className="text-xl font-medium mb-2">Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {resume.skills?.map((skill, index) => (
                    <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                      {skill}
                    </span>
                  )) || <p className="text-gray-500 italic">No skills listed</p>}
                </div>
              </div>
              
              {/* Experience */}
              <div>
                <h3 className="text-xl font-medium mb-2">Experience</h3>
                {resume.experience?.map((exp, index) => (
                  <div key={index} className="mb-3 pb-3 border-b border-gray-100 last:border-0">
                    <p className="font-medium">{exp.title}</p>
                    <p className="text-sm text-gray-600">{exp.company} • {exp.duration || 'Duration not specified'}</p>
                    <p className="text-sm mt-1">{exp.description || 'No description provided'}</p>
                  </div>
                )) || <p className="text-gray-500 italic">No experience listed</p>}
              </div>
              
              {/* Education */}
              <div>
                <h3 className="text-xl font-medium mb-2">Education</h3>
                {resume.education?.map((edu, index) => (
                  <div key={index} className="mb-3 pb-3 border-b border-gray-100 last:border-0">
                    <p className="font-medium">{edu.degree}</p>
                    <p className="text-sm text-gray-600">{edu.institution} • {edu.year || 'Year not specified'}</p>
                  </div>
                )) || <p className="text-gray-500 italic">No education listed</p>}
              </div>
            </div>
          )}
        </section>
        
        {/* GitHub Profile */}
        <section className="mb-8 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">GitHub Profile</h2>
          
          {!github || Object.keys(github).length === 0 ? (
            <p className="text-gray-500 italic">No GitHub profile information available</p>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                {github.avatar_url && (
                  <img src={github.avatar_url} alt="GitHub Avatar" className="w-16 h-16 rounded-full" />
                )}
                <div>
                  <h3 className="font-medium text-lg">{github.name || github.login}</h3>
                  {github.login && <p className="text-gray-600">@{github.login}</p>}
                  {github.bio && <p className="mt-1">{github.bio}</p>}
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="bg-gray-50 p-3 rounded-md">
                  <p className="text-2xl font-bold">{github.public_repos || 0}</p>
                  <p className="text-sm text-gray-600">Repositories</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <p className="text-2xl font-bold">{github.followers || 0}</p>
                  <p className="text-sm text-gray-600">Followers</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <p className="text-2xl font-bold">{github.following || 0}</p>
                  <p className="text-sm text-gray-600">Following</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <p className="text-2xl font-bold">{github.contributions || 0}</p>
                  <p className="text-sm text-gray-600">Contributions</p>
                </div>
              </div>
              
              {/* Top Languages */}
              {github.languages && github.languages.length > 0 && (
                <div>
                  <h3 className="text-xl font-medium mb-2">Top Languages</h3>
                  <div className="flex flex-wrap gap-2">
                    {github.languages.map((lang, index) => (
                      <span key={index} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                        {lang.name} ({lang.percentage}%)
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Top Repositories */}
              {github.top_repos && github.top_repos.length > 0 && (
                <div>
                  <h3 className="text-xl font-medium mb-2">Top Repositories</h3>
                  <div className="space-y-3">
                    {github.top_repos.map((repo, index) => (
                      <div key={index} className="border border-gray-200 rounded-md p-3">
                        <p className="font-medium">{repo.name}</p>
                        <p className="text-sm text-gray-600 mt-1">{repo.description || 'No description'}</p>
                        <div className="flex items-center mt-2 text-sm text-gray-500 space-x-4">
                          <span>⭐ {repo.stars || 0}</span>
                          <span>🍴 {repo.forks || 0}</span>
                          <span>{repo.language || 'No language specified'}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
        
        {/* LeetCode Profile */}
        <section className="mb-8 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">LeetCode Profile</h2>
          
          {!leetcode || Object.keys(leetcode).length === 0 ? (
            <p className="text-gray-500 italic">No LeetCode profile information available</p>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div>
                  <h3 className="font-medium text-lg">{leetcode.username || 'LeetCode User'}</h3>
                  <p className="text-gray-600">Rank: {leetcode.ranking || 'N/A'}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="bg-green-50 p-3 rounded-md">
                  <p className="text-2xl font-bold">{leetcode.totalSolved || 0}</p>
                  <p className="text-sm text-gray-600">Total Solved</p>
                </div>
                <div className="bg-yellow-50 p-3 rounded-md">
                  <p className="text-2xl font-bold">{leetcode.acceptanceRate || '0%'}</p>
                  <p className="text-sm text-gray-600">Acceptance Rate</p>
                </div>
                <div className="bg-blue-50 p-3 rounded-md">
                  <p className="text-2xl font-bold">{leetcode.contributionPoints || 0}</p>
                  <p className="text-sm text-gray-600">Contribution Points</p>
                </div>
              </div>
              
              {/* Problem Solving Stats */}
              <div>
                <h3 className="text-xl font-medium mb-2">Problem Solving Stats</h3>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="bg-green-100 p-3 rounded-md">
                    <p className="text-lg font-bold">{leetcode.easySolved || 0}/{leetcode.easyTotal || 0}</p>
                    <p className="text-sm text-gray-600">Easy</p>
                  </div>
                  <div className="bg-yellow-100 p-3 rounded-md">
                    <p className="text-lg font-bold">{leetcode.mediumSolved || 0}/{leetcode.mediumTotal || 0}</p>
                    <p className="text-sm text-gray-600">Medium</p>
                  </div>
                  <div className="bg-red-100 p-3 rounded-md">
                    <p className="text-lg font-bold">{leetcode.hardSolved || 0}/{leetcode.hardTotal || 0}</p>
                    <p className="text-sm text-gray-600">Hard</p>
                  </div>
                </div>
              </div>
              
              {/* Recent Submissions */}
              {leetcode.recentSubmissions && leetcode.recentSubmissions.length > 0 && (
                <div>
                  <h3 className="text-xl font-medium mb-2">Recent Submissions</h3>
                  <div className="space-y-2">
                    {leetcode.recentSubmissions.map((submission, index) => (
                      <div key={index} className="border border-gray-200 rounded-md p-3">
                        <p className="font-medium">{submission.title}</p>
                        <div className="flex justify-between items-center mt-1 text-sm">
                          <span className={`px-2 py-1 rounded-full ${
                            submission.difficulty === 'Easy' ? 'bg-green-100 text-green-800' : 
                            submission.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {submission.difficulty}
                          </span>
                          <span className="text-gray-500">{submission.date}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
        
        {/* Skill Assessments */}
        {skillAssessments && skillAssessments.length > 0 && (
          <section className="mb-8 bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-4">Skill Assessments</h2>
            <div className="space-y-4">
              {skillAssessments.map((assessment, index) => (
                <div key={index} className="border border-gray-200 rounded-md p-4">
                  <div className="flex justify-between items-start">
                    <h3 className="font-medium text-lg">{assessment.skillName}</h3>
                    <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                      Score: {assessment.score}/{assessment.maxScore}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Completed on: {assessment.completedDate}</p>
                  {assessment.feedback && (
                    <div className="mt-3">
                      <p className="text-sm font-medium">Feedback:</p>
                      <p className="text-sm mt-1">{assessment.feedback}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
  );
};

export default CandidateReport;