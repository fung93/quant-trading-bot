"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

/** Re-runs the server fetches (health + candles). No polling by design. */
export default function RefreshButton() {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  return (
    <button
      type="button"
      onClick={() => startTransition(() => router.refresh())}
      disabled={isPending}
      className="rounded-md border border-white/15 px-3 py-1 text-xs text-gray-300 hover:bg-white/5 disabled:opacity-50"
    >
      <span className={`mr-1 inline-block ${isPending ? "animate-spin" : ""}`} aria-hidden>
        ↻
      </span>
      {isPending ? "Refreshing" : "Refresh"}
    </button>
  );
}
