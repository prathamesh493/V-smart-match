// This is the server component
import { Code, UserCircle, Download, CheckCircle, AlertCircle, ArrowLeft } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import Header from "@/components/Header"
import { Badge } from "@/components/ui/badge"
import ClientCategoryScoresCard from "./ClientCategoryScoresCard"
import Link from "next/link"
import AcceptRejectButtons from "./AcceptRejectButtons"
import CompanyNavBarClientWrapper from './CompanyNavBarClientWrapper';

async function getMatchReport(id) {
  try {
    const response = await fetch(`http://localhost:8000/api/match/${id}`, { cache: "no-store" })
    if (!response.ok) {
      throw new Error("Failed to fetch report data")
    }
    const data = await response.json()
    console.log("Match report data:", data) // This will log to your server terminal
    return data
  } catch (error) {
    console.error("Error fetching report:", error)
    throw error
  }
}

async function getJobDescription(jdId) {
  try {
    const response = await fetch(`http://localhost:8000/api/job-description/${jdId}`, { cache: "no-store" })
    if (!response.ok) {
      throw new Error("Failed to fetch job description")
    }
    const data = await response.json()
    return data.description || data.extracted_content || "No JD available."
  } catch (error) {
    console.error("Error fetching JD:", error)
    return "No JD available."
  }
}

async function getCandidateResume(candidateId) {
  try {
    const response = await fetch(`http://localhost:8000/api/resume/${candidateId}`, { cache: "no-store" })
    if (!response.ok) {
      throw new Error("Failed to fetch candidate resume")
    }
    const data = await response.json()
    return data.resume || data.extracted_content || "No resume available."
  } catch (error) {
    console.error("Error fetching resume:", error)
    return "No resume available."
  }
}

export default async function CompanyCandidateReport({ params }) {
  let reportData
  let error = null
  let jobDescription = ""
  let candidateResume = ""

  try {
    reportData = await getMatchReport(params.id)
    // Fetch JD and Resume in parallel
    const [jd, resume] = await Promise.all([
      getJobDescription(reportData.jobDescriptionId),
      getCandidateResume(reportData.candidateId)
    ])
    jobDescription = jd
    candidateResume = resume
  } catch (err) {
    error = err.message || "Failed to load candidate report"
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <Link href="/company/listing" className="text-white/80 hover:text-white flex items-center">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Job Listings
            </Link>
          </div>

          <div className="bg-red-500/20 backdrop-blur-sm rounded-lg p-6 text-center">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 text-white" />
            <p className="text-white text-lg">{error}</p>
            <Link
              href="/company/listing"
              className="mt-4 px-6 py-2 bg-white text-purple-700 rounded-lg font-medium inline-block"
            >
              Return to Listings
            </Link>
          </div>
        </main>
      </div>
    )
  }

  // Collapsible state for JD and Resume (client-side only)
  // We'll use a simple fallback for SSR: show both expanded
  const CollapsibleSection = ({ title, content }) => (
    <div className="w-full md:w-1/2 p-2">
      <div className="bg-white rounded-lg shadow p-4">
        <div className="font-bold text-purple-700 mb-2">{title}</div>
        <div className="text-gray-800 whitespace-pre-line text-sm max-h-64 overflow-y-auto">{content}</div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gradient-to-r from-purple-600 to-fuchsia-600">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <CompanyNavBarClientWrapper />
        {/* Candidate Info */}
        <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-2">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">{reportData.candidate_name}</h1>
            <div className="text-lg font-semibold text-fuchsia-100">{reportData.candidate_email}</div>
          </div>
        </div>

        {/* Collapsible JD & Resume */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <CollapsibleSection title="Extracted Job Description" content={jobDescription} />
          <CollapsibleSection title="Candidate Resume" content={candidateResume} />
        </div>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Candidate Match Report</h1>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-lg font-semibold text-white bg-green-500 px-3 py-1 rounded-full">
                {reportData.overallScore}% Match
              </span>
              <CheckCircle className="w-5 h-5 text-white" />
              <span className="ml-4 text-white/80 text-base font-medium bg-purple-700 px-2 py-1 rounded">Embedding Score: {reportData.embedding_score ? (reportData.embedding_score * 100).toFixed(1) : "N/A"}%</span>
            </div>
          </div>
          <div className="flex gap-2 items-center">
            <Button className="bg-white text-purple-700 hover:bg-gray-100">
              <Download className="w-4 h-4 mr-2" />
              Export PDF
            </Button>
            {/* Accept/Reject Buttons or Status */}
            <AcceptRejectButtons matchId={reportData.matchId} initialSelection={reportData.selection} />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <OverallScoreCard score={reportData.overallScore} />
          <AnalysisSummaryCard summary={reportData.analysis.summary} />
          <MetadataCard metadata={reportData.metadata} matchId={reportData.matchId} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ClientCategoryScoresCard categoryScores={reportData.categoryScores} />
          <SkillsMatchCard skillsMatch={reportData.categoryScores.skillsMatch} />
          <SoftSkillsMatchCard softSkillsMatch={reportData.categoryScores.softSkillsMatch} />
          <MissingSkillsCard missingSkills={reportData.categoryScores.skillsMatch.missingCriticalSkills} />
        </div>

        <div className="grid grid-cols-1 gap-6">
          <StrengthsWeaknessesCard
            strengths={reportData.analysis.strengths}
            weaknesses={reportData.analysis.weaknesses}
          />
          <RecommendationsCard recommendations={reportData.analysis.recommendations} />
        </div>
      </main>
    </div>
  )
}

const LoadingCard = ({ title }) => {
  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">{title}</CardTitle>
      </CardHeader>
      <CardContent className="mt-4 flex justify-center items-center h-64">
        <div className="text-gray-500">Loading...</div>
      </CardContent>
    </Card>
  )
}

