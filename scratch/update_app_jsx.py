import os

app_path = r"C:\Projects\VeriNexa\frontend\src\App.jsx"

with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """  // Parse Verdict string into clean badge label & explanation text
  const parseVerdictInfo = (rawVerdict, fallbackText = "") => {
    if (!rawVerdict) {
      return { label: "VERDICT: UNCLEAR", type: "unclear", reason: fallbackText };
    }

    const str = String(rawVerdict).trim();

    // 1. Locate all VERDICT occurrences to extract the final arbitration verdict
    const verdictMatches = [...str.matchAll(/VERDICT:\\s*([^\\n\\r]+)/gi)];
    let lastVerdictLine = "";
    if (verdictMatches.length > 0) {
      lastVerdictLine = verdictMatches[verdictMatches.length - 1][1].trim();
    } else {
      lastVerdictLine = str.split("\\n")[0].trim();
    }

    let verdictKeyword = "";
    let verdictBriefReason = "";
    const dashMatch = lastVerdictLine.match(/^([A-Za-z_\\s]+?)(?:\\s*[-:]\\s*(.*))?$/);
    if (dashMatch) {
      verdictKeyword = dashMatch[1].trim().toUpperCase();
      verdictBriefReason = dashMatch[2] ? dashMatch[2].trim() : "";
    } else {
      verdictKeyword = lastVerdictLine.trim().toUpperCase();
    }

    // 2. Classify badge label & color type
    let label = "VERDICT: UNCLEAR";
    let type = "unclear";

    if (
      verdictKeyword.includes("CONFLICT") ||
      verdictKeyword.includes("CONTRADICT") ||
      verdictKeyword.includes("INCONSISTENT")
    ) {
      label = verdictKeyword.includes("INCONSISTENT")
        ? "VERDICT: INCONSISTENT"
        : verdictKeyword.includes("CONFLICT")
        ? "VERDICT: CONFLICT"
        : "VERDICT: CONTRADICT";
      type = "red";
    } else if (verdictKeyword.includes("PARTIAL")) {
      label = verdictKeyword.includes("PARTIALLY CONSISTENT")
        ? "VERDICT: PARTIALLY CONSISTENT"
        : "VERDICT: PARTIAL";
      type = "amber";
    } else if (
      verdictKeyword.includes("CONSISTENT") ||
      verdictKeyword.includes("AGREE") ||
      verdictKeyword.includes("MATCH")
    ) {
      label = "VERDICT: CONSISTENT";
      type = "green";
    } else if (verdictKeyword.includes("UNCLEAR")) {
      label = "VERDICT: UNCLEAR";
      type = "unclear";
    } else if (verdictKeyword) {
      label = `VERDICT: ${verdictKeyword}`;
      type = "unclear";
    }

    // 3. Strip all verdict tags (e.g., 'VERDICT: PARTIAL -', 'VERDICT: CONFLICT', 'REASON:')
    // from the summary text so it only appears in the badge, keeping the text area completely clean.
    let cleanText = str;

    // Remove standalone or inline verdict tags while preserving reasons/bullets
    cleanText = cleanText
      .replace(/VERDICT:\\s*[A-Za-z_\\s]+(?:\\s*-\\s*|\\s*:\\s*|\\n|$)/gi, "")
      .replace(/(?:REASON|EXPLANATION):\\s*/gi, "")
      .trim();

    // If cleanText is empty (e.g. LLM only returned "VERDICT: PARTIAL"), fallback to brief reason or original
    if (!cleanText) {
      cleanText = verdictBriefReason || fallbackText || str;
    }

    return { label, type, reason: cleanText };
  };

  // Format Verdict Badge
  const renderVerdictBadge = (verdict, fallbackText = "") => {
    const { label, type } = parseVerdictInfo(verdict, fallbackText);

    if (type === "red") {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#ff4757]/15 border border-[#ff4757]/40 text-[#ff4757] font-mono font-bold text-xs">
          <XCircle className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    } else if (type === "amber") {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#e8a33d]/15 border border-[#e8a33d]/40 text-[#e8a33d] font-mono font-bold text-xs">
          <AlertTriangle className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    } else if (type === "green") {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#2dd4ce]/15 border border-[#2dd4ce]/40 text-[#2dd4ce] font-mono font-bold text-xs">
          <CheckCircle2 className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#8fa89b]/15 border border-[#8fa89b]/40 text-[#8fa89b] font-mono font-bold text-xs">
          <AlertTriangle className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    }
  };"""

