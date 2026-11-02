import os, re

base = r"c:\Users\rahul\Documents\ai\hospital_finder"
pages_dir = os.path.join(base, "pages")

for fname in sorted(os.listdir(pages_dir)):
    if not fname.endswith(".py"):
        continue
    path = os.path.join(pages_dir, fname)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Add pg.run() at very end if not already there
    if "pg.run()" not in content:
        content = content.rstrip() + "\n\npg.run()\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("pg.run() added: " + fname)
    else:
        print("Already has pg.run(): " + fname)

print("Done!")
