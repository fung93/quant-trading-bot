import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "quant-bot monitor",
  description: "BTC/ETH candle pipeline monitor",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <nav className="mx-auto flex w-full max-w-4xl gap-4 px-4 pt-3 text-sm text-gray-400">
          <a href="/" className="hover:text-gray-200">monitor</a>
          <a href="/signals" className="hover:text-gray-200">signals</a>
          <a href="/log" className="hover:text-gray-200">log</a>
        </nav>
        {children}
      </body>
    </html>
  );
}
