'use client'
import { useState } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function ClientCategoryScoresCard({ categoryScores }) {
  const [chartType, setChartType] = useState('radar') // 'bar' or 'radar'
  
  const data = [
    { name: "Skills", score: categoryScores.skillsMatch.score },
    { name: "Soft Skills", score: categoryScores.softSkillsMatch.score },
    { name: "Education", score: categoryScores.educationMatch.score },
    { name: "Experience", score: categoryScores.experienceMatch.score },
    { name: "Cultural Fit", score: categoryScores.culturalFitMatch.score },
  ]

  const toggleChart = (direction) => {
    if (direction === 'next') {
      setChartType(chartType === 'bar' ? 'radar' : 'bar')
    } else {
      setChartType(chartType === 'radar' ? 'bar' : 'radar')
    }
  }

  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <div className="flex items-center justify-between">
          <CardTitle className="text-white">Category Scores</CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleChart('prev')}
              className="text-white hover:bg-white/20 p-1"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-white text-sm font-medium min-w-[80px] text-center">
              {chartType === 'bar' ? 'Bar Chart' : 'Radar Chart'}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleChart('next')}
              className="text-white hover:bg-white/20 p-1"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="mt-4">
        <ResponsiveContainer width="100%" height={250}>
          {chartType === 'bar' ? (
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="score" fill="#c026d3" />
            </BarChart>
          ) : (
            <RadarChart data={data}>
              <PolarGrid />
              <PolarAngleAxis dataKey="name" />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={false}
                axisLine={false}
              />
              <Radar
                name="Score"
                dataKey="score"
                stroke="#c026d3"
                fill="#c026d3"
                fillOpacity={0.3}
                strokeWidth={2}
              />
              <Tooltip />
            </RadarChart>
          )}
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