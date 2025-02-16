"use client"

import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { BookOpen, GitBranch, Star, Code, Award, FileText, BriefcaseIcon, GraduationCap, UserCircle, Download, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import Header from '@/components/Header';

const CompanyCandidateReport = () => {
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
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
      </div>
    );
  }

  const handleExportPDF = () => {
    // Implement PDF export functionality
    console.log('Exporting PDF...');
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-purple-600 to-fuchsia-600">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Candidate Report</h1>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-lg font-semibold text-white bg-green-500 px-3 py-1 rounded-full">92% Match</span>
              <CheckCircle className="w-5 h-5 text-white" />
            </div>
          </div>
          <Button 
            onClick={handleExportPDF}
            className="bg-white text-purple-700 hover:bg-gray-100"
          >
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <ProfileCard data={reportData?.profile} />
          <GithubStatsCard data={reportData?.github} />
          <LeetcodeStatsCard data={reportData?.leetcode} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SkillsCard skills={reportData?.skills} jobRequiredSkills={["JavaScript", "React", "Node.js", "AWS"]} />
          <ExperienceCard experience={reportData?.experience} jobKeywords={["SaaS", "microservices", "React", "Node.js"]} />
          <EducationCard education={reportData?.education} />
          <ProjectsCard projects={reportData?.projects} jobKeywords={["React", "Node.js", "AWS"]} />
        </div>
      </main>
    </div>
  );
};

const ProfileCard = ({ data }) => {
  if (!data) return null;

  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Profile</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="bg-gradient-to-r from-purple-600 to-fuchsia-600 text-white p-3 rounded-full">
              <UserCircle className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-semibold">{data.name}</h3>
              <p className="text-gray-600">{data.title}</p>
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-gray-600">{data.location}</p>
            <p className="text-sm text-gray-600">{data.email}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// GitHub and LeetCode cards with updated styling
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
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">GitHub Statistics</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center p-3 bg-gray-50 rounded">
            <GitBranch className="w-6 h-6 mx-auto mb-1 text-purple-600" />
            <div className="text-sm text-gray-600">Repositories</div>
            <div className="font-semibold">{data.repositories}</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded">
            <Star className="w-6 h-6 mx-auto mb-1 text-purple-600" />
            <div className="text-sm text-gray-600">Stars</div>
            <div className="font-semibold">{data.stars}</div>
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-600 mb-2">Most Used Languages</div>
          <ResponsiveContainer width="100%" height={100}>
            <BarChart data={data.languages}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="percentage" fill="#c026d3" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
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
        className="bg-white"
      />
    );
  }

  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">LeetCode Statistics</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-sm text-gray-600">Easy</div>
            <div className="font-semibold text-green-600">{data.solved.easy}</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-sm text-gray-600">Medium</div>
            <div className="font-semibold text-yellow-600">{data.solved.medium}</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-sm text-gray-600">Hard</div>
            <div className="font-semibold text-red-600">{data.solved.hard}</div>
          </div>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Contest Rating</span>
            <span className="font-semibold">{data.contestRating}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Global Ranking</span>
            <span className="font-semibold">Top {data.globalRanking}%</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const EmptyCard = ({ title, icon: Icon, buttonText, onClick, className = "" }) => {
  return (
    <Card className={`bg-white overflow-hidden ${className}`}>
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">{title}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center py-8">
        <Icon className="w-12 h-12 text-gray-300 mb-4" />
        <p className="text-gray-500 mb-4 text-center">No {title.toLowerCase()} data available</p>
        <Button onClick={onClick} variant="outline">
          {buttonText}
        </Button>
      </CardContent>
    </Card>
  );
};

const SkillsCard = ({ skills, jobRequiredSkills }) => {
  if (!skills?.length) return null;

  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Skills</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="flex flex-wrap gap-2">
          {skills.map((skill, index) => {
            const isMatch = jobRequiredSkills.includes(skill);
            return (
              <span
                key={index}
                className={`px-3 py-1 rounded-full ${
                  isMatch 
                    ? 'bg-green-100 text-green-700 border border-green-300' 
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {skill}
                {isMatch && <CheckCircle className="w-3 h-3 inline ml-1" />}
              </span>
            );
          })}
        </div>
        <div className="mt-4">
          <p className="text-sm text-gray-600 mb-2">Match with Job Requirements</p>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-green-600 h-2.5 rounded-full" 
              style={{ width: `${(skills.filter(s => jobRequiredSkills.includes(s)).length / jobRequiredSkills.length) * 100}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {skills.filter(s => jobRequiredSkills.includes(s)).length} out of {jobRequiredSkills.length} required skills
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

const ExperienceCard = ({ experience, jobKeywords }) => {
  if (!experience?.length) return null;

  const highlightText = (text, keywords) => {
    let highlightedText = text;
    keywords.forEach(keyword => {
      const regex = new RegExp(`(${keyword})`, 'gi');
      highlightedText = highlightedText.replace(regex, '<span class="text-green-600 font-medium">$1</span>');
    });
    return <div dangerouslySetInnerHTML={{ __html: highlightedText }} />;
  };

  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Work Experience</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="space-y-4">
          {experience.map((exp, index) => (
            <div key={index} className="border-l-2 border-purple-600 pl-4">
              <h3 className="font-medium text-gray-900">{exp.title}</h3>
              <p className="text-gray-600">{exp.company}</p>
              <p className="text-sm text-gray-500">
                {exp.startDate} - {exp.endDate || 'Present'}
              </p>
              <div className="text-gray-700 mt-2">
                {highlightText(exp.description, jobKeywords)}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
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
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Education</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="space-y-4">
          {education.map((edu, index) => (
            <div key={index} className="border-l-2 border-purple-600 pl-4">
              <h3 className="font-medium text-gray-900">{edu.degree}</h3>
              <p className="text-gray-600">{edu.school}</p>
              <p className="text-sm text-gray-500">{edu.graduationYear}</p>
              {edu.gpa && (
                <p className="text-gray-700 mt-1">GPA: {edu.gpa}</p>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

const ProjectsCard = ({ projects, jobKeywords }) => {
  if (!projects?.length) return null;

  const highlightText = (text, keywords) => {
    let highlightedText = text;
    keywords.forEach(keyword => {
      const regex = new RegExp(`(${keyword})`, 'gi');
      highlightedText = highlightedText.replace(regex, '<span class="text-green-600 font-medium">$1</span>');
    });
    return <div dangerouslySetInnerHTML={{ __html: highlightedText }} />;
  };

  return (
    <Card className="bg-white overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-fuchsia-600">
        <CardTitle className="text-white">Projects</CardTitle>
      </CardHeader>
      <CardContent className="mt-4">
        <div className="space-y-4">
          {projects.map((project, index) => (
            <div key={index} className="border-l-2 border-purple-600 pl-4">
              <h3 className="font-medium text-gray-900">{project.name}</h3>
              <div className="flex items-center flex-wrap gap-2 mt-1">
                {project.technologies.map((tech, techIndex) => (
                  <span 
                    key={techIndex}
                    className={`text-xs px-2 py-1 rounded-full ${
                      jobKeywords.includes(tech)
                        ? 'bg-green-100 text-green-700 border border-green-300'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {tech}
                  </span>
                ))}
              </div>
              <div className="text-gray-700 mt-2">
                {highlightText(project.description, jobKeywords)}
              </div>
              {project.link && (
                <a 
                  href={project.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-purple-600 hover:text-purple-800 mt-2 inline-block"
                >
                  View Project →
                </a>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default CompanyCandidateReport;