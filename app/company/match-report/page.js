"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { UserCircle, AlertCircle, Search, ArrowLeft } from "lucide-react"
import Header from "@/components/Header"
import Link from "next/link"
import { useAuth } from "@/lib/useAuth"

export default function MatchReport() {
  const [jobDetails, setJobDetails] = useState(null)
  const [error, setError] = useState("")
  const [threshold, setThreshold] = useState(47)
  const [searchTerm, setSearchTerm] = useState("")
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user, loading: authLoading } = useAuth()
  const jobId = searchParams.get("jobId")
  const csvLinkRef = useRef(null);

  // --- New and Updated State for Pagination & Data Handling ---
  const [candidates, setCandidates] = useState([]);
  const [candidateDetails, setCandidateDetails] = useState({});
  const [isLoading, setIsLoading] = useState(true); // For initial page load
  const [isLoadingMore, setIsLoadingMore] = useState(false); // For "Load More" button
  const [hasMore, setHasMore] = useState(true);
  const [lastCandidateId, setLastCandidateId] = useState(null);

  // Handle authentication and initial redirect
  useEffect(() => {
    if (!user && !authLoading) {
      router.push("/signin")
    }
  }, [user, authLoading, router])

  // --- New Data Fetching Function with Pagination ---
  const fetchData = async (isNewSearch = false) => {
    // Prevent duplicate fetches when already loading
    if (isLoadingMore) return;
    
    // For a new filter/search, show the main loader, not the button loader
    if (isNewSearch) {
      setIsLoading(true);
      setCandidates([]);
      setLastCandidateId(null);
      setHasMore(true);
    } else {
      setIsLoadingMore(true);
    }
    setError("");

    try {
      // Fetch job details only on the first load
      if (isNewSearch) {
        const jobResponse = await fetch(`http://localhost:8000/api/job-description/${jobId}`)
        if (!jobResponse.ok) throw new Error("Failed to fetch job details")
        const jobData = await jobResponse.json()
        setJobDetails(jobData)
      }

      // Construct the API URL with filtering and pagination parameters
      const params = new URLSearchParams({
        limit: "12", // Fetch 12 candidates per page
        min_score: threshold,
      });

      // For subsequent pages, add the 'start_after' cursor
      const lastId = isNewSearch ? null : lastCandidateId;
      if (lastId) {
        params.append('start_after', lastId);
      }

      const matchesResponse = await fetch(`http://localhost:8000/api/match/job/${jobId}?${params.toString()}`)
      if (!matchesResponse.ok) throw new Error("Failed to fetch candidate matches")
      
      const newMatches = await matchesResponse.json();

      // Append new matches to the existing list or set a new list
      setCandidates(prev => isNewSearch ? newMatches : [...prev, ...newMatches]);
      
      // If we received fewer matches than we asked for, we've reached the end
      if (newMatches.length < 12) {
        setHasMore(false);
      } else {
        // Store the ID of the last candidate for the next fetch
        setLastCandidateId(newMatches[newMatches.length - 1].matchId);
      }
    } catch (error) {
      console.error("Error fetching data:", error)
      setError(error.message || "Failed to load data")
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  }

  // --- Effect to trigger data fetching ---
  useEffect(() => {
    // Only fetch if we have a user and jobId, and auth is complete
    if (user && jobId && !authLoading) {
      fetchData(true); // `true` indicates a new search/filter change
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId, user, authLoading, threshold]); // Re-fetches when threshold changes


  // Client-side filtering now only applies to the search term for loaded candidates
  const filteredCandidates = candidates.filter((candidate) => {
    if (!searchTerm) return true;
    const details = candidateDetails[candidate.candidateId];
    return (
      (details?.full_name?.toLowerCase() || "").includes(searchTerm.toLowerCase()) ||
      (details?.email?.toLowerCase() || "").includes(searchTerm.toLowerCase())
    )
  });

  // Fetch candidate details (name, email) for all visible candidates
  useEffect(() => {
    async function fetchAllCandidateDetails() {
      const idsToFetch = candidates
        .map(c => c.candidateId)
        .filter(id => id && !candidateDetails[id]); // Only fetch if not already present
        
      if (idsToFetch.length === 0) return;

      const newDetails = { ...candidateDetails };
      await Promise.all(idsToFetch.map(async (id) => {
        try {
          const res = await fetch(`http://localhost:8000/api/candidate/basic-info/${id}`);
          if (res.ok) {
            newDetails[id] = await res.json();
          } else {
            newDetails[id] = { full_name: 'Name not found', email: '' };
          }
        } catch (e) {
          newDetails[id] = { full_name: 'Error loading name', email: '' };
        }
      }));
      setCandidateDetails(newDetails);
    }
    // Run this whenever the main 'candidates' list changes
    if (candidates.length > 0) {
        fetchAllCandidateDetails();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [candidates]);

  // Split candidates by selection status
  const selectedCandidates = filteredCandidates.filter(c => c.selection === 'yes');
  const rejectedCandidates = filteredCandidates.filter(c => c.selection === 'no');
  const unreviewedCandidates = filteredCandidates.filter(c => !c.selection);

  // CSV Export logic remains the same
  function handleExportCSV() {
    const headers = ["Candidate Name", "Candidate Email", "Candidate ID", "Match ID", "Overall Score", "Selection", "Key Skills"];
    const rows = filteredCandidates.map(c => [
      candidateDetails[c.candidateId]?.full_name || "",
      candidateDetails[c.candidateId]?.email || "",
      c.candidateId,
      c.matchId,
      c.overallScore,
      c.selection || "Unreviewed",
      (c.categoryScores?.skillsMatch?.keyMatches?.map(s => `${s.skill} (${s.relevance}%)`).join('; ') || "")
    ]);
    const csvContent = [headers, ...rows].map(row => row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    if (csvLinkRef.current) {
      csvLinkRef.current.href = url;
      csvLinkRef.current.download = `candidates_${jobDetails?.job_title || jobId}.csv`;
      csvLinkRef.current.click();
      URL.revokeObjectURL(url);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <Link href="/company/listing" className="text-white/80 hover:text-white flex items-center">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Job Listings
            </Link>
            <button
              onClick={handleExportCSV}
              disabled={candidates.length === 0}
              className="px-6 py-2 bg-white text-purple-700 rounded-lg font-medium hover:bg-gray-100 transition-colors border border-white/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Export Visible as CSV
            </button>
            <a ref={csvLinkRef} style={{ display: 'none' }} aria-hidden="true" />
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
            </div>
          ) : error ? (
            <div className="bg-red-500/20 backdrop-blur-sm rounded-lg p-6 text-center">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-white" />
              <p className="text-white text-lg">{error}</p>
            </div>
          ) : (
            <>
              <h1 className="text-4xl md:text-5xl font-bold text-white text-center mb-4">Candidate Matches</h1>
              {jobDetails && (
                <div className="text-center mb-8">
                  <h2 className="text-2xl text-white/90 mb-2">{jobDetails.job_title}</h2>
                  <p className="text-xl text-white/80">{jobDetails.company}</p>
                </div>
              )}

              <div className="mb-8">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-white/50" />
                  <input
                    type="text"
                    placeholder="Search loaded candidates by name or email..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-12 py-4 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30"
                  />
                </div>
              </div>

              <div className="backdrop-blur-lg bg-white/10 rounded-xl p-6 mb-12 border border-white/20">
                <h2 className="text-lg font-semibold mb-4 text-white">Minimum Match Score: {threshold}%</h2>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={threshold}
                  onChange={(e) => setThreshold(Number(e.target.value))}
                  className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer"
                  style={{ background: `linear-gradient(to right, rgba(255,255,255,0.8) ${threshold}%, rgba(255,255,255,0.2) ${threshold}%)` }}
                />
              </div>

              {/* Render candidate lists */}
              {selectedCandidates.length > 0 && (
                <div className="mb-12"><h2 className="text-2xl font-bold text-green-200 mb-4">Selected</h2><div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{selectedCandidates.map(c => <CandidateCard key={c.matchId} candidate={c} candidateDetails={candidateDetails} />)}</div></div>
              )}
              {rejectedCandidates.length > 0 && (
                <div className="mb-12"><h2 className="text-2xl font-bold text-red-200 mb-4">Rejected</h2><div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{rejectedCandidates.map(c => <CandidateCard key={c.matchId} candidate={c} candidateDetails={candidateDetails} />)}</div></div>
              )}
              <div className="mb-12"><h2 className="text-2xl font-bold text-white mb-4">Unreviewed</h2>{unreviewedCandidates.length > 0 ? <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{unreviewedCandidates.map(c => <CandidateCard key={c.matchId} candidate={c} candidateDetails={candidateDetails} />)}</div> : !hasMore && <div className="bg-white/10 backdrop-blur-sm rounded-lg p-12 text-center"><UserCircle className="h-16 w-16 mx-auto mb-4 text-white/70" /><h2 className="text-2xl font-bold text-white mb-2">No candidates match the current criteria.</h2></div>}</div>

              {/* --- "Load More" Button --- */}
              {hasMore && (
                <div className="text-center mt-8">
                  <button
                    onClick={() => fetchData(false)}
                    disabled={isLoadingMore}
                    className="px-8 py-3 bg-white text-purple-700 rounded-lg font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-wait"
                  >
                    {isLoadingMore ? "Loading..." : "Load More"}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  )
}

// CandidateCard component (no changes needed)
function CandidateCard({ candidate, candidateDetails }) {
  const details = candidateDetails[candidate.candidateId] || {};
  return (
    <div className="backdrop-blur-lg bg-white/10 rounded-xl p-6 border border-white/20 hover:shadow-xl transition-all duration-300 hover:scale-105 group">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-4">
          <div className="p-2 rounded-full bg-white/20 group-hover:bg-white/30 transition-colors">
            <UserCircle className="h-8 w-8 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">{details.full_name || 'Loading Name...'}</h3>
            <p className="text-sm text-white/75">{details.email || 'Loading Email...'}</p>
            <p className="text-xs text-white/50">ID: {candidate.candidateId.substring(0, 10)}...</p>
          </div>
        </div>
        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${candidate.overallScore >= 80 ? "bg-green-500/30 text-green-100" : candidate.overallScore >= 60 ? "bg-yellow-500/30 text-yellow-100" : "bg-red-500/30 text-red-100"}`}>
          {candidate.overallScore}% Match
        </span>
      </div>
      <div className="mb-6">
        <h4 className="font-medium mb-2 text-white/90">Key Skills</h4>
        <div className="flex flex-wrap gap-2">
          {candidate.categoryScores?.skillsMatch?.keyMatches?.slice(0, 5).map((skill, index) => (
            <span key={index} className="px-3 py-1 bg-white/20 rounded-full text-sm text-white/90 hover:bg-white/30 transition-colors">
              {skill.skill} ({skill.relevance}%)
            </span>
          )) || <span className="text-white/60">No skills data available</span>}
        </div>
      </div>
      <Link href={`/company/report/${candidate.matchId}`} className="block w-full py-3 px-6 bg-white/20 text-white text-center rounded-full font-semibold hover:bg-white/30 transition-colors border border-white/20">
        View Full Report
      </Link>
    </div>
  );
}