new_block = """  // Helper to render markdown bold syntax **bold** cleanly
  const renderInlineMarkdown = (text) => {
    if (!text) return null;
    const parts = text.split(/(\\*\\*[^*]+?\\*\\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
        return (
          <strong key={index} className="font-semibold text-white">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  // Helper to sanitize leading asterisk combinations and render structured bullets
  const renderFormattedReason = (rawReason) => {
    if (!rawReason) return null;

    const rawLines = String(rawReason).split(/\\r?\\n/);
    const elements = [];
    let currentBulletList = [];

    const flushBulletList = () => {
      if (currentBulletList.length > 0) {
        const listItems = [...currentBulletList];
        elements.push(
          <ul key={`ul-${elements.length}`} className="space-y-2 my-2 pl-1">
            {listItems.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-[#d8f3f0] leading-relaxed">
                <span className="text-[#e8a33d] font-bold text-sm leading-none mt-0.5">•</span>
                <span className="flex-1">{renderInlineMarkdown(item)}</span>
              </li>
            ))}
          </ul>
        );
        currentBulletList = [];
      }
    };

    for (let i = 0; i < rawLines.length; i++) {
      let line = rawLines[i].trim();
      if (!line) {
        flushBulletList();
        continue;
      }

      // Check if line is a bullet point or has leading asterisk combinations
      // Examples: '* **Title**:', '***Title***:', '**Title**:', '- **Title**:', '* Title'
      const bulletMatch = line.match(/^([*•\\-–]|\\d+\\.)\\s*(.*)$/);
      const isAsteriskCombo = /^(\\*{2,3})\\s*(.*)$/.test(line);

      if (bulletMatch || isAsteriskCombo) {
        let content = bulletMatch ? bulletMatch[2] : line;

        // Clean leading double/triple asterisk combinations e.g., '***', '**'
        content = content.replace(/^\\*{3}([^*]+?)\\*{3}/, "**$1**");
        content = content.replace(/^\\*{2,3}\\s*/, "**");
        content = content.trim();

        currentBulletList.push(content);
      } else {
        flushBulletList();
        // Regular paragraph (introductory or concluding sentence)
        const cleanedPara = line.replace(/^\\*{2,3}\\s*/, "").trim();
        elements.push(
          <p key={`p-${elements.length}`} className="text-xs text-[#d8f3f0] leading-relaxed">
            {renderInlineMarkdown(cleanedPara)}
          </p>
        );
      }
    }

    flushBulletList();

    return <div className="space-y-2">{elements}</div>;
  };

  // Parse Verdict string into clean badge label & explanation text
  const parseVerdictInfo = (rawVerdict, fallbackText = "") => {
    if (!rawVerdict) {
      return { label: "VERDICT: INSUFFICIENT DATA", type: "unclear", reason: fallbackText };
    }

    const str = String(rawVerdict).trim();

    // 1. Locate all VERDICT occurrences to extract candidate verdict line
    const verdictMatches = [...str.matchAll(/VERDICT:\\s*([^\\n\\r]+)/gi)];
    let lastVerdictLine = "";
    if (verdictMatches.length > 0) {
      lastVerdictLine = verdictMatches[verdictMatches.length - 1][1].trim();
    } else {
      lastVerdictLine = str.split("\\n")[0].trim();
    }

    const upperText = (lastVerdictLine + " " + str).toUpperCase();

    // 2. Classify strictly into the 4 canonical categories:
    // VERDICT: PARTIAL, VERDICT: CONFLICT DETECTED, VERDICT: CONCORDANT, VERDICT: INSUFFICIENT DATA
    let label = "VERDICT: PARTIAL";
    let type = "amber";

    if (
      upperText.includes("CONFLICT") ||
      upperText.includes("CONTRADICT") ||
      upperText.includes("INCONSISTENT") ||
      upperText.includes("DISCORDANT")
    ) {
      label = "VERDICT: CONFLICT DETECTED";
      type = "red";
    } else if (
      upperText.includes("PARTIAL") ||
      upperText.includes("PARTIALLY")
    ) {
      label = "VERDICT: PARTIAL";
      type = "amber";
    } else if (
      upperText.includes("CONCORDANT") ||
      upperText.includes("CONSISTENT") ||
      upperText.includes("AGREE") ||
      upperText.includes("MATCH")
    ) {
      label = "VERDICT: CONCORDANT";
      type = "green";
    } else if (
      upperText.includes("INSUFFICIENT") ||
      upperText.includes("UNCLEAR") ||
      upperText.includes("NO DATA") ||
      upperText.includes("NOT ENOUGH")
    ) {
      label = "VERDICT: INSUFFICIENT DATA";
      type = "unclear";
    } else {
      // Fallback cleanly to VERDICT: PARTIAL
      label = "VERDICT: PARTIAL";
      type = "amber";
    }

    // 3. Strip all verdict tags (e.g., 'VERDICT: PARTIAL -', 'VERDICT: CONFLICT', 'REASON:')
    let cleanText = str;
    cleanText = cleanText
      .replace(/VERDICT:\\s*[A-Za-z_\\s]+(?:\\s*-\\s*|\\s*:\\s*|\\n|$)/gi, "")
      .replace(/(?:REASON|EXPLANATION):\\s*/gi, "")
      .trim();

    if (!cleanText) {
      cleanText = fallbackText || str;
    }

    return { label, type, reason: cleanText };
  };

  // Format Verdict Badge
  const renderVerdictBadge = (verdict, fallbackText = "") => {
    const { label, type } = parseVerdictInfo(verdict, fallbackText);

    if (type === "red") {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#ff4757]/15 border border-[#ff4757]/40 text-[#ff4757] font-mono font-bold text-xs">
          <XCircle className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    } else if (type === "green") {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#2dd4ce]/15 border border-[#2dd4ce]/40 text-[#2dd4ce] font-mono font-bold text-xs">
          <CheckCircle2 className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    } else if (type === "unclear") {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#8fa89b]/15 border border-[#8fa89b]/40 text-[#8fa89b] font-mono font-bold text-xs">
          <HelpCircle className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#e8a33d]/15 border border-[#e8a33d]/40 text-[#e8a33d] font-mono font-bold text-xs">
          <AlertTriangle className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    }
  };"""

# Normalize line endings for replacement
norm_content = content.replace("\r\n", "\n")
norm_old = old_block.replace("\r\n", "\n")
norm_new = new_block.replace("\r\n", "\n")

if norm_old in norm_content:
    updated = norm_content.replace(norm_old, norm_new, 1)
    with open(app_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(updated.replace("\n", "\r\n"))
    print("Successfully replaced verdict functions in App.jsx!")
else:
    print("Error: old_block not found in App.jsx!")
