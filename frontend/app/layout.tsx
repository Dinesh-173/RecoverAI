import type { Metadata } from "next";
import "./globals.css";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { AppHeader } from "@/components/layout/AppHeader";
import { IntelligenceAssistantPanel } from "@/components/assistant/IntelligenceAssistantPanel";

export const metadata: Metadata = {
  title: "RecoverAI — Autonomous AI Revenue Recovery Agent",
  description: "Detect. Decide. Recover. Autonomous AI revenue recovery for merchants on Razorpay.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-foreground min-h-screen flex antialiased">
        <AppSidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <AppHeader />
          <main className="flex-1 overflow-y-auto p-8">{children}</main>
        </div>
        <IntelligenceAssistantPanel />
      </body>
    </html>
  );
}
