// app/api/candidate/report/route.js
export async function GET() {
    // Mock data for development
    const mockData = {
      profile: {
        name: "Jane Smith",
        title: "Senior Full Stack Developer",
        location: "San Francisco, CA",
        email: "jane.smith@example.com",
        phone: "+1 (555) 123-4567"
      },
      github: {
        repositories: 48,
        stars: 237,
        languages: [
          { name: "JavaScript", percentage: 45 },
          { name: "Python", percentage: 30 },
          { name: "TypeScript", percentage: 15 },
          { name: "Java", percentage: 10 }
        ],
        contributions: 827,
        followers: 156
      },
      leetcode: {
        solved: {
          easy: 120,
          medium: 225,
          hard: 75
        },
        contestRating: 1856,
        globalRanking: 5,
        totalSolved: 420,
        acceptanceRate: 67.8
      },
      skills: [
        "JavaScript",
        "React",
        "Node.js",
        "Python",
        "AWS",
        "Docker",
        "TypeScript",
        "PostgreSQL",
        "GraphQL",
        "System Design"
      ],
      experience: [
        {
          title: "Senior Full Stack Developer",
          company: "TechCorp Inc.",
          location: "San Francisco, CA",
          startDate: "Jan 2021",
          endDate: null,
          description: "Lead developer for the company's main SaaS platform, managing a team of 5 developers and implementing microservices architecture."
        },
        {
          title: "Full Stack Developer",
          company: "StartupXYZ",
          location: "Seattle, WA",
          startDate: "Mar 2018",
          endDate: "Dec 2020",
          description: "Developed and maintained multiple client-facing applications using React and Node.js, improving system performance by 40%."
        },
        {
          title: "Software Engineer",
          company: "Tech Solutions Ltd",
          location: "Portland, OR",
          startDate: "Jun 2016",
          endDate: "Feb 2018",
          description: "Worked on backend systems using Python and Django, handling data processing for over 1M daily users."
        }
      ],
      education: [
        {
          degree: "Master of Science in Computer Science",
          school: "Stanford University",
          location: "Stanford, CA",
          graduationYear: "2016",
          gpa: "3.92"
        },
        {
          degree: "Bachelor of Science in Computer Engineering",
          school: "University of Washington",
          location: "Seattle, WA",
          graduationYear: "2014",
          gpa: "3.85"
        }
      ],
      projects: [
        {
          name: "E-commerce Platform",
          description: "Built a full-stack e-commerce platform with real-time inventory management and payment processing.",
          technologies: ["React", "Node.js", "MongoDB", "Stripe"],
          link: "https://github.com/janesmith/ecommerce-platform"
        },
        {
          name: "AI Image Recognition API",
          description: "Developed a REST API for image recognition using machine learning models, handling 100K+ requests daily.",
          technologies: ["Python", "TensorFlow", "Flask", "AWS"],
          link: "https://github.com/janesmith/ai-image-api"
        },
        {
          name: "DevOps Pipeline Tool",
          description: "Created an automated CI/CD pipeline tool used by 50+ development teams.",
          technologies: ["TypeScript", "Docker", "Jenkins", "Kubernetes"],
          link: "https://github.com/janesmith/devops-pipeline"
        }
      ],
      certifications: [
        {
          name: "AWS Certified Solutions Architect",
          issuer: "Amazon Web Services",
          date: "2023",
          link: "https://aws.amazon.com/certification/certified-solutions-architect-associate/"
        },
        {
          name: "Google Cloud Professional Developer",
          issuer: "Google",
          date: "2022",
          link: "https://cloud.google.com/certification/cloud-developer"
        }
      ]
    };
  
    // Simulate network delay for development
    await new Promise(resolve => setTimeout(resolve, 1000));
  
    return new Response(JSON.stringify(mockData), {
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }