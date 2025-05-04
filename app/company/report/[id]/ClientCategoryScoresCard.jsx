'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

export default function ClientCategoryScoresCard({ categoryScores }) {
  const data = [
    { name: "Skills", score: categoryScores.skillsMatch.score },
    { name: "Soft Skills", score: categoryScores.softSkillsMatch.score },
    { name: "Education", score: categoryScores.educationMatch.score },
    { name: "Experience", score: categoryScores.experienceMatch.score },
    { name: "Cultural Fit", score: categoryScores.culturalFitMatch.score },
  ]

  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Category Scores</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Bar dataKey="score" fill="#c026d3" />
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 space-y-3">
          {data.map((item, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-gray-700">{item.name}</span>
              <div className="flex items-center">
                <Progress value={item.score} className="w-32 h-2 mr-2" />
                <span className="text-gray-700 font-medium">{item.score}%</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}