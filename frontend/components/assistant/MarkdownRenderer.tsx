"use client";

import React, { useState } from "react";
import { Check, Copy } from "lucide-react";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = "" }) => {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const handleCopyCode = (codeText: string, id: string) => {
    navigator.clipboard.writeText(codeText);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  // Helper to parse inline styles: bold (**), italic (*), inline code (`), and links ([text](url))
  const renderInline = (text: string): React.ReactNode[] => {
    const parts: React.ReactNode[] = [];
    let remaining = text;
    let keyIdx = 0;

    while (remaining.length > 0) {
      // Inline Code: `code`
      const codeMatch = remaining.match(/^([\s\S]*?)`([^`]+)`/);
      // Bold: **text**
      const boldMatch = remaining.match(/^([\s\S]*?)\*\*([^*]+)\*\*/);
      // Italic: *text*
      const italicMatch = remaining.match(/^([\s\S]*?)\*([^*]+)\*/);
      // Link: [text](url)
      const linkMatch = remaining.match(/^([\s\S]*?)\[([^\]]+)\]\(([^)]+)\)/);

      // Find earliest match
      let firstMatch: { type: string; prefix: string; content: string; extra?: string; fullLen: number } | null = null;
      let minPos = Infinity;

      if (codeMatch && codeMatch[1].length < minPos) {
        minPos = codeMatch[1].length;
        firstMatch = { type: "code", prefix: codeMatch[1], content: codeMatch[2], fullLen: codeMatch[0].length };
      }
      if (boldMatch && boldMatch[1].length < minPos) {
        minPos = boldMatch[1].length;
        firstMatch = { type: "bold", prefix: boldMatch[1], content: boldMatch[2], fullLen: boldMatch[0].length };
      }
      if (italicMatch && italicMatch[1].length < minPos) {
        minPos = italicMatch[1].length;
        firstMatch = { type: "italic", prefix: italicMatch[1], content: italicMatch[2], fullLen: italicMatch[0].length };
      }
      if (linkMatch && linkMatch[1].length < minPos) {
        minPos = linkMatch[1].length;
        firstMatch = { type: "link", prefix: linkMatch[1], content: linkMatch[2], extra: linkMatch[3], fullLen: linkMatch[0].length };
      }

      if (!firstMatch) {
        parts.push(<React.Fragment key={keyIdx++}>{remaining}</React.Fragment>);
        break;
      }

      if (firstMatch.prefix) {
        parts.push(<React.Fragment key={keyIdx++}>{firstMatch.prefix}</React.Fragment>);
      }

      if (firstMatch.type === "code") {
        parts.push(
          <code key={keyIdx++} className="px-1.5 py-0.5 mx-0.5 rounded bg-slate-800/90 text-blue-300 font-mono text-[11px] border border-slate-700/60">
            {firstMatch.content}
          </code>
        );
      } else if (firstMatch.type === "bold") {
        parts.push(
          <strong key={keyIdx++} className="font-semibold text-slate-100">
            {firstMatch.content}
          </strong>
        );
      } else if (firstMatch.type === "italic") {
        parts.push(
          <em key={keyIdx++} className="text-slate-200 italic">
            {firstMatch.content}
          </em>
        );
      } else if (firstMatch.type === "link") {
        const rawUrl = firstMatch.extra || "#";
        const isSafeUrl = rawUrl.startsWith("/") || rawUrl.startsWith("http://") || rawUrl.startsWith("https://");
        parts.push(
          <a
            key={keyIdx++}
            href={isSafeUrl ? rawUrl : "#"}
            target={rawUrl.startsWith("/") ? "_self" : "_blank"}
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300 underline underline-offset-2 font-medium"
          >
            {firstMatch.content}
          </a>
        );
      }

      remaining = remaining.substring(firstMatch.fullLen);
    }

    return parts;
  };

  // Block level parser
  const renderBlocks = (): React.ReactNode[] => {
    const blocks: React.ReactNode[] = [];
    const lines = content.split(/\r?\n/);
    let i = 0;
    let blockKey = 0;

    while (i < lines.length) {
      const line = lines[i];

      // 1. Code Block: ```lang
      if (line.trim().startsWith("```")) {
        const lang = line.trim().substring(3).trim() || "code";
        const codeLines: string[] = [];
        i++;
        while (i < lines.length && !lines[i].trim().startsWith("```")) {
          codeLines.push(lines[i]);
          i++;
        }
        const codeText = codeLines.join("\n");
        const codeId = `code_${blockKey}`;

        blocks.push(
          <div key={blockKey++} className="my-3 rounded-xl border border-slate-800 bg-slate-950 overflow-hidden shadow-lg font-mono text-xs">
            <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900/90 border-b border-slate-800 text-[11px] text-slate-400">
              <span className="font-semibold text-slate-300 uppercase tracking-wider">{lang}</span>
              <button
                onClick={() => handleCopyCode(codeText, codeId)}
                className="flex items-center gap-1 hover:text-white transition text-slate-400"
              >
                {copiedCode === codeId ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-400 font-sans">Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span className="font-sans">Copy</span>
                  </>
                )}
              </button>
            </div>
            <pre className="p-3 overflow-x-auto text-slate-200 leading-relaxed font-mono whitespace-pre">{codeText}</pre>
          </div>
        );
        i++;
        continue;
      }

      // 2. Blockquote: > text
      if (line.trim().startsWith(">")) {
        const quoteLines: string[] = [];
        while (i < lines.length && lines[i].trim().startsWith(">")) {
          quoteLines.push(lines[i].trim().substring(1).trim());
          i++;
        }
        blocks.push(
          <blockquote
            key={blockKey++}
            className="my-2.5 pl-3 py-2 border-l-2 border-blue-500/80 bg-blue-950/20 text-slate-200 rounded-r-lg text-xs leading-relaxed"
          >
            {quoteLines.map((ql, qidx) => (
              <div key={qidx}>{renderInline(ql)}</div>
            ))}
          </blockquote>
        );
        continue;
      }

      // 3. Headings: ###, ##, #
      if (line.startsWith("### ")) {
        blocks.push(
          <h3 key={blockKey++} className="text-sm font-bold text-slate-100 mt-3 mb-1.5 flex items-center gap-1.5 tracking-tight border-b border-slate-800/60 pb-1">
            {renderInline(line.substring(4))}
          </h3>
        );
        i++;
        continue;
      }
      if (line.startsWith("## ")) {
        blocks.push(
          <h2 key={blockKey++} className="text-base font-bold text-white mt-4 mb-2 tracking-tight border-b border-slate-700/60 pb-1">
            {renderInline(line.substring(3))}
          </h2>
        );
        i++;
        continue;
      }
      if (line.startsWith("# ")) {
        blocks.push(
          <h1 key={blockKey++} className="text-lg font-bold text-white mt-4 mb-2 tracking-tight">
            {renderInline(line.substring(2))}
          </h1>
        );
        i++;
        continue;
      }

      // 4. Bullet List: - or *
      if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
        const listItems: string[] = [];
        while (
          i < lines.length &&
          (lines[i].trim().startsWith("- ") || lines[i].trim().startsWith("* "))
        ) {
          listItems.push(lines[i].trim().substring(2).trim());
          i++;
        }
        blocks.push(
          <ul key={blockKey++} className="my-2 space-y-1.5 pl-1">
            {listItems.map((item, lidx) => (
              <li key={lidx} className="flex items-start gap-2 text-xs text-slate-200 leading-relaxed">
                <span className="text-blue-400 mt-1.5 text-[8px] shrink-0">●</span>
                <span className="flex-1">{renderInline(item)}</span>
              </li>
            ))}
          </ul>
        );
        continue;
      }

      // 5. Numbered List: 1., 2.
      if (/^\d+\.\s/.test(line.trim())) {
        const listItems: string[] = [];
        while (i < lines.length && /^\d+\.\s/.test(lines[i].trim())) {
          listItems.push(lines[i].trim().replace(/^\d+\.\s/, ""));
          i++;
        }
        blocks.push(
          <ol key={blockKey++} className="my-2 space-y-1.5 pl-1">
            {listItems.map((item, lidx) => (
              <li key={lidx} className="flex items-start gap-2 text-xs text-slate-200 leading-relaxed">
                <span className="font-semibold text-blue-400 text-xs shrink-0">{lidx + 1}.</span>
                <span className="flex-1">{renderInline(item)}</span>
              </li>
            ))}
          </ol>
        );
        continue;
      }

      // 6. Markdown Table: | Header 1 | Header 2 |
      if (line.trim().startsWith("|") && line.trim().endsWith("|")) {
        const tableLines: string[] = [];
        while (i < lines.length && lines[i].trim().startsWith("|") && lines[i].trim().endsWith("|")) {
          tableLines.push(lines[i].trim());
          i++;
        }

        if (tableLines.length >= 2) {
          const headerRow = tableLines[0].split("|").slice(1, -1).map((c) => c.trim());
          let bodyStartIndex = 1;

          if (tableLines[1].replace(/[\s\:\-\|]/g, "").length === 0) {
            bodyStartIndex = 2;
          }

          const bodyRows = tableLines.slice(bodyStartIndex).map((rowLine) =>
            rowLine.split("|").slice(1, -1).map((c) => c.trim())
          );

          blocks.push(
            <div key={blockKey++} className="my-3 overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/80 shadow-md">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-900/90 border-b border-slate-800 text-slate-200">
                    {headerRow.map((cell, cidx) => (
                      <th key={cidx} className="px-3 py-2 font-semibold text-blue-300">
                        {renderInline(cell)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {bodyRows.map((row, ridx) => (
                    <tr key={ridx} className="hover:bg-slate-900/40 transition">
                      {row.map((cell, cidx) => (
                        <td key={cidx} className="px-3 py-2 text-slate-300">
                          {renderInline(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
          continue;
        }
      }

      // 7. Horizontal Rule: ---
      if (line.trim() === "---" || line.trim() === "***") {
        blocks.push(<hr key={blockKey++} className="my-3 border-slate-800" />);
        i++;
        continue;
      }

      // 7. Regular Paragraph Line
      if (line.trim().length > 0) {
        blocks.push(
          <p key={blockKey++} className="my-1.5 text-xs text-slate-200 leading-relaxed">
            {renderInline(line)}
          </p>
        );
      } else {
        // Empty line gap
        blocks.push(<div key={blockKey++} className="h-1.5" />);
      }

      i++;
    }

    return blocks;
  };

  return <div className={`space-y-0.5 text-slate-200 ${className}`}>{renderBlocks()}</div>;
};
