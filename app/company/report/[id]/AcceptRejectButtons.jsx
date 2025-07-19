//AcceptRejectButtons.jsx

"use client"
import { useState, useTransition, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/lib/useAuth"
import { useApiClient } from "@/lib/clientApiClient"

export default function AcceptRejectButtons({ matchId, initialSelection }) {
  const [pending, startTransition] = useTransition();
  const [status, setStatus] = useState(initialSelection || null);
  const [error, setError] = useState(null);
  const { user } = useAuth();
  const api = useApiClient(user);

  useEffect(() => {
    setStatus(initialSelection || null);
  }, [initialSelection]);

  const handleSelection = (selection) => {
    setStatus(null);
    setError(null);
    startTransition(async () => {
      try {
        await api.patch(`/api/match/${matchId}`, { selection });
        setStatus(selection);
      } catch (err) {
        setError(err.userMessage || 'Error updating selection');
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
