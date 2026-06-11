"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";
import { TIMEFRAMES, type Timeframe } from "@/lib/data";

export default function TimeframeToggle({ active }: { active: Timeframe }) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  return (
    <div
      className={`inline-flex overflow-hidden rounded-md border border-white/15 text-sm transition-opacity ${
        isPending ? "opacity-50" : ""
      }`}
    >
      {TIMEFRAMES.map((tf) => (
        <button
          key={tf}
          type="button"
          onClick={() =>
            startTransition(() => router.push(`/?tf=${tf}`, { scroll: false }))
          }
          className={`px-4 py-1.5 font-mono ${
            tf === active
              ? "bg-white/15 text-white"
              : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
          }`}
        >
          {tf}
        </button>
      ))}
    </div>
  );
}
