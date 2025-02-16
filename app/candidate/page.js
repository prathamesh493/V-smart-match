import { FileUp, UserCircle, Briefcase } from 'lucide-react'
import Link from 'next/link'
import Header from '@/components/Header'

export default function CandidateDashboard() {
  const features = [
    {
      title: "Quick Profile Setup",
      description: "Upload your resume, add additional skills, and connect your LeetCode & GitHub profiles - all in under 2 minutes.",
      icon: FileUp,
      href: "/candidate/profile",
      gradient: "from-emerald-500 to-teal-600",
      highlights: [
        "One-click resume upload",
        "Auto-skill extraction",
        "GitHub & LeetCode integration"
      ]
    },
    {
      title: "Your Profile Report",
      description: "View your comprehensive skill profile extracted from your resume and online presence.",
      icon: UserCircle,
      href: "/candidate/report",
      gradient: "from-violet-500 to-purple-600",
      highlights: [
        "Extracted skills overview",
        "Experience analysis",
        "Project highlights"
      ]
    },
    {
      title: "Smart Job Matches",
      description: "Discover jobs that perfectly match your skills - no more endless applying. Let opportunities find you.",
      icon: Briefcase,
      href: "/candidate/dashboard",
      gradient: "from-orange-500 to-pink-600",
      highlights: [
        "AI-powered job matching",
        "Match percentage breakdown",
        "Direct recruiter connections"
      ]
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold text-white text-center mb-8 animate-fade-in-up">
            Your Career Dashboard
          </h1>
          <p className="text-xl text-white/90 text-center mb-16 animate-fade-in-up animation-delay-200">
            Let AI-powered matching connect you with the perfect opportunities. No more endless job applications.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 animate-fade-in-up animation-delay-400">
            {features.map((feature, index) => (
              <Link
                key={feature.title}
                href={feature.href}
                className="group relative overflow-hidden rounded-2xl transition-all duration-300 hover:scale-105"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-90 transition-opacity group-hover:opacity-100`} />
                <div className="relative z-10 flex flex-col h-full p-8 min-h-[420px]">
                  <feature.icon className="h-12 w-12 text-white mb-6" />
                  <h2 className="text-2xl font-bold text-white mb-4">{feature.title}</h2>
                  <p className="text-white/90 mb-6">{feature.description}</p>
                  <div className="mt-auto">
                    <ul className="space-y-2 mb-6">
                      {feature.highlights.map((highlight, idx) => (
                        <li key={idx} className="flex items-center text-white/90 text-sm">
                          <svg
                            className="h-4 w-4 mr-2 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                          {highlight}
                        </li>
                      ))}
                    </ul>
                    <div className="flex items-center text-white">
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
                </div>
              </Link>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}