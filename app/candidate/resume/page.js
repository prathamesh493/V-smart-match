"use client";

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import ResumeViewer from '@/components/ResumeViewer';

export default function CandidateResumePage() {
  const { currentUser, userProfile } = useAuth();
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Your Resume</h1>
        <p className="text-gray-600 mt-2">
          View your parsed resume in a beautifully formatted presentation.
        </p>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Resume Preview</h2>
          <button 
            onClick={() => window.print()} 
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Print/Save PDF
          </button>
        </div>
        
        <div className="mt-4">
          <ResumeViewer userId={currentUser?.uid} />
        </div>
      </div>
    </div>
  );
}