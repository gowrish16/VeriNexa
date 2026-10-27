import os

target_words = ['waste bin', 'proper disposal', 'littering', 'litter']

for root, dirs, files in os.walk('.'):
    if 'node_modules' in root or '.git' in root or '.system_generated' in root or 'venv' in root or '.gemini' in root:
        continue
    for f in files:
        if f.endswith(('.py', '.js', '.jsx', '.json', '.md', '.sql', '.txt')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    for word in target_words:
                        if word.lower() in content.lower():
                            print(f"Found '{word}' in {path}")
            except Exception as e:
                pass
