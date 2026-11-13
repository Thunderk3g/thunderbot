import type { Metadata, Viewport } from "next";
import { Anek_Latin, Literata } from "next/font/google";
import "./globals.css";

// Two voices (docs/design.md). Anek Latin, by Ek Type in Mumbai, is the interface: its width axis gives the
// narrow, heavy money figures and the wide page titles. Literata is used for one thing only: words that an
// LLM wrote (italic for a line or two, upright in a callout for a longer passage), so the model's voice can
// never be mistaken for the rules'.
const anek = Anek_Latin({ subsets: ["latin", "latin-ext"], axes: ["wdth"], variable: "--font-anek", display: "swap" });
const literata = Literata({ subsets: ["latin", "latin-ext"], style: ["normal", "italic"], axes: ["opsz"], variable: "--font-literata", display: "swap" });

export const metadata: Metadata = {
  title: "Thunderbot",
  description: "A portfolio manager you run yourself: what you hold, what it will do next, and why",
  robots: { index: false, follow: false },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ece9f2" },
    { media: "(prefers-color-scheme: dark)", color: "#140d22" },
  ],
};

// Apply the saved theme before paint so there's no flash.
const themeScript = `try{var t=localStorage.getItem("tb-theme");if(t)document.documentElement.dataset.theme=t}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${anek.variable} ${literata.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
