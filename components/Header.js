import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Header() {
  return (
    <header className="bg-transparent py-6">
      <div className="container mx-auto px-4 flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-white">
          vSmart Match
        </Link>
        <nav>
          <ul className="flex space-x-4">
            <li>
              <Button variant="ghost" className="text-white hover:text-gray-200">
                About
              </Button>
            </li>
            <li>
              <Button variant="ghost" className="text-white hover:text-gray-200">
                Features
              </Button>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  )
}