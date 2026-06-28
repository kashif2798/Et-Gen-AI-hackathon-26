import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "E-newspaper | AI-Native News Platform",
  description: "Hyper-personalized, context-aware news intelligence powered by multi-agent AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light">
      <body className="antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
