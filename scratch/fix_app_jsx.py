import os

app_path = r"C:\Projects\VeriNexa\frontend\src\App.jsx"

with open(app_path, "rb") as f:
    raw = f.read()

# Normalize all CRLF / double-CRLF to standard LF
cleaned = raw.replace(b"\r\r\n", b"\n").replace(b"\r\n", b"\n")
text = cleaned.decode("utf-8")
print(f"Total lines after LF normalization: {len(text.splitlines())}")

old_target = """                        <p className="text-xs text-[#d8f3f0] leading-relaxed whitespace-pre-line">
                          {parsed.reason}
                        </p>"""

new_replacement = """                        <div className="text-xs text-[#d8f3f0] leading-relaxed">
                          {renderFormattedReason(parsed.reason)}
                        </div>"""

count = text.count(old_target)
print(f"Occurrences found: {count}")

if count > 0:
    text = text.replace(old_target, new_replacement)
    with open(app_path, "wb") as f:
        # Write with clean standard CRLF
        f.write(text.replace("\n", "\r\n").encode("utf-8"))
    print(f"Successfully replaced {count} occurrences and saved with clean CRLF line endings.")
else:
    print("Old target not found. Checking lines around 'parsed.reason'...")
    lines = text.splitlines()
    for idx, l in enumerate(lines):
        if "parsed.reason" in l:
            print(f"Line {idx+1}: {repr(l)}")
            for j in range(max(0, idx-2), min(len(lines), idx+3)):
                print(f"  [{j+1}] {repr(lines[j])}")
