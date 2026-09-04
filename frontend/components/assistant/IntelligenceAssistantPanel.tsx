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
  ChevronRight,
  ChevronDown,
  ChevronUp,
  BarChart3,
  Presentation,
  Copy,
  Check,
  Zap,
  CornerDownLeft,
} from "lucide-react";
import { api } from "@/lib/api-client";
import {
  AssistantChatResponse,
  AssistantCitation,
  SuggestedAction,
  ToolExecutionLog,
} from "@/lib/types";
import { MarkdownRenderer } from "./MarkdownRenderer";

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
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({});
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);

  const pathname = usePathname();
  const router = useRouter();
  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

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
            "I can analyze live revenue at risk, explain ML recoverability scores (**ROC-AUC 0.8332**), walk through Policy Engine decisions, and answer general technical or domain questions.\n\n" +
            "> 🛡️ *Note: AI recommendations are strictly advisory. RecoverAI's Policy Engine enforces all financial boundaries.*",
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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleActionClick = (action: SuggestedAction) => {
    if (action.action_type === "NAVIGATE" && action.payload?.route) {
      router.push(action.payload.route);
    } else if (action.action_type === "PROMPT" && action.payload?.prompt) {
      handleSendMessage(action.payload.prompt);
    }
  };

  const toggleTools = (msgId: string) => {
    setExpandedTools((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const copyMessageText = (text: string, msgId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(msgId);
    setTimeout(() => setCopiedMsgId(null), 2000);
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
            className="flex items-center gap-2.5 px-4 py-2.5 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary-hover hover:to-indigo-500 text-white font-medium rounded-full shadow-md shadow-primary/25 hover:shadow-primary/35 transition duration-150 active:scale-[0.98] border border-primary-light/30 backdrop-blur-md focus-ring"
          >
            <div className="relative">
              <Bot className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-emerald-400 rounded-full animate-pulse-subtle" />
            </div>
            <span className="text-sm font-semibold tracking-wide">RecoverAI Copilot</span>
            <span className="text-[10px] bg-primary-dark/60 px-2 py-0.5 rounded-full border border-primary-light/30 text-indigo-100 font-mono">
              AI
            </span>
          </button>
        )}
      </div>

      {/* Floating Chat Drawer Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-full max-w-[520px] h-[700px] max-h-[90vh] bg-slate-950/95 backdrop-blur-2xl border border-slate-700/80 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-slide-up ring-1 ring-white/10">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3.5 bg-slate-900/90 border-b border-borderSubtle">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-gradient-to-br from-primary/20 to-indigo-500/20 border border-primary/30 rounded-xl shadow-sm">
                <Bot className="w-5 h-5 text-primary-light" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-white">RecoverAI Intelligence Assistant</h3>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                    ADVISORY
                  </span>
                </div>
                <div className="flex items-center gap-1.5 mt-0.5 text-xs text-slate-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                  <span>Context: <strong className="text-primary-light capitalize">{pageContext.replace("_", " ")}</strong></span>
                  {entityId && <span className="text-slate-500 font-mono">({entityId.substring(0, 10)})</span>}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={() => setPresentationMode(!presentationMode)}
                title="Toggle Presentation / Pitch Mode"
                className={`p-1.5 rounded-xl border text-xs flex items-center gap-1 transition ${
                  presentationMode
                    ? "bg-amber-500/20 text-amber-300 border-amber-500/40 shadow-sm"
                    : "bg-surfaceSubtle text-slate-400 border-borderSubtle hover:text-slate-200"
                }`}
              >
                <Presentation className="w-3.5 h-3.5" />
                <span className="text-[11px] font-medium hidden sm:inline">Pitch Mode</span>
              </button>

              <button
                onClick={clearChat}
                title="Clear Conversation"
                className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-surfaceSubtle rounded-xl transition"
              >
                <Trash2 className="w-4 h-4" />
              </button>

              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 text-slate-400 hover:text-white hover:bg-surfaceSubtle rounded-xl transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick Prompt Chips */}
          <div className="flex items-center gap-1.5 px-3 py-2 bg-slate-900/60 border-b border-borderSubtle overflow-x-auto no-scrollbar">
            <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500 font-medium whitespace-nowrap pl-1">Prompts:</span>
            <button
              onClick={() => handleSendMessage("Explain our current revenue at risk and recovery metrics")}
              className="text-xs px-2.5 py-1 rounded-full bg-slate-900 hover:bg-primary/20 text-slate-300 hover:text-primary-light border border-borderSubtle hover:border-primary/40 transition duration-150 whitespace-nowrap active:scale-[0.98] focus-ring"
            >
              📊 Revenue Analysis
            </button>
            <button
              onClick={() => handleSendMessage("What does ROC-AUC 0.8332 mean for our ML model?")}
              className="text-xs px-2.5 py-1 rounded-full bg-slate-900 hover:bg-primary/20 text-slate-300 hover:text-primary-light border border-borderSubtle hover:border-primary/40 transition duration-150 whitespace-nowrap active:scale-[0.98] focus-ring"
            >
              🤖 Explain ML Model
            </button>
            <button
              onClick={() => handleSendMessage("What is the difference between precision and recall?")}
              className="text-xs px-2.5 py-1 rounded-full bg-slate-900 hover:bg-primary/20 text-slate-300 hover:text-primary-light border border-borderSubtle hover:border-primary/40 transition duration-150 whitespace-nowrap active:scale-[0.98] focus-ring"
            >
              🎯 Precision vs Recall
            </button>
            <button
              onClick={() => handleSendMessage("Why did Policy Engine escalate or stop transactions?")}
              className="text-xs px-2.5 py-1 rounded-full bg-slate-900 hover:bg-primary/20 text-slate-300 hover:text-primary-light border border-borderSubtle hover:border-primary/40 transition duration-150 whitespace-nowrap active:scale-[0.98] focus-ring"
            >
              🛡️ Policy Rules
            </button>
            <button
              onClick={() => handleSendMessage("How do I test custom transaction data in simulation?")}
              className="text-xs px-2.5 py-1 rounded-full bg-slate-900 hover:bg-primary/20 text-slate-300 hover:text-primary-light border border-borderSubtle hover:border-primary/40 transition duration-150 whitespace-nowrap active:scale-[0.98] focus-ring"
            >
              🧪 Simulation Guide
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"} animate-fade-in`}
              >
                <div className="flex items-center gap-1.5 mb-1 px-1">
                  <span className="text-[10px] text-slate-400 font-medium">
                    {msg.sender === "user" ? "You" : "RecoverAI AI"}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">• {msg.timestamp}</span>
                </div>

                <div
                  className={`max-w-[92%] p-3.5 rounded-2xl text-xs leading-relaxed relative group ${
                    msg.sender === "user"
                      ? "bg-gradient-to-r from-primary to-indigo-600 text-white rounded-tr-none shadow-md shadow-primary/20 font-sans"
                      : "bg-slate-900/90 text-slate-200 border border-slate-800 rounded-tl-none shadow-sm"
                  }`}
                >
                  {msg.sender === "assistant" ? (
                    <>
                      <MarkdownRenderer content={msg.text} />
                      <button
                        onClick={() => copyMessageText(msg.text, msg.id)}
                        title="Copy message"
                        className="absolute top-2.5 right-2.5 p-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-200 opacity-0 group-hover:opacity-100 transition duration-150 focus-ring"
                      >
                        {copiedMsgId === msg.id ? (
                          <Check className="w-3 h-3 text-emerald-400" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    </>
                  ) : (
                    <div className="whitespace-pre-wrap font-sans">{msg.text}</div>
                  )}

                  {/* Polished Collapsible Data Sources Used */}
                  {msg.toolsUsed && msg.toolsUsed.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-slate-800/80">
                      <button
                        onClick={() => toggleTools(msg.id)}
                        className="flex items-center gap-1.5 text-[11px] font-medium text-slate-400 hover:text-primary-light transition duration-150 py-0.5 focus-ring rounded"
                      >
                        <ShieldCheck className="w-3.5 h-3.5 text-primary" />
                        <span>Data sources used · {msg.toolsUsed.length}</span>
                        {expandedTools[msg.id] ? (
                          <ChevronUp className="w-3 h-3 text-slate-500" />
                        ) : (
                          <ChevronDown className="w-3 h-3 text-slate-500" />
                        )}
                      </button>

                      {expandedTools[msg.id] && (
                        <div className="mt-2 space-y-1.5 pl-1 animate-slide-up">
                          {msg.toolsUsed.map((t, idx) => (
                            <div
                              key={idx}
                              className="flex items-center gap-2 text-[11px] text-slate-300 bg-slate-950/70 px-2.5 py-1.5 rounded-lg border border-slate-800/80"
                            >
                              <span className="text-emerald-400 font-bold text-[10px]">✓</span>
                              <span className="font-semibold text-primary-light capitalize">
                                {t.tool_name.replace("get_", "").replace("_", " ")}
                              </span>
                              <span className="text-slate-400 text-[10px] truncate max-w-[240px]">
                                ({t.summary})
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {msg.citations.map((c, idx) => (
                        <span
                          key={idx}
                          className="text-[10px] px-2 py-0.5 bg-slate-950/80 text-slate-400 rounded-md border border-slate-800 flex items-center gap-1"
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
                        className="text-[11px] px-2.5 py-1 bg-slate-900/90 hover:bg-primary/20 text-primary-light hover:text-white rounded-lg border border-primary/30 transition duration-150 flex items-center gap-1 shadow-sm active:scale-[0.98] focus-ring"
                      >
                        <span>{act.label}</span>
                        <ChevronRight className="w-3 h-3 text-primary" />
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Loading Indicator */}
            {loading && (
              <div className="flex items-center gap-2.5 text-slate-400 text-xs py-2 px-1 animate-pulse-subtle">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-primary" />
                <span>Evaluating context and querying verified data tools...</span>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Footer Input Composer */}
          <div className="p-3 bg-slate-900/90 border-t border-borderSubtle flex items-end gap-2">
            <textarea
              ref={inputRef}
              rows={1}
              value={inputMsg}
              onChange={(e) => setInputMsg(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                pageContext === "recovery_case"
                  ? "Ask about this case or decision rationale..."
                  : "Ask about recovery telemetry, policy rules, or ML metrics..."
              }
              className="flex-1 max-h-24 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus-ring resize-none transition duration-150"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputMsg.trim() || loading}
              className="p-2.5 bg-primary hover:bg-primary-hover disabled:opacity-40 disabled:hover:bg-primary text-white rounded-xl transition duration-150 shadow-md shadow-primary/25 active:scale-[0.98] shrink-0 focus-ring"
              title="Send message (Enter)"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
