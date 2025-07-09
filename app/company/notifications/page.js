"use client"

import { useState } from "react"
import { Bell, Users, MessageCircle } from 'lucide-react'
import Header from "@/components/Header"
import CompanyNavBar from '@/components/CompanyNavBar';

export default function Notifications() {
  const [message, setMessage] = useState("")
  const [recipients, setRecipients] = useState([])

  const recipientOptions = [
    { value: "all", label: "All Candidates", description: "Send to every candidate in the system" },
    { value: "matched", label: "Matched Candidates", description: "Only candidates that match your job requirements" },
    { value: "shortlisted", label: "Shortlisted Candidates", description: "Candidates you've marked as potential fits" }
  ]

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log("Sending notification:", { message, recipients })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#c6269e] to-[#4f46e5]">
      <Header />
      <div className="container mx-auto px-4">
        <CompanyNavBar />
        <main className="py-16">
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-12 animate-fade-in-up">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
                Send Notifications
              </h1>
              <p className="text-lg text-white/80">
                Communicate with your candidates efficiently
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-xl animate-fade-in-up animation-delay-200">
              <form onSubmit={handleSubmit} className="space-y-8">
                <div className="space-y-6">
                  <div>
                    <label className="flex items-center text-white text-lg font-medium mb-4">
                      <Users className="w-5 h-5 mr-2" />
                      Select Recipients
                    </label>
                    <div className="grid gap-4">
                      {recipientOptions.map((option) => (
                        <label
                          key={option.value}
                          className="relative flex items-start p-4 rounded-lg bg-white/5 border border-white/10 cursor-pointer hover:bg-white/10 transition-all"
                        >
                          <div className="flex items-center h-5">
                            <input
                              type="checkbox"
                              value={option.value}
                              checked={recipients.includes(option.value)}
                              onChange={(e) => {
                                const value = e.target.value
                                setRecipients(prev =>
                                  prev.includes(value)
                                    ? prev.filter(r => r !== value)
                                    : [...prev, value]
                                )
                              }}
                              className="form-checkbox h-4 w-4 text-pink-500 rounded border-white/30 focus:ring-pink-500"
                            />
                          </div>
                          <div className="ml-3">
                            <span className="text-white font-medium">{option.label}</span>
                            <p className="text-white/60 text-sm">{option.description}</p>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label htmlFor="message" className="flex items-center text-white text-lg font-medium mb-2">
                      <MessageCircle className="w-5 h-5 mr-2" />
                      Message
                    </label>
                    <textarea
                      id="message"
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      required
                      placeholder="Type your message here..."
                      className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/20 transition-all h-40"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-pink-500 to-violet-500 text-white py-4 px-6 rounded-lg font-semibold hover:from-pink-600 hover:to-violet-600 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center"
                >
                  <Bell className="w-5 h-5 mr-2" />
                  Send Notification
                </button>
              </form>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}