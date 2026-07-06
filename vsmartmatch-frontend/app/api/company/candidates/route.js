import { NextResponse } from "next/server"

export async function GET() {
  // Simulated candidate data
  const candidates = [
    { id: 1, name: "John Doe", matchScore: 85, category: "Experienced", skills: ["React", "Node.js", "MongoDB"] },
    { id: 2, name: "Jane Smith", matchScore: 92, category: "Fresher", skills: ["JavaScript", "HTML", "CSS"] },
    { id: 3, name: "Bob Johnson", matchScore: 78, category: "Intern", skills: ["Python", "Django", "PostgreSQL"] },
  ]

  return NextResponse.json(candidates);
}

