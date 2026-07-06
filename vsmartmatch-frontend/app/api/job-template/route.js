// app/api/job-template/route.js
import { NextResponse } from 'next/server'

// Dummy database of job templates with detailed descriptions and requirements
const jobTemplates = {
  "Software Engineer": {
    description: 
`We are looking for a Software Engineer to join our dynamic team. In this role, you will:

- Design, develop, and maintain high-quality software
- Collaborate with cross-functional teams to define, design, and ship new features
- Identify and address performance bottlenecks and bugs
- Continuously discover, evaluate, and implement new technologies
- Participate in code reviews and provide constructive feedback to other developers

You'll be working in an agile environment with the latest technologies and will have the opportunity to contribute to the architecture and design of our systems.`,
    requirements:
`Requirements:
- Bachelor's degree in Computer Science, Engineering, or a related field (or equivalent practical experience)
- 2+ years of professional software development experience
- Proficiency in at least one modern programming language (e.g., Python, Java, C++, JavaScript)
- Strong understanding of data structures, algorithms, and software design principles
- Experience with version control systems (Git)
- Excellent problem-solving skills
- Strong communication and collaboration abilities

Preferred Qualifications:
- Experience with cloud platforms (AWS, GCP, or Azure)
- Knowledge of containerization technologies (Docker, Kubernetes)
- Understanding of CI/CD pipelines
- Experience with microservices architecture
- Open source contributions
`
  },
  
  "Full Stack Developer": {
    description:
`We're seeking a skilled Full Stack Developer to build and maintain web applications from front to back. In this role, you will:

- Develop responsive and user-friendly web interfaces
- Design and implement RESTful APIs and backend services
- Work with databases to store and retrieve data efficiently
- Ensure application security and performance
- Collaborate with designers and product managers to implement new features
- Debug and fix issues across the entire stack
- Write clean, maintainable, and well-documented code

You'll have the opportunity to work with modern frameworks and technologies while contributing to all aspects of our product development lifecycle.`,
    requirements:
`Requirements:
- 3+ years of experience in full stack development
- Strong proficiency in JavaScript/TypeScript and at least one modern frontend framework (React, Angular, or Vue)
- Experience with server-side languages like Node.js, Python, Ruby, or PHP
- Familiarity with database technologies (SQL and NoSQL)
- Understanding of web security best practices
- Experience with version control systems and collaborative development
- Knowledge of responsive design principles
- Excellent problem-solving and communication skills

Preferred Qualifications:
- Experience with cloud services (AWS, GCP, or Azure)
- Knowledge of DevOps practices and tools
- Understanding of performance optimization techniques
- Experience with testing frameworks and methodologies
- Contributions to open source projects
`
  },
  
  "Data Scientist": {
    description:
`We are looking for a talented Data Scientist to help us discover insights and solve business problems using data. Your primary focus will be:

- Developing advanced analytics models to address complex business challenges
- Mining and analyzing data to identify patterns and opportunities
- Building and implementing machine learning algorithms
- Creating data visualizations to communicate findings
- Collaborating with engineering teams to deploy models to production
- Staying up-to-date with the latest methodologies and technologies
- Providing data-driven recommendations to stakeholders

You will work in a collaborative environment and have the opportunity to make a significant impact on our product and business strategy through data-driven decisions.`,
    requirements:
`Requirements:
- Master's or PhD in Statistics, Mathematics, Computer Science, or related quantitative field
- 2+ years of professional experience in data science or related field
- Strong programming skills in Python or R, and SQL
- Experience with data visualization tools
- Proficiency in using statistical and machine learning techniques
- Excellent analytical and problem-solving skills
- Ability to communicate complex findings to non-technical stakeholders

Preferred Qualifications:
- Experience with big data technologies (Hadoop, Spark)
- Knowledge of deep learning frameworks (TensorFlow, PyTorch)
- Experience with cloud-based data platforms
- Understanding of experimental design and causal inference
- Industry experience in our specific domain
- Published research or contributions to the data science community
`
  },
  
  "Product Manager": {
    description:
`We're looking for a strategic Product Manager to lead the development of innovative products. In this role, you will:

- Define product vision, strategy, and roadmap
- Gather and prioritize product and customer requirements
- Work closely with engineering, design, and marketing teams to deliver successful products
- Define and analyze metrics that measure product success
- Conduct competitive analysis and market research
- Represent the voice of the customer throughout the product lifecycle
- Communicate product plans, benefits, and results to internal stakeholders

You will be responsible for guiding cross-functional teams from concept to launch, ensuring we build products that our customers love.`,
    requirements:
`Requirements:
- Bachelor's degree in Business, Engineering, Computer Science, or related field
- 3+ years of product management experience
- Demonstrated experience in successfully launching products
- Strong analytical and problem-solving abilities
- Excellent communication and presentation skills
- Ability to prioritize competing demands in a fast-paced environment
- Data-driven decision-making mindset
- User-centered design thinking

Preferred Qualifications:
- MBA or advanced degree
- Technical background or experience working with software development teams
- Experience with Agile/Scrum methodologies
- Knowledge of user research techniques and tools
- Experience with product analytics tools
- Industry-specific knowledge relevant to our business
`
  },
  
  "UI/UX Designer": {
    description:
`We are seeking a creative and user-focused UI/UX Designer to create exceptional user experiences. Your responsibilities will include:

- Designing intuitive, accessible, and visually appealing user interfaces
- Creating wireframes, prototypes, and high-fidelity mockups
- Conducting user research and usability testing
- Developing user personas and journey maps
- Collaborating with developers to implement designs
- Maintaining design systems and style guides
- Staying current with UX trends and best practices
- Iterating designs based on user feedback and analytics

You will play a crucial role in shaping how users interact with our products, ensuring they are both beautiful and functional.`,
    requirements:
`Requirements:
- Bachelor's degree in Design, HCI, or related field (or equivalent experience)
- 2+ years of experience in UI/UX design
- Proficiency with design and prototyping tools (Figma, Sketch, Adobe XD)
- Strong portfolio demonstrating your design process and solutions
- Understanding of user-centered design principles
- Knowledge of accessibility standards and best practices
- Excellent visual design skills with strong attention to detail
- Ability to give and receive constructive feedback

Preferred Qualifications:
- Experience with design systems and component libraries
- Knowledge of HTML, CSS, and basic front-end development
- Understanding of motion design and animation
- Experience conducting user research and usability testing
- Familiarity with data visualization design
- Knowledge of A/B testing and design metrics
`
  }
}

export async function GET(request) {
  const { searchParams } = new URL(request.url)
  const title = searchParams.get('title') || ''
  
  // Find an exact match or partial match
  const exactMatch = jobTemplates[title]
  if (exactMatch) {
    return NextResponse.json(exactMatch)
  }
  
  // Look for partial matches if no exact match
  for (const [key, template] of Object.entries(jobTemplates)) {
    if (title.toLowerCase().includes(key.toLowerCase()) || 
        key.toLowerCase().includes(title.toLowerCase())) {
      return NextResponse.json(template)
    }
  }
  
  // Return empty template if no match found
  return NextResponse.json({
    description: "",
    requirements: ""
  })
}