const OverallScoreCard = ({ score }) => {
  let scoreColor = "text-red-500"
  let bgColor = "bg-red-100"

  if (score >= 80) {
    scoreColor = "text-green-500"
    bgColor = "bg-green-100"
  } else if (score >= 60) {
    scoreColor = "text-yellow-500"
    bgColor = "bg-yellow-100"
  }

  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Overall Match Score</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center py-6">
        <div className={`text-6xl font-bold ${scoreColor}`}>{score}%</div>
        <div className="w-full mt-4">
          <Progress value={score} className="h-3" />
        </div>
        <div className={`mt-4 px-4 py-2 rounded-full ${bgColor} ${scoreColor} font-medium`}>
          {score >= 80 ? "Strong Match" : score >= 60 ? "Moderate Match" : "Weak Match"}
        </div>
      </CardContent>
    </Card>
  )
}

const AnalysisSummaryCard = ({ summary }) => {
  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Analysis Summary</CardTitle>
      </CardHeader>
      <CardContent className="mt-4 max-h-[250px] overflow-y-auto">
        <p className="text-gray-700">{summary}</p>
      </CardContent>
    </Card>
  )
}

const MetadataCard = ({ metadata, matchId }) => {
  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Match Details</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Match ID:</span>
            <span className="font-medium">{matchId}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Model Version:</span>
            <span className="font-medium">{metadata.modelVersion}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Processing Time:</span>
            <span className="font-medium">{(metadata.processingTime / 1000).toFixed(2)}s</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

const SkillsMatchCard = ({ skillsMatch }) => {
  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Technical Skills Match</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="bg-purple-100 p-2 rounded-full mr-3">
              <Code className="w-5 h-5 text-purple-600" />
            </div>
            <span className="font-medium">Match Score</span>
          </div>
          <div className="flex items-center">
            <Progress value={skillsMatch.score} className="w-24 h-2 mr-2" />
            <span className="font-medium">{skillsMatch.score}%</span>
          </div>
        </div>
        <div className="mb-4">
          <div className="text-sm text-gray-600 mb-2">Confidence: {skillsMatch.confidence}%</div>
        </div>
        <div className="space-y-1">
          <h3 className="font-medium text-gray-700 mb-2">Key Matches</h3>
          <div className="flex flex-wrap gap-2">
            {skillsMatch.keyMatches.map((match, index) => (
              <Badge key={index} variant="outline" className="bg-green-50 text-green-700 border-green-200">
                {match.skill} ({match.relevance}%)
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

const SoftSkillsMatchCard = ({ softSkillsMatch }) => {
  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Soft Skills Match</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="bg-purple-100 p-2 rounded-full mr-3">
              <UserCircle className="w-5 h-5 text-purple-600" />
            </div>
            <span className="font-medium">Match Score</span>
          </div>
          <div className="flex items-center">
            <Progress value={softSkillsMatch.score} className="w-24 h-2 mr-2" />
            <span className="font-medium">{softSkillsMatch.score}%</span>
          </div>
        </div>
        <div className="mb-4">
          <div className="text-sm text-gray-600 mb-2">Confidence: {softSkillsMatch.confidence}%</div>
        </div>
        <div className="space-y-1">
          <h3 className="font-medium text-gray-700 mb-2">Key Matches</h3>
          <div className="flex flex-wrap gap-2">
            {softSkillsMatch.keyMatches.map((match, index) => (
              <Badge key={index} variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                {match.skill} ({match.relevance}%)
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

const MissingSkillsCard = ({ missingSkills }) => {
  if (!missingSkills || missingSkills.length === 0) return null

  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Missing Critical Skills</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="flex items-center mb-4">
          <div className="bg-orange-100 p-2 rounded-full mr-3">
            <AlertCircle className="w-5 h-5 text-orange-600" />
          </div>
          <span className="font-medium">Skills that need attention</span>
        </div>
        <div className="space-y-3">
          {missingSkills.map((skill, index) => (
            <div key={index} className="flex justify-between items-center">
              <span className="text-gray-700">{skill.skill}</span>
              <div className="flex items-center">
                <span className="text-sm text-gray-600 mr-2">Importance:</span>
                <Badge
                  variant="outline"
                  className={`
                    ${
                      skill.importance >= 70
                        ? "bg-red-50 text-red-700 border-red-200"
                        : skill.importance >= 50
                          ? "bg-orange-50 text-orange-700 border-orange-200"
                          : "bg-yellow-50 text-yellow-700 border-yellow-200"
                    }
                  `}
                >
                  {skill.importance}%
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

const StrengthsWeaknessesCard = ({ strengths, weaknesses }) => {
  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Strengths & Weaknesses</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-green-600 flex items-center mb-3">
              <CheckCircle className="w-5 h-5 mr-2" />
              Strengths
            </h3>
            <ul className="space-y-2">
              {strengths.map((strength, index) => (
                <li key={index} className="text-gray-700 flex">
                  <span className="text-green-500 mr-2">•</span>
                  <span>{strength}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="font-medium text-orange-600 flex items-center mb-3">
              <AlertCircle className="w-5 h-5 mr-2" />
              Weaknesses
            </h3>
            <ul className="space-y-2">
              {weaknesses.map((weakness, index) => (
                <li key={index} className="text-gray-700 flex">
                  <span className="text-orange-500 mr-2">•</span>
                  <span>{weakness}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

const RecommendationsCard = ({ recommendations }) => {
  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Recommendations</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <ul className="space-y-3">
          {recommendations.map((recommendation, index) => (
            <li key={index} className="flex">
              <div className="bg-purple-100 text-purple-600 rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 mt-0.5">
                {index + 1}
              </div>
              <span className="text-gray-700">{recommendation}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
