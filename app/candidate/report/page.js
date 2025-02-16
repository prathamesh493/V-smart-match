"use client"

import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { BookOpen, GitBranch, Star, Code, Award, FileText, BriefcaseIcon, GraduationCap, Plus, UserCircle, Download } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';

const CandidateReport = () => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReportData = async () => {
      try {
        const response = await fetch('/api/candidate/report');
        const data = await response.json();
        setReportData(data);
      } catch (error) {
        console.error('Error fetching report:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchReportData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const completionScore = calculateCompletionScore(reportData);

  const handleExportPDF = () => {
    console.log('Exporting PDF...');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <main className="container mx-auto px-4 py-12">
        {/* Header Section */}
        <div className="bg-white rounded-2xl shadow-sm p-8 mb-8">
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
            <div className="space-y-2">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Professional Profile
              </h1>
              <p className="text-slate-600">Your comprehensive skill assessment and career portfolio</p>
            </div>
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-none">
                <CardContent className="py-3 px-4">
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm text-slate-600">Profile Score</div>
                      <div className="text-lg font-semibold text-blue-600">{completionScore}%</div>
                    </div>
                    <Progress value={completionScore} className="w-32 bg-blue-100" />
                  </div>
                </CardContent>
              </Card>
              <Button 
                onClick={handleExportPDF}
                className="bg-blue-600 hover:bg-blue-700 transition-colors"
              >
                <Download className="w-4 h-4 mr-2" />
                Export Report
              </Button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Card className="bg-white/50 backdrop-blur-sm border-none shadow-sm hover:shadow-md transition-all">
            <ProfileCard data={reportData?.profile} />
          </Card>
          <Card className="bg-white/50 backdrop-blur-sm border-none shadow-sm hover:shadow-md transition-all">
            <GithubStatsCard data={reportData?.github} />
          </Card>
          <Card className="bg-white/50 backdrop-blur-sm border-none shadow-sm hover:shadow-md transition-all">
            <LeetcodeStatsCard data={reportData?.leetcode} />
          </Card>
        </div>

        {/* Detailed Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-6">
            <Card className="bg-white/50 backdrop-blur-sm border-none shadow-sm hover:shadow-md transition-all">
              <SkillsCard skills={reportData?.skills} />
            </Card>
            <Card className="bg-white/50 backdrop-blur-sm border-none shadow-sm hover:shadow-md transition-all">
              <EducationCard education={reportData?.education} />
            </Card>
          </div>
          <div className="space-y-6">
            <Card className="bg-white/50 backdrop-blur-sm border-none shadow-sm hover:shadow-md transition-all">
              <ExperienceCard experience={reportData?.experience} />
            </Card>
            <Card className="bg-white/50 backdrop-blur-sm border-none shadow-sm hover:shadow-md transition-all">
              <ProjectsCard projects={reportData?.projects} />
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

const calculateCompletionScore = (data) => {
  if (!data) return 0;
  
  const sections = [
    'profile',
    'github',
    'leetcode',
    'skills',
    'experience',
    'education',
    'projects'
  ];
  
  const completedSections = sections.filter(section => {
    const sectionData = data[section];
    return sectionData && (
      Array.isArray(sectionData) ? sectionData.length > 0 : Object.keys(sectionData).length > 0
    );
  });
  
  return Math.round((completedSections.length / sections.length) * 100);
};

const EmptyCard = ({ title, icon: Icon, buttonText, onClick }) => (
  <CardContent className="pt-6">
    <div className="text-center">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-50 flex items-center justify-center">
        <Icon className="w-8 h-8 text-blue-600" />
      </div>
      <CardTitle className="mb-2 text-slate-800">{title}</CardTitle>
      <p className="text-sm text-slate-500 mb-4">This section needs your attention</p>
      <Button 
        onClick={onClick}
        className="bg-blue-600 hover:bg-blue-700 transition-colors"
      >
        {buttonText}
      </Button>
    </div>
  </CardContent>
);

const ProfileCard = ({ data }) => {
  if (!data) {
    return (
      <EmptyCard
        title="Profile Information"
        icon={UserCircle}
        buttonText="Complete Profile"
        onClick={() => console.log('Complete profile')}
      />
    );
  }

  return (
    <>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-slate-800">Profile</CardTitle>
          <Button variant="ghost" className="text-blue-600 hover:text-blue-700">
            Edit
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="bg-gradient-to-br from-blue-600 to-indigo-600 text-white p-3 rounded-xl">
              <UserCircle className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-800">{data.name}</h3>
              <p className="text-slate-600">{data.title}</p>
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-slate-600">{data.location}</p>
            <p className="text-sm text-slate-600">{data.email}</p>
          </div>
        </div>
      </CardContent>
    </>
  );
};

const GithubStatsCard = ({ data }) => {
  if (!data) {
    return (
      <EmptyCard
        title="GitHub Statistics"
        icon={GitBranch}
        buttonText="Connect GitHub"
        onClick={() => console.log('Connect GitHub')}
      />
    );
  }

  return (
    <>
      <CardHeader>
        <CardTitle className="text-slate-800">GitHub Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 text-center">
            <GitBranch className="w-6 h-6 mx-auto mb-2 text-blue-600" />
            <div className="text-sm text-slate-600">Repositories</div>
            <div className="font-semibold text-slate-800">{data.repositories}</div>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 text-center">
            <Star className="w-6 h-6 mx-auto mb-2 text-blue-600" />
            <div className="text-sm text-slate-600">Stars</div>
            <div className="font-semibold text-slate-800">{data.stars}</div>
          </div>
        </div>
        <div>
          <div className="text-sm font-medium text-slate-800 mb-3">Most Used Languages</div>
          <ResponsiveContainer width="100%" height={100}>
            <BarChart data={data.languages}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fill: '#64748b' }} />
              <YAxis tick={{ fill: '#64748b' }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <Bar dataKey="percentage" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </>
  );
};

const LeetcodeStatsCard = ({ data }) => {
  if (!data) {
    return (
      <EmptyCard
        title="LeetCode Statistics"
        icon={Code}
        buttonText="Connect LeetCode"
        onClick={() => console.log('Connect LeetCode')}
      />
    );
  }

  return (
    <>
      <CardHeader>
        <CardTitle className="text-slate-800">LeetCode Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 text-center">
            <div className="text-sm text-slate-600">Easy</div>
            <div className="font-semibold text-emerald-600">{data.solved.easy}</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-50 to-amber-50 rounded-xl p-4 text-center">
            <div className="text-sm text-slate-600">Medium</div>
            <div className="font-semibold text-amber-600">{data.solved.medium}</div>
          </div>
          <div className="bg-gradient-to-br from-red-50 to-rose-50 rounded-xl p-4 text-center">
            <div className="text-sm text-slate-600">Hard</div>
            <div className="font-semibold text-rose-600">{data.solved.hard}</div>
          </div>
        </div>
        <div className="space-y-4">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600">Contest Rating</span>
              <span className="font-semibold text-blue-600">{data.contestRating}</span>
            </div>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600">Global Ranking</span>
              <span className="font-semibold text-blue-600">Top {data.globalRanking}%</span>
            </div>
          </div>
        </div>
      </CardContent>
    </>
  );
};

const SkillsCard = ({ skills }) => {
  if (!skills?.length) {
    return (
      <EmptyCard
        title="Skills"
        icon={Award}
        buttonText="Add Skills"
        onClick={() => console.log('Add skills')}
      />
    );
  }

  return (
    <>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-slate-800">Skills</CardTitle>
          <Button variant="ghost" className="text-blue-600 hover:text-blue-700">
            Add More
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {skills.map((skill, index) => (
            <span
              key={index}
              className="px-4 py-1.5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-full text-slate-700 text-sm font-medium"
            >
              {skill}
            </span>
          ))}
        </div>
      </CardContent>
    </>
  );
};

const ExperienceCard = ({ experience }) => {
  if (!experience?.length) {
    return (
      <EmptyCard
        title="Work Experience"
        icon={BriefcaseIcon}
        buttonText="Add Experience"
        onClick={() => console.log('Add experience')}
      />
    );
  }

  return (
    <>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-slate-800">Work Experience</CardTitle>
          <Button variant="ghost" className="text-blue-600 hover:text-blue-700">
            Add More
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
        {experience.map((exp, index) => (
            <div key={index} className="relative pl-6 border-l-2 border-blue-200 hover:border-blue-400 transition-colors">
              <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-blue-600"></div>
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4">
                <h3 className="font-medium text-slate-800">{exp.title}</h3>
                <p className="text-blue-600 font-medium">{exp.company}</p>
                <p className="text-sm text-slate-500 mt-1">
                  {exp.startDate} - {exp.endDate || 'Present'}
                </p>
                <p className="text-slate-600 mt-3">{exp.description}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </>
  );
};

const EducationCard = ({ education }) => {
  if (!education?.length) {
    return (
      <EmptyCard
        title="Education"
        icon={GraduationCap}
        buttonText="Add Education"
        onClick={() => console.log('Add education')}
      />
    );
  }

  return (
    <>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-slate-800">Education</CardTitle>
          <Button variant="ghost" className="text-blue-600 hover:text-blue-700">
            Add More
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {education.map((edu, index) => (
            <div key={index} className="relative pl-6 border-l-2 border-blue-200 hover:border-blue-400 transition-colors">
              <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-blue-600"></div>
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4">
                <h3 className="font-medium text-slate-800">{edu.degree}</h3>
                <p className="text-blue-600 font-medium">{edu.school}</p>
                <p className="text-sm text-slate-500 mt-1">{edu.graduationYear}</p>
                {edu.gpa && (
                  <div className="mt-2 inline-flex items-center bg-white/50 rounded-full px-3 py-1">
                    <Award className="w-4 h-4 text-blue-600 mr-1" />
                    <span className="text-sm font-medium text-slate-700">GPA: {edu.gpa}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </>
  );
};

const ProjectsCard = ({ projects }) => {
  if (!projects?.length) {
    return (
      <EmptyCard
        title="Projects"
        icon={FileText}
        buttonText="Add Projects"
        onClick={() => console.log('Add projects')}
      />
    );
  }

  return (
    <>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-slate-800">Projects</CardTitle>
          <Button variant="ghost" className="text-blue-600 hover:text-blue-700">
            Add More
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {projects.map((project, index) => (
            <div key={index} className="relative pl-6 border-l-2 border-blue-200 hover:border-blue-400 transition-colors">
              <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-blue-600"></div>
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4">
                <h3 className="font-medium text-slate-800">{project.name}</h3>
                <div className="flex flex-wrap gap-2 mt-2">
                  {project.technologies.map((tech, techIndex) => (
                    <span 
                      key={techIndex}
                      className="px-2.5 py-1 bg-white/50 rounded-full text-sm font-medium text-slate-600"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
                <p className="text-slate-600 mt-3">{project.description}</p>
                {project.link && (
                  <a 
                    href={project.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center mt-3 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
                  >
                    View Project
                    <svg
                      className="w-4 h-4 ml-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M14 5l7 7m0 0l-7 7m7-7H3"
                      />
                    </svg>
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </>
  );
};

export default CandidateReport;