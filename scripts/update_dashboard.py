import os
import datetime
import re

def update_dashboard():
    base_path = "."
    projects = []

    # Scan all project folders
    for item in sorted(os.listdir(base_path)):
        if os.path.isdir(os.path.join(base_path, item)) and not item.startswith("."):
            changelog = os.path.join(base_path, item, "CHANGELOG.md")
            if os.path.exists(changelog):
                with open(changelog, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract last updated date
                match = re.search(r'Last updated: (\S+)', content)
                last_updated = match.group(1) if match else "Unknown"

                # Extract last change title
                match = re.search(r'## (.+)', content)
                last_change = match.group(1).strip() if match else "No entries yet"
                # Clean up date prefix if present
                last_change = re.sub(r'\*\*Date:.*?\*\*\s*\|?', '', last_change).strip()

                projects.append({
                    "name": item,
                    "last_updated": last_updated,
                    "last_change": last_change[:60] + "..." if len(last_change) > 60 else last_change
                })

    # Build README
    today = datetime.date.today().isoformat()
    readme = f"""# Applikon IT Solutions — Project Documentation Hub

> Last refreshed: {today}

## Active Projects ({len(projects)})

| Project | Last Updated | Last Change |
|---------|-------------|-------------|
"""
    for p in projects:
        readme += f"| [{p['name']}](./{p['name']}/CHANGELOG.md) | {p['last_updated']} | {p['last_change']} |\n"

    if not projects:
        readme += "| *No projects documented yet* | | |\n"

    readme += """
## How to View Documentation
Click any project name above to view its full changelog.

## How Documentation is Generated
Triggered manually via **Actions → Auto Documentation** in each project repo.
Claude AI reads the code diff and generates professional documentation automatically.
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"✅ Dashboard updated with {len(projects)} projects")

if __name__ == "__main__":
    update_dashboard()
