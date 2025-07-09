'use client';
//app\company\page.js

import { FileText, PieChart, Bell, Briefcase } from 'lucide-react'
import Link from 'next/link'
import Header from '@/components/Header'
import { useAuth } from '@/lib/useAuth'; // Adjust path
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function RecruiterDashboard() {

  const { user, loading } = useAuth();
  const router = useRouter();

  // Redirect to signin if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      console.log('Redirecting to sign-in: No authenticated user');
      router.push('/signin');
    }
  }, [user, loading, router]);

  const features = [
    {
      title: "Upload Job Listing",
      description: "Create detailed job listings with required skills, experience, and qualifications to find your perfect match.",
      icon: FileText,
      href: "/company/upload",
      gradient: "from-purple-500 to-indigo-600"
    },
    {
      title: "View Job Listings",
      description: "Manage and review all your active and archived job postings in one centralized location.",
      icon: Briefcase,
      href: "/company/listing",
      gradient: "from-green-500 to-emerald-600"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold text-white text-center mb-8 animate-fade-in-up">
            Welcome to Your Recruitment Hub
          </h1>
          <p className="text-xl text-white/90 text-center mb-16 animate-fade-in-up animation-delay-200">
            Streamline your hiring process with AI-powered candidate matching and efficient communication tools.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 animate-fade-in-up animation-delay-400">
            {features.map((feature, index) => (
              <Link
                key={feature.title}
                href={feature.href}
                className="group relative overflow-hidden rounded-2xl p-6 transition-all duration-300 hover:scale-105"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-90 transition-opacity group-hover:opacity-100`} />
                <div className="relative z-10 flex flex-col h-full min-h-[260px]">
                  <feature.icon className="h-10 w-10 text-white mb-4" />
                  <h2 className="text-xl font-bold text-white mb-3">{feature.title}</h2>
                  <p className="text-white/90 text-sm flex-grow">{feature.description}</p>
                  <div className="mt-4 flex items-center text-white">
                    <span className="text-sm font-semibold">Get Started</span>
                    <svg
                      className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}