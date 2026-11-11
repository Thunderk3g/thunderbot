import type { Metadata, Viewport } from "next";
import { Bricolage_Grotesque } from "next/font/google";
import "./globals.css";

// One variable family for everything (docs/design.md). The width and optical-size axes give the narrow,
// heavy money figures; latin-ext carries the rupee sign.
const bricolage = Bricolage_Grotesque({
  subsets: ["latin", "latin-ext"], axes: ["opsz", "wdth"], variable: "--font-bricolage", display: "swap",
});

export const metadata: Metadata = {
  title: "Thunderbot",
  description: "Your ETF investing bot: what you hold, when it acts next, and what to do now",
  robots: { index: false, follow: false },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#eef2f5" },
    { media: "(prefers-color-scheme: dark)", color: "#0a1c28" },
  ],
};

// Apply the saved theme before paint so there's no flash.
const themeScript = `try{var t=localStorage.getItem("tb-theme");if(t)document.documentElement.dataset.theme=t}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={bricolage.variable} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
