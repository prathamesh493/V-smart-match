import Link from "next/link"
import { Github, Linkedin, Mail } from "lucide-react"
import Header from "@/components/Header"

const teamMembers = [
  {
    name: "Gourav Goutam Midya",
    role: "AI/ML & Devops Enthusiast",
    image: "/team_photos/gourav.png",
    github: "https://github.com/GouravMidya",
    linkedin: "https://www.linkedin.com/in/gourav-midya/",
    email: "gouravgmidya@gmail.com",
  },
  {
    name: "Ayush Panigrahi",
    role: "Data Science + ML engineer",
    image: "/team_photos/ayush.jpg",
    github: "https://github.com/Ayushpani",
    linkedin:" https://in.linkedin.com/in/ayush-panigrahi-412501231",
    email: "ayushpanigrahi84@gmail.com",
  },
  {
    name: "Prathamesh Naik",
    role: "Full Stack Developer",
    image: "/team_photos/prathamesh.jpg",
    github: "https://github.com/prathamesh493",
    linkedin: "https://linkedin.com/in/prathameshnaik493",
    email: "prathameshnaik493@gmail.com",
},
  {
    name: "Meet Jamsutkar",
    role: "MLOPs and Open source Enthusiast",
    image: "/team_photos/meet.png",
    github: "https://github.com/MeJaM35",
    linkedin: "https://linkedin.com/in/meet-jamsutkar",
    email: "meetjamsutkar645@apsit.edu.in",
},
{
  name: "Krithik Patil",
  role: "Frontend Developer",
  image: "/team_photos/krithik.png",
  github: "https://github.com/KrithikPatil",
  linkedin: "https://www.linkedin.com/in/krithik-patil-554078249",
  email: "patilkrithik@gmail.com",
  },
]

export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <main className="container mx-auto px-4 py-16 text-white">
        {/* About Section */}
        <section className="mb-20 animate-fade-in-up">
          <h1 className="text-5xl md:text-7xl font-bold mb-8">About Us</h1>
          <p className="text-xl md:text-2xl max-w-3xl mb-12">
            We are Penta Generators, a team of passionate developers from APSIT college. Our mission is to revolutionize
            the hiring process through intelligent skill matching and automated candidate assessment.
          </p>
        </section>

        {/* Team Section */}
        <section className="animate-fade-in-up animation-delay-200">
          <h2 className="text-4xl font-bold mb-12">Meet Our Team</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {teamMembers.map((member, index) => (
              <div
                key={member.name}
                className="bg-white/10 backdrop-blur-lg rounded-xl p-6 transform hover:scale-105 transition-transform duration-300"
              >
                <img
                  src={member.image || "/placeholder.svg"}
                  alt={member.name}
                  className="w-48 h-48 rounded-full mx-auto mb-6 object-cover border-4 border-white/20"
                />
                <div className="text-center">
                  <h3 className="text-2xl font-bold mb-2">{member.name}</h3>
                  <p className="text-lg text-white/80 mb-4">{member.role}</p>
                  <div className="flex justify-center space-x-4">
                    <Link
                      href={member.github}
                      className="hover:text-white/80 transition-colors"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Github className="h-6 w-6" />
                      <span className="sr-only">GitHub</span>
                    </Link>
                    <Link
                      href={member.linkedin}
                      className="hover:text-white/80 transition-colors"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Linkedin className="h-6 w-6" />
                      <span className="sr-only">LinkedIn</span>
                    </Link>
                    <Link href={`mailto:${member.email}`} className="hover:text-white/80 transition-colors">
                      <Mail className="h-6 w-6" />
                      <span className="sr-only">Email</span>
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* College Section */}
        <section className="mt-20 animate-fade-in-up animation-delay-400">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 md:p-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Our Institution</h2>
            <div className="flex flex-col md:flex-row items-center gap-8">
              <img
                src="/apsit.jpg"
                alt="APSIT College"
                className="rounded-lg w-full md:w-1/2 object-cover"
              />
              <div>
                <h3 className="text-2xl font-bold mb-4">A.P. Shah Institute of Technology</h3>
                <p className="text-lg text-white/80">
                  We are proud students of APSIT, where innovation meets excellence. Our college has provided us with
                  the knowledge, resources, and support to bring vSmart Match to life.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

