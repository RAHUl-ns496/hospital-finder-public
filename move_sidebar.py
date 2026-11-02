import os
import re

base = r"c:\Users\rahul\Documents\ai\hospital_finder\pages"
files_to_update = ["1_Find_Hospitals.py", "2_Blood_Bank.py", "3_Pharmacy.py"]

for fname in files_to_update:
    path = os.path.join(base, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We want to replace "with st.sidebar:" with a layout in the main page.
    # But since the header is currently AFTER the sidebar in the code,
    # if we just replace it, the controls will appear BEFORE the header.
    # We need to swap their positions.
    
    # Find the header block
    header_match = re.search(r'(st\.markdown\("""\n<div class="app-header">.*?</style>\n""",?\s*unsafe_allow_html=True\)?|st\.markdown\("""\n<div class="app-header">.*?</div>""",\s*unsafe_allow_html=True\)\n.*?)(?=if not st\.session_state|hospitals=|banks=|pharma=)', content, re.DOTALL)
    
    # Also find the sidebar block
    sidebar_match = re.search(r'# ── Sidebar location ──────────────────────────\nwith st\.sidebar:(.*?)(?=\n# ── Header)', content, re.DOTALL)
    
    if not sidebar_match:
        sidebar_match = re.search(r'with st\.sidebar:(.*?)(?=st\.markdown\("""\n<div class="app-header">)', content, re.DOTALL)

    if header_match and sidebar_match:
        sidebar_code = sidebar_match.group(1)
        # Indent correction (sidebar code is indented by 4 spaces, keep it that way for the expander)
        new_search_block = f"""
# ── Search & Filters (Moved from Sidebar) ────
with st.expander("🔍 Search & Location Settings", expanded=not st.session_state.get('{fname.split("_")[1][:2].lower()}_searched', False)):
{sidebar_code}
"""
        # Remove old sidebar
        content = content.replace(sidebar_match.group(0), "")
        
        # Insert new search block right AFTER the header block
        header_full = header_match.group(0)
        content = content.replace(header_full, header_full + new_search_block)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {fname}")
    else:
        print(f"Failed to match blocks in {fname}")

