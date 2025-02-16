import Header from "@/components/Header"
import { ArrowRight, Database, Search, Network, FileText, BarChart2, Cpu } from "lucide-react"

const features = [
  {
    icon: Database,
    step: "01",
    title: "Data Collection & Preprocessing",
    description: "Collect and structure resumes and job descriptions through our intelligent parsing system.",
  },
  {
    icon: Search,
    step: "02",
    title: "BM25-Based Keyword Matching",
    description: "Index and retrieve candidates using advanced keyword overlap algorithms for initial matching.",
  },
  {
    icon: Network,
    step: "03",
    title: "Knowledge Graph Expansion",
    description: "Expand skill requirements using a comprehensive knowledge graph for better matching accuracy.",
  },
  {
    icon: FileText,
    step: "04",
    title: "Text to Embeddings",
    description: "Create dense vector embeddings for texts to enable semantic matching capabilities.",
  },
  {
    icon: BarChart2,
    step: "05",
    title: "Feature Extraction for Ranking",
    description: "Extract sophisticated features to power our advanced ranking model.",
  },
  {
    icon: Cpu,
    step: "06",
    title: "Train & Deploy Ranking Model",
    description: "Deploy our trained ranking model to provide accurate candidate-job matches.",
  },
]

export default function Features() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16 text-white">
        {/* Hero Section */}
        <section className="mb-20 animate-fade-in-up">
          <h1 className="text-5xl md:text-7xl font-bold mb-8">Our Technology</h1>
          <p className="text-xl md:text-2xl max-w-3xl">
            Discover how vSmart Match uses cutting-edge AI and machine learning to revolutionize the hiring process.
          </p>
        </section>

        {/* Features Grid */}
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={feature.step}
              className="bg-white/10 backdrop-blur-lg rounded-xl p-6 transform hover:scale-105 transition-transform duration-300 animate-fade-in-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-center mb-4">
                <div className="bg-white/20 rounded-lg p-3 mr-4">
                  <feature.icon className="h-6 w-6" />
                </div>
                <span className="text-lg font-semibold text-white/60">Step {feature.step}</span>
              </div>
              <h3 className="text-2xl font-bold mb-4">{feature.title}</h3>
              <p className="text-white/80 mb-6">{feature.description}</p>
              <div className="mt-auto">
                <button className="group flex items-center text-white/60 hover:text-white transition-colors">
                  Learn more
                  <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                </button>
              </div>
            </div>
          ))}
        </section>

        {/* Technology Stack */}
        <section className="mt-20 animate-fade-in-up animation-delay-700">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 md:p-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-8">Our Tech Stack</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {/* Replace with actual tech stack logos */}
              {[1, 2, 3, 4].map((item) => (
                <div key={item} className="flex flex-col items-center p-4 bg-white/5 rounded-lg">
                  <img
                    src={`/placeholder.svg?height=80&width=80`}
                    alt={`Technology ${item}`}
                    className="h-20 w-20 mb-4"
                  />
                  <span className="text-lg font-semibold">Technology {item}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

