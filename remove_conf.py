import os, re

base = r"c:\Users\rahul\Documents\ai\hospital_finder\pages"

for fname in sorted(os.listdir(base)):
    if not fname.endswith(".py"): continue
    path = os.path.join(base, fname)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Remove st.set_page_config block
    content = re.sub(
        r"st\.set_page_config\([^)]+\)\n?", "", content, flags=re.DOTALL
    )
    # Remove leftover render_user_sidebar calls inside sidebar blocks
    content = re.sub(r"\s+render_user_sidebar\(\)\n", "\n", content)
    # Remove import of render_user_sidebar if standalone
    content = re.sub(r"from utils\.auth import.*?render_user_sidebar.*?\n", "", content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Stripped config: " + fname)

print("Done!")
