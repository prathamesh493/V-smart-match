import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "vSmart Match",
  description: "Precision hiring platform that matches candidates with job descriptions",
}

export default function RootLayout({ children }) {
  return (
    (<html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-white">{children}</div>
      </body>
    </html>)
  );
}

