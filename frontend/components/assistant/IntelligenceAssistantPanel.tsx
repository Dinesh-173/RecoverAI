"use client";

import React, { useState, useEffect, useRef } from "react";
import { usePathname, useRouter } from "next/navigation";
import {
  Bot,
  X,
  Send,
  Sparkles,
  RefreshCw,
  Trash2,
  ShieldCheck,
  ExternalLink,
  ChevronRight,
  HelpCircle,
  BarChart3,
  Presentation,
} from "lucide-react";
import { api } from "@/lib/api-client";
import {
  AssistantChatResponse,
  AssistantCitation,
  SuggestedAction,
  ToolExecutionLog,
} from "@/lib/types";

interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  toolsUsed?: ToolExecutionLog[];
  citations?: AssistantCitation[];
  suggestedActions?: SuggestedAction[];
  timestamp: string;
}

export function IntelligenceAssistantPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputMsg, setInputMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [presentationMode, setPresentationMode] = useState(false);
  const [conversationId, setConversationId] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const pathname = usePathname();
  const router = useRouter();
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Derive Page Context & Entity ID
  const getContextFromPath = (): { pageContext: string; entityId?: string } => {
    if (!pathname) return { pageContext: "dashboard" };
    if (pathname === "/dashboard") return { pageContext: "dashboard" };
    if (pathname === "/transactions") return { pageContext: "transactions" };
    if (pathname === "/simulation") return { pageContext: "simulation" };
    if (pathname === "/analytics") return { pageContext: "analytics" };
    if (pathname === "/approvals") return { pageContext: "approvals" };
    if (pathname === "/audit-logs") return { pageContext: "audit_logs" };
    if (pathname.startsWith("/recovery-cases/")) {
      const parts = pathname.split("/");
      const caseId = parts[parts.length - 1];
      return { pageContext: "recovery_case", entityId: caseId };
    }
    return { pageContext: "general" };
  };

  const { pageContext, entityId } = getContextFromPath();

  // Initial Welcome Message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: "welcome-1",
          sender: "assistant",
          text:
            "👋 **Hello! I am RecoverAI Intelligence Assistant**, your context-aware operating companion.\n\n" +
            "I can analyze live revenue at risk, explain ML recoverability scores (**ROC-AUC 0.8332**), walk through Policy Engine decisions, and guide simulation testing.\n\n" +
            "> 🛡️ *Note: AI recommendations are advisory. Deterministic Policy Engine rules control all financial decisions.*",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          suggestedActions: [
            { label: "Explain Dashboard", action_type: "PROMPT", payload: { prompt: "Explain our current dashboard metrics" } },
            { label: "Why did Policy Engine stop case?", action_type: "PROMPT", payload: { prompt: "Why does Policy Engine stop certain transactions?" } },
            { label: "Explain Model ROC-AUC", action_type: "PROMPT", payload: { prompt: "What does ROC-AUC 0.8332 mean?" } },
            { label: "Check System Health", action_type: "PROMPT", payload: { prompt: "Check system health" } },
          ],
        },
      ]);
    }
  }, [messages.length]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSendMessage = async (customText?: string) => {
    const textToSend = customText || inputMsg;
    if (!textToSend.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: `usr_${Date.now()}`,
      sender: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!customText) setInputMsg("");
    setLoading(true);

    try {
      const res: AssistantChatResponse = await api.sendAssistantMessage({
        message: textToSend,
        conversation_id: conversationId || undefined,
        page_context: pageContext,
        entity_id: entityId,
        presentation_mode: presentationMode,
      });

      if (res.conversation_id) {
        setConversationId(res.conversation_id);
      }

      const assistantMessage: ChatMessage = {
        id: `asst_${Date.now()}`,
        sender: "assistant",
        text: res.message,
        toolsUsed: res.tools_used,
        citations: res.citations,
        suggestedActions: res.suggested_actions,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: `err_${Date.now()}`,
        sender: "assistant",
        text: `⚠️ **Connection Error**: I couldn't reach the RecoverAI backend assistant engine (${err.message || "Network Error"}). Please verify backend server is active on port 8000.`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleActionClick = (action: SuggestedAction) => {
    if (action.action_type === "NAVIGATE" && action.payload?.route) {
      router.push(action.payload.route);
    } else if (action.action_type === "PROMPT" && action.payload?.prompt) {
      handleSendMessage(action.payload.prompt);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setConversationId("");
  };

  return (
    <>
      {/* Floating Trigger Widget Button */}
      <div className="fixed bottom-6 right-6 z-50">
        {!isOpen && (
          <button
            id="recoverai-assistant-toggle-btn"
            onClick={() => setIsOpen(true)}
            className="flex items-center gap-2.5 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium rounded-full shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all transform hover:scale-105 active:scale-95 border border-blue-400/30"
          >
            <div className="relative">
              <Bot className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 rounded-full animate-ping" />
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 rounded-full" />
            </div>
            <span className="text-sm font-semibold tracking-wide">RecoverAI AI</span>
            <span className="text-xs bg-blue-700/60 px-2 py-0.5 rounded-full border border-blue-400/30 text-blue-100">
              Copilot
            </span>
          </button>
        )}
      </div>

      {/* Floating Chat Drawer Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-full max-w-[460px] h-[640px] max-h-[85vh] bg-slate-900/95 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3.5 bg-slate-950/80 border-b border-slate-800/80">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-gradient-to-br from-blue-500/20 to-indigo-500/20 border border-blue-500/30 rounded-xl">
                <Bot className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-slate-100">RecoverAI Intelligence Assistant</h3>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                    ADVISORY
                  </span>
                </div>
                <div className="flex items-center gap-1.5 mt-0.5 text-xs text-slate-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
                  <span>Context: <strong className="text-blue-300 capitalize">{pageContext.replace("_", " ")}</strong></span>
                  {entityId && <span className="text-slate-500">({entityId.substring(0, 10)})</span>}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={() => setPresentationMode(!presentationMode)}
                title="Toggle Presentation / Pitch Mode"
                className={`p-1.5 rounded-lg border text-xs flex items-center gap-1 transition ${
                  presentationMode
                    ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                    : "bg-slate-800/50 text-slate-400 border-slate-700 hover:text-slate-200"
                }`}
              >
                <Presentation className="w-3.5 h-3.5" />
                <span className="text-[11px] font-medium hidden sm:inline">Pitch Mode</span>
              </button>

              <button
                onClick={clearChat}
                title="Clear Conversation"
                className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition"
              >
                <Trash2 className="w-4 h-4" />
              </button>

              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick Prompt Chips */}
          <div className="flex items-center gap-1.5 px-3 py-2 bg-slate-900/60 border-b border-slate-800/50 overflow-x-auto no-scrollbar">
            <span className="text-[11px] text-slate-500 font-medium whitespace-nowrap pl-1">Prompts:</span>
            <button
              onClick={() => handleSendMessage("Explain our current revenue at risk and recovery metrics")}
              className="text-xs px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-blue-600/30 text-slate-300 hover:text-blue-200 border border-slate-700/60 transition whitespace-nowrap"
            >
              📊 Revenue Analysis
            </button>
            <button
              onClick={() => handleSendMessage("What does ROC-AUC 0.8332 mean for our ML model?")}
              className="text-xs px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-blue-600/30 text-slate-300 hover:text-blue-200 border border-slate-700/60 transition whitespace-nowrap"
            >
              🤖 Explain ML Model
            </button>
            <button
              onClick={() => handleSendMessage("Why did Policy Engine escalate or stop transactions?")}
              className="text-xs px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-blue-600/30 text-slate-300 hover:text-blue-200 border border-slate-700/60 transition whitespace-nowrap"
            >
              🛡️ Policy Rules
            </button>
            <button
              onClick={() => handleSendMessage("How do I test custom transaction data in simulation?")}
              className="text-xs px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-blue-600/30 text-slate-300 hover:text-blue-200 border border-slate-700/60 transition whitespace-nowrap"
            >
              🧪 Simulation Guide
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
              >
                <div className="flex items-center gap-1.5 mb-1 px-1">
                  <span className="text-[10px] text-slate-500 font-medium">
                    {msg.sender === "user" ? "You" : "RecoverAI AI"}
                  </span>
                  <span className="text-[10px] text-slate-600">• {msg.timestamp}</span>
                </div>

                <div
                  className={`max-w-[90%] p-3.5 rounded-2xl text-xs leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-blue-600 text-white rounded-tr-none shadow-md shadow-blue-600/10"
                      : "bg-slate-800/90 text-slate-200 border border-slate-700/60 rounded-tl-none"
                  }`}
                >
                  <div className="whitespace-pre-wrap font-sans">{msg.text}</div>

                  {/* Tool Execution Transparency Badges */}
                  {msg.toolsUsed && msg.toolsUsed.length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-slate-700/50 space-y-1">
                      <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                        Verified Data Tools Used:
                      </div>
                      {msg.toolsUsed.map((t, idx) => (
                        <div
                          key={idx}
                          className="flex items-center gap-1.5 text-[11px] text-blue-300/90 bg-blue-950/40 px-2 py-0.5 rounded border border-blue-800/40"
                        >
                          <ShieldCheck className="w-3 h-3 text-blue-400" />
                          <span className="font-mono text-[10px] text-blue-200">{t.tool_name}</span>
                          <span className="text-slate-400 text-[10px]">- {t.summary}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {msg.citations.map((c, idx) => (
                        <span
                          key={idx}
                          className="text-[10px] px-2 py-0.5 bg-slate-900/80 text-slate-400 rounded border border-slate-700/60 flex items-center gap-1"
                        >
                          <BarChart3 className="w-2.5 h-2.5 text-slate-400" />
                          <span>Source: {c.title}</span>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Suggested Action Chips */}
                {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5 pl-1">
                    {msg.suggestedActions.map((act, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleActionClick(act)}
                        className="text-[11px] px-2.5 py-1 bg-slate-800/90 hover:bg-blue-600/30 text-blue-300 hover:text-blue-100 rounded-lg border border-blue-500/30 transition flex items-center gap-1"
                      >
                        <span>{act.label}</span>
                        <ChevronRight className="w-3 h-3 text-blue-400" />
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Loading Spinner */}
            {loading && (
              <div className="flex items-center gap-2 text-slate-400 text-xs py-2 px-1">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-blue-400" />
                <span>Analyzing page context and querying verified RecoverAI tools...</span>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Footer Input Bar */}
          <div className="p-3 bg-slate-950/90 border-t border-slate-800/80 flex items-center gap-2">
            <input
              type="text"
              value={inputMsg}
              onChange={(e) => setInputMsg(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder={
                pageContext === "recovery_case"
                  ? "Ask about this case or decision rationale..."
                  : "Ask about revenue, ML scores, or policy rules..."
              }
              className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/60 focus:ring-1 focus:ring-blue-500/30"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputMsg.trim() || loading}
              className="p-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:hover:bg-blue-600 text-white rounded-xl transition shadow-md shadow-blue-600/20"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
