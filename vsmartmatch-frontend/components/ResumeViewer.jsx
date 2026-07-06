'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import ReactMarkdown from 'react-markdown';

const ResumeViewer = ({ userId }) => {
  const [resumeData, setResumeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { currentUser } = useAuth();
  const router = useRouter();

  useEffect(() => {
    const fetchResumeData = async () => {
      try {
        // Default to current user if no userId provided
        const targetUserId = userId || currentUser?.uid;
        
        if (!targetUserId) {
          setError('User ID is required');
          setLoading(false);
          return;
        }

        const response = await fetch(`/api/candidate/resume?userId=${targetUserId}`);
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to load resume');
        }
        
        const data = await response.json();
        setResumeData(data);
      } catch (err) {
        console.error('Error fetching resume data:', err);
        setError(err.message || 'Failed to load resume');
      } finally {
        setLoading(false);
      }
    };

    fetchResumeData();
  }, [userId, currentUser]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md">
        <p>{error}</p>
      </div>
    );
  }

  if (!resumeData || !resumeData.extracted_content) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 p-4 rounded-md">
        <p>No resume found. Please upload a resume to view it here.</p>
      </div>
    );
  }

  return (
    <div className="resume-viewer">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="p-6 border-b border-gray-200 flex justify-between items-center bg-gradient-to-r from-blue-50 to-indigo-50">
          <h2 className="text-2xl font-bold text-gray-800">Resume</h2>
          <div className="text-sm text-gray-500">
            {resumeData.timestamp && (
              <p>Last updated: {new Date(resumeData.timestamp).toLocaleDateString()}</p>
            )}
          </div>
        </div>

        <div className="p-6">
          {/* Use ReactMarkdown to render the markdown content with custom styling */}
          <div className="prose max-w-none">
            <ReactMarkdown
              components={{
                h1: ({ node, ...props }) => <h1 className="text-3xl font-bold text-gray-800 mb-2" {...props} />,
                h2: ({ node, ...props }) => <h2 className="text-2xl font-semibold text-gray-700 mt-6 mb-3" {...props} />,
                h3: ({ node, ...props }) => <h3 className="text-xl font-medium text-gray-700 mt-4 mb-2" {...props} />,
                p: ({ node, ...props }) => <p className="text-gray-600 mb-3" {...props} />,
                ul: ({ node, ...props }) => <ul className="list-disc pl-5 mb-4 text-gray-600" {...props} />,
                li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                a: ({ node, ...props }) => <a className="text-blue-600 hover:underline" {...props} />,
                strong: ({ node, ...props }) => <strong className="font-semibold text-gray-700" {...props} />,
              }}
            >
              {resumeData.extracted_content}
            </ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeViewer;