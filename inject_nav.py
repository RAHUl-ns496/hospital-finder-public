import os, re

base = r"c:\Users\rahul\Documents\ai\hospital_finder"
pages_dir = os.path.join(base, "pages")

# New nav header to inject at top of each page (after set_page_config)
NAV_HEADER = """
# ── Role-based navigation (injected) ─────────
from utils.auth import check_auth
from utils.nav  import run_navigation

check_auth()           # redirect to Home if not logged in
pg = run_navigation()  # build role-filtered sidebar
"""

for fname in sorted(os.listdir(pages_dir)):
    if not fname.endswith(".py"):
        continue
    path = os.path.join(pages_dir, fname)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Remove old check_auth / render_user_sidebar injections
    content = re.sub(r"from utils\.auth import check_auth.*?\n", "", content)
    content = re.sub(r"from utils\.auth import check_auth, render_user_sidebar.*?\n", "", content)
    content = re.sub(r"check_auth\(.*?\)\n", "", content)
    content = re.sub(r"from utils\.nav import run_navigation.*?\n", "", content)
    content = re.sub(r"pg = run_navigation\(\).*?\n", "", content)

    # Insert after set_page_config block
    m = re.search(r"st\.set_page_config\(.*?\)", content, re.DOTALL)
    if m:
        pos = m.end()
        content = content[:pos] + NAV_HEADER + content[pos:]
    else:
        content = NAV_HEADER + content

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated: " + fname)

print("All pages updated!")
