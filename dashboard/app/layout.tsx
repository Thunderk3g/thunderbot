import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Thunderbot",
  description: "Trading engine cockpit",
  robots: { index: false, follow: false },
};

// Apply the saved theme before paint so there's no flash.
const themeScript = `try{var t=localStorage.getItem("tb-theme");if(t)document.documentElement.dataset.theme=t}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
