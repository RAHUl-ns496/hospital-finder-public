import os, re

pages = [
    "pages/1_Find_Hospitals.py",
    "pages/2_Ambulance_SOS.py",
    "pages/3_Blood_Bank.py",
    "pages/4_Pharmacy.py",
    "pages/5_First_Aid_Guide.py",
    "pages/6_My_Profile.py",
]

guard = "from utils.auth import check_auth, render_user_sidebar\ncheck_auth()\n"

base = r"c:\Users\rahul\Documents\ai\hospital_finder"

for rel in pages:
    path = os.path.join(base, rel)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Skip if already has check_auth
    if "check_auth()" in content:
        print("Already guarded: " + rel)
        continue

    # Insert guard after set_page_config
    m = re.search(r"st\.set_page_config\([^)]+\)", content, re.DOTALL)
    if m:
        pos = m.end()
        content = content[:pos] + "\n" + guard + content[pos:]
    else:
        content = guard + content

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Guard added: " + rel)

print("Done!")
