import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Header() {
  return (
    <header className="bg-transparent py-6">
      <div className="container mx-auto px-4 flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-white hover:opacity-80 transition-opacity">
          vSmart Match
        </Link>
        <nav>
          <ul className="flex space-x-4">
            <li>
              <Link href="/about">
                <Button 
                  variant="ghost" 
                  className="text-white bg-transparent hover:bg-white/10 hover:text-white backdrop-blur-sm transition-all duration-200"
                >
                  About
                </Button>
              </Link>
            </li>
            <li>
              <Link href="/features">
                <Button 
                  variant="ghost" 
                  className="text-white bg-transparent hover:bg-white/10 hover:text-white backdrop-blur-sm transition-all duration-200"
                >
                  Features
                </Button>
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  )
}