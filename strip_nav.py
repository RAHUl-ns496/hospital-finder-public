import os, re

base = r"c:\Users\rahul\Documents\ai\hospital_finder\pages"

for fname in sorted(os.listdir(base)):
    if not fname.endswith(".py"): continue
    path = os.path.join(base, fname)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Remove injected nav block
    content = re.sub(
        r"# .* Role-based navigation.*?\n"
        r"from utils\.auth import check_auth\n"
        r"from utils\.nav\s+import run_navigation\n+"
        r"check_auth\(\)\s*#.*\n"
        r"pg = run_navigation\(\)\s*#.*\n",
        "", content, flags=re.DOTALL
    )
    # Remove leftover from inject_auth.py
    content = re.sub(r"from utils\.auth import check_auth, render_user_sidebar\ncheck_auth\(\)\n", "", content)
    content = re.sub(r"from utils\.auth import check_auth\ncheck_auth\(\)\n", "", content)
    # Remove pg.run() at bottom
    content = re.sub(r"\n+pg\.run\(\)\n?$", "", content.rstrip()) + "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Cleaned: " + fname)

print("All cleaned!")
