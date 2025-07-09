import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navLinks = [
  { label: 'Dashboard', href: '/company' },
  { label: 'Upload Job Listing', href: '/company/upload' },
  { label: 'View Job Listings', href: '/company/listing' },
  { label: 'Notifications', href: '/company/notifications' },
];

export default function CompanyNavBar() {
  const pathname = usePathname();
  return (
    <nav className="flex gap-4 bg-white/80 rounded-xl shadow px-4 py-2 mb-8 mt-4">
      {navLinks.map(link => (
        <Link
          key={link.href}
          href={link.href}
          className={`font-medium px-3 py-1 rounded transition-colors ${pathname === link.href ? 'bg-indigo-500 text-white' : 'text-indigo-700 hover:bg-indigo-100'}`}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
