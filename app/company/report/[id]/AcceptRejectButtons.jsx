//AcceptRejectButtons.jsx

"use client"
import { useState, useTransition, useEffect } from "react"
import { Button } from "@/components/ui/button"

// Get API base URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function AcceptRejectButtons({ matchId, initialSelection }) {
  const [pending, startTransition] = useTransition();
  const [status, setStatus] = useState(initialSelection || null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setStatus(initialSelection || null);
  }, [initialSelection]);

  const handleSelection = (selection) => {
    setStatus(null);
    setError(null);
    startTransition(async () => {
      try {
        const res = await fetch(`${API_URL}/api/match/${matchId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ selection }),
        });
        if (!res.ok) throw new Error('Failed to update selection');
        setStatus(selection);
      } catch (err) {
        setError(err.message || 'Error updating selection');
      }
    });
  };

  if (status === 'yes' || status === 'no') {
    return (
      <span
        className={`ml-2 font-medium px-3 py-1 rounded-lg shadow bg-white/90 ${status === 'yes' ? 'text-green-600' : 'text-red-600'}`}
        style={{ display: 'inline-block' }}
      >
        {status === 'yes' ? 'Accepted' : 'Rejected'}
      </span>
    );
  }

  return (
    <div className="flex gap-2 items-center">
      <Button
        variant={status === 'yes' ? 'default' : 'outline'}
        className="bg-green-500 text-white hover:bg-green-600"
        disabled={pending}
        onClick={() => handleSelection('yes')}
      >
        Accept
      </Button>
      <Button
        variant={status === 'no' ? 'default' : 'outline'}
        className="bg-red-500 text-white hover:bg-red-600"
        disabled={pending}
        onClick={() => handleSelection('no')}
      >
        Reject
      </Button>
      {error && <span className="ml-2 text-red-500">{error}</span>}
    </div>
  );
}
