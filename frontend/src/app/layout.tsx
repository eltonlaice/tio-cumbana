import type { Metadata } from "next";
import { Fraunces, Albert_Sans } from "next/font/google";
import "./globals.css";

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  axes: ["SOFT", "opsz"],
});

const albertSans = Albert_Sans({
  variable: "--font-albert-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Tio Cumbana",
  description:
    "An agronomist that watches, remembers, and calls you first.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pt"
      className={`${fraunces.variable} ${albertSans.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-sisal text-preto-terra">
        {children}
      </body>
    </html>
  );
}
