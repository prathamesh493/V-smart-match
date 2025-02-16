"use client"

import { useState, useEffect } from "react"
import { UserCircle } from "lucide-react"
import Header from "@/components/Header"
import Link from "next/link"

export default function MatchReport() {
  const [candidates, setCandidates] = useState([
    {
      id: 1,
      name: "John Doe",
      category: "Full Stack",
      matchScore: 85,
      skills: ["React", "Node.js", "MongoDB"]
    },
    {
      id: 2,
      name: "Jane Smith",
      category: "Frontend",
      matchScore: 92,
      skills: ["JavaScript", "HTML", "CSS"]
    },
    {
      id: 3,
      name: "Bob Johnson",
      category: "Backend",
      matchScore: 78,
      skills: ["Python", "Django", "PostgreSQL"]
    }
  ])
  const [threshold, setThreshold] = useState(47)

  const filteredCandidates = candidates.filter(
    (candidate) => candidate.matchScore >= threshold
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-5xl font-bold text-white text-center mb-4">
            Match Report
          </h1>
          <p className="text-xl text-white/90 text-center mb-16">
            Review and filter qualified candidates based on their match scores
          </p>

          <div className="backdrop-blur-lg bg-white/10 rounded-xl p-6 mb-12 border border-white/20">
            <h2 className="text-lg font-semibold mb-4 text-white">
              Minimum Qualification Threshold: {threshold}%
            </h2>
            <input
              type="range"
              min="0"
              max="100"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer"
              style={{
                background: `linear-gradient(to right, rgba(255,255,255,0.8) ${threshold}%, rgba(255,255,255,0.2) ${threshold}%)`
              }}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCandidates.map((candidate) => (
              <div
                key={candidate.id}
                className="backdrop-blur-lg bg-white/10 rounded-xl p-6 border border-white/20 hover:shadow-xl transition-all duration-300 hover:scale-105 group"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-4">
                    <div className="p-2 rounded-full bg-white/20 group-hover:bg-white/30 transition-colors">
                      <UserCircle className="h-8 w-8 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">{candidate.name}</h3>
                      <p className="text-sm text-white/75">{candidate.category}</p>
                    </div>
                  </div>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-white/20 text-white">
                    {candidate.matchScore}% Match
                  </span>
                </div>

                <div className="mb-6">
                  <h4 className="font-medium mb-2 text-white/90">Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {candidate.skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-3 py-1 bg-white/20 rounded-full text-sm text-white/90 hover:bg-white/30 transition-colors"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="w-full py-3 px-6 bg-white/20 text-white rounded-full font-semibold hover:bg-white/30 transition-colors border border-white/20">
                  <Link href="/company/report">
                    View Profile
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}