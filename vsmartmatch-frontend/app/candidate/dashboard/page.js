'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../../../components/Header';
import { signOut } from 'firebase/auth';
import { Search, Briefcase, CheckCircle, Star, Trophy, Zap, Building2, ArrowLeft, Clock, AlertCircle, User, Calendar } from 'lucide-react';
import { useAuth } from '../../../lib/useAuth';
import { useApiClient } from '../../../lib/clientApiClient';
import Link from 'next/link';

export default function CandidateDashboard() {
  const [dashboardData, setDashboardData] = useState({
    accepted_matches: [],
    pending_matches: [],
    rejected_matches: [],
    total_matches: 0,
    summary: {}
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('pending'); // 'pending', 'accepted', 'rejected'
  const [includeRejected, setIncludeRejected] = useState(false);
  
  const { user, loading: authLoading } = useAuth();
  const api = useApiClient(user);
  const router = useRouter();

  // Redirect unauthenticated users to sign-in
  useEffect(() => {
    if (!authLoading && !user) {
      console.log('Redirecting to sign-in: No authenticated user');
      router.push('/signin');
    }
  }, [user, authLoading, router]);

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      console.log('Fetching dashboard data...', { userId: user?.uid, includeRejected }); // Debug log
      if (!user || !api) return;
      
      try {
        setLoading(true);
        setError(null);
        
        const response = await api.get(`/api/candidate/dashboard?include_rejected=${includeRejected}&limit=50`);
        
        if (response.data) {
          setDashboardData(response.data);
        }
        console.log('Dashboard data fetched successfully'); // Debug log
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (user && api) {
      fetchDashboardData();
    }
  }, [user?.uid, includeRejected]); // Use user.uid instead of user object to prevent unnecessary re-renders

  // Filter matches based on search term
  const filterMatches = (matches) => {
    if (!searchTerm) return matches;
    
    return matches.filter(match => 
      match.job_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      match.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      match.recruiter_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  // Get matches for current tab
  const getCurrentMatches = () => {
    switch (activeTab) {
      case 'accepted':
        return filterMatches(dashboardData.accepted_matches || []);
      case 'pending':
        // Only show actual pending matches, not rejected ones
        return filterMatches((dashboardData.pending_matches || []).filter(match => match.status === 'pending'));
      case 'rejected':
        // Only show rejected matches if includeRejected is true
        return includeRejected ? filterMatches(dashboardData.rejected_matches || []) : [];
      default:
        return [];
    }
  };

  // Render match card
  const renderMatchCard = (match) => (
    <div key={match.match_id} className="card hover:shadow-lg transition-all duration-300 border-l-4 border-l-purple-500">
      <div className="flex flex-col lg:flex-row justify-between gap-6">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3 flex-wrap">
            <h3 className="text-xl font-semibold text-gray-900">{match.job_title}</h3>
            
            {/* Match Score Badge */}
            <span className={`px-3 py-1 text-sm rounded-full flex items-center gap-1 ${
              match.overall_score >= 85 
                ? 'bg-green-100 text-green-800' 
                : match.overall_score >= 70 
                ? 'bg-yellow-100 text-yellow-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              <Star className="w-4 h-4" />
              {Math.round(match.overall_score)}% Match
            </span>

            {/* Status Badge */}
            {match.status === 'yes' && (
              <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full flex items-center gap-1">
                <CheckCircle className="w-4 h-4" />
                Accepted
              </span>
            )}
            {match.status === 'pending' && (
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full flex items-center gap-1">
                <Clock className="w-4 h-4" />
                Pending Review
              </span>
            )}
            {match.status === 'no' && (
              <span className="px-3 py-1 bg-red-100 text-red-800 text-sm rounded-full flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                Not Selected
              </span>
            )}
          </div>

          {/* Company and Recruiter Info */}
          <div className="flex items-center gap-4 text-sm text-gray-600 mb-4 flex-wrap">
            {match.company_name && (
              <span className="flex items-center gap-1">
                <Building2 className="w-4 h-4" />
                {match.company_name}
              </span>
            )}
            {match.recruiter_name && (
              <span className="flex items-center gap-1">
                <User className="w-4 h-4" />
                {match.recruiter_name}
              </span>
            )}
            {match.created_at && (
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {new Date(match.created_at).toLocaleDateString()}
              </span>
            )}
          </div>

          {/* Recruiter Notes */}
          {match.recruiter_notes && (
            <div className="mb-4 p-3 bg-blue-50 rounded-lg">
              <h4 className="text-sm font-semibold text-blue-900 mb-1">Recruiter Notes:</h4>
              <p className="text-sm text-blue-800">{match.recruiter_notes}</p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col items-stretch gap-3 lg:w-48">
          {match.next_step_available ? (
            <button className="btn-primary flex items-center justify-center gap-2">
              <Briefcase className="w-5 h-5" />
              Next Step
            </button>
          ) : (
            <div className="text-center py-3 px-4 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-600">
                {match.status === 'pending' ? 'Pending Human Evaluation' : 'No action available'}
              </span>
            </div>
          )}
          
          <button className="text-sm text-purple-600 hover:text-purple-800 py-2 px-4 border border-purple-200 rounded-lg hover:bg-purple-50 transition-colors">
            View Details
          </button>
        </div>
      </div>
    </div>
  );

  // Show loading state while checking auth
  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5] flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5] flex items-center justify-center">
        <div className="text-white text-center">
          <AlertCircle className="w-12 h-12 mx-auto mb-4" />
          <p className="mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const currentMatches = getCurrentMatches();

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          {/* Back Button */}
          <Link 
            href="/candidate" 
            className="inline-flex items-center text-white/90 hover:text-white mb-6 transition-colors group"
          >
            <ArrowLeft className="h-5 w-5 mr-2 transition-transform group-hover:-translate-x-1" />
            Back to Dashboard
          </Link>
          
          {/* Header */}
          <h1 className="text-4xl md:text-5xl font-bold text-white text-center mb-4 animate-fade-in-up">
            Your Job Matches
          </h1>
          <p className="text-xl text-white/90 text-center mb-12 animate-fade-in-up animation-delay-200">
            Track your AI-matched opportunities and their current status.
          </p>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12 animate-fade-in-up animation-delay-300">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <Trophy className="h-8 w-8 mb-4" />
              <h3 className="text-3xl font-bold mb-2">{dashboardData.summary?.total || 0}</h3>
              <p className="text-white/80">Total Matches</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <CheckCircle className="h-8 w-8 mb-4" />
              <h3 className="text-3xl font-bold mb-2">{dashboardData.summary?.accepted || 0}</h3>
              <p className="text-white/80">Accepted</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <Clock className="h-8 w-8 mb-4" />
              <h3 className="text-3xl font-bold mb-2">{(dashboardData.pending_matches || []).filter(match => match.status === 'pending').length}</h3>
              <p className="text-white/80">Pending Review</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <Star className="h-8 w-8 mb-4" />
              <h3 className="text-3xl font-bold mb-2">
                {dashboardData.total_matches > 0 
                  ? Math.round([...dashboardData.accepted_matches, ...dashboardData.pending_matches]
                      .reduce((sum, match) => sum + match.overall_score, 0) / dashboardData.total_matches)
                  : 0}%
              </h3>
              <p className="text-white/80">Avg Match Score</p>
            </div>
          </div>

          {/* Main Content */}
          <div className="bg-white rounded-2xl shadow-xl p-8 animate-fade-in-up animation-delay-400">
            {/* Search and Tabs */}
            <div className="flex flex-col lg:flex-row gap-4 mb-8">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by job title, company, or recruiter..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input pl-10"
                />
              </div>
              
              {/* Include Rejected Toggle */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="includeRejected"
                  checked={includeRejected}
                  onChange={(e) => setIncludeRejected(e.target.checked)}
                  className="rounded border-gray-300"
                />
                <label htmlFor="includeRejected" className="text-sm text-gray-600">
                  Show rejected matches
                </label>
              </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex border-b border-gray-200 mb-8">
              <button
                onClick={() => setActiveTab('pending')}
                className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
                  activeTab === 'pending'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Pending Review ({(dashboardData.pending_matches || []).filter(match => match.status === 'pending').length})
              </button>
              <button
                onClick={() => setActiveTab('accepted')}
                className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
                  activeTab === 'accepted'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Accepted ({dashboardData.summary?.accepted || 0})
              </button>
              {includeRejected && (
                <button
                  onClick={() => setActiveTab('rejected')}
                  className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
                    activeTab === 'rejected'
                      ? 'border-purple-500 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Not Selected ({dashboardData.summary?.rejected || 0})
                </button>
              )}
            </div>

            {/* Matches Grid */}
            <div className="space-y-6">
              {currentMatches.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Briefcase className="w-12 h-12 text-gray-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {activeTab === 'pending' && 'No pending matches'}
                    {activeTab === 'accepted' && 'No accepted matches yet'}
                    {activeTab === 'rejected' && 'No rejected matches'}
                  </h3>
                  <p className="text-gray-600 mb-6">
                    {activeTab === 'pending' && 'New matches will appear here when recruiters review your profile.'}
                    {activeTab === 'accepted' && 'Accepted matches will appear here when recruiters show interest.'}
                    {activeTab === 'rejected' && 'Matches that weren\'t selected will appear here if you enable the option.'}
                  </p>
                  {activeTab === 'pending' && (
                    <Link href="/candidate/profile" className="btn-primary">
                      Update Your Profile
                    </Link>
                  )}
                </div>
              ) : (
                currentMatches.map(renderMatchCard)
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}