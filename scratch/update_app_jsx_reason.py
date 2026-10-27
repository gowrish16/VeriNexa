app_path = r"C:\Projects\VeriNexa\frontend\src\App.jsx"

with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

target1 = """                        <p className="text-xs text-[#d8f3f0] leading-relaxed whitespace-pre-line">
                          {parsed.reason}
                        </p>"""

replacement1 = """                        <div className="text-xs text-[#d8f3f0] leading-relaxed">
                          {renderFormattedReason(parsed.reason)}
                        </div>"""

norm_content = content.replace("\r\n", "\n")
norm_target = target1.replace("\r\n", "\n")
norm_replacement = replacement1.replace("\r\n", "\n")

if norm_target in norm_content:
    updated = norm_content.replace(norm_target, norm_replacement)
    with open(app_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(updated.replace("\n", "\r\n"))
    print("Replaced both occurrences of parsed.reason with renderFormattedReason!")
else:
    print("Target not found!")
