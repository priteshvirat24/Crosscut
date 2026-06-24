import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/layout/Header";

// Using Inter at weight 500/400 as a substitute for FerrariSans
const inter = Inter({ subsets: ["latin"], weight: ["400", "500", "600", "700"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "Crosscut — Run only the tests that matter",
  description: "Crosscut uses GitLab Orbit to intelligently select and run only the tests impacted by your code changes.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased`}>
        <Header />
        <main className="pt-16"> {/* 64px header height */}
          {children}
        </main>
      </body>
    </html>
  );
}
