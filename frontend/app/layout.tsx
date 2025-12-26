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
  title: "SmartWealth AI | 智慧存股領航員",
  description: "使用 AI 與數據科學打造的專業 ETF 投資分析平台。歷史回測、蒙地卡羅模擬、智能投資組合建議。",
  keywords: ["ETF", "投資", "台股", "回測", "蒙地卡羅", "0050", "0056", "00878"],
  authors: [{ name: "SmartWealth AI" }],
  openGraph: {
    title: "SmartWealth AI | 智慧存股領航員",
    description: "使用 AI 與數據科學打造的專業 ETF 投資分析平台",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-TW" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
