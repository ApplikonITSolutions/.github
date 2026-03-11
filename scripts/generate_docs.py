import anthropic
import os
import datetime

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Could not read {path}: {e}")
        return ""

def generate_documentation():
    print("=== Starting documentation generation ===")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    diff        = read_file("code_diff.txt")
    files       = read_file("changed_files.txt")
    commits     = read_file("recent_commits.txt")
    author      = os.environ.get("GITHUB_ACTOR", "Unknown")
    branch      = os.environ.get("GITHUB_REF", "main")
    repo        = os.environ.get("GITHUB_REPOSITORY", "unknown").split("/")[-1]
    date        = datetime.date.today().isoformat()
    description = os.environ.get("RELEASE_DESCRIPTION", "Manual documentation run")

    print(f"Repo={repo}, Author={author}, Date={date}")
    print(f"Release description: {description}")
    print(f"Diff length: {len(diff)} characters")

    if not diff and not files:
        print("No changes detected. Skipping.")
        return

    if len(diff) > 8000:
        diff = diff[:8000] + "\n\n[... diff truncated ...]"

    prompt = f"""You are a senior Salesforce technical writer at Applikon IT Solutions.

A developer has manually triggered documentation for the following batch of changes:

PROJECT: {repo}
RELEASE DESCRIPTION: {description}
RECENT COMMITS:
{commits}

FILES CHANGED:
{files}

CODE DIFF:
{diff}

Generate a detailed professional changelog entry in markdown:

## {description}
**Project:** {repo} | **Date:** {date} | **Author:** {author} | **Branch:** {branch}

### Summary
(2-3 sentences — plain English summary)

### Business Impact
(Why do these changes matter?)

### Technical Details
(What exactly changed — group by component)

### Salesforce Metadata Affected
(List Apex, LWC, Flows, Objects, Fields)

### Deployment Instructions
(Step by step)

### Risk Assessment
(Low / Medium / High and why)

### Rollback Plan
(How to undo if needed)"""

    print("Calling Claude API...")
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    documentation = message.content[0].text
    print(f"Response received — {len(documentation)} characters")

    os.makedirs("docs/changes", exist_ok=True)
    filename = f"docs/changes/{date}-{author}.md"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(documentation)
        f.write("\n\n---\n\n")

    update_changelog(documentation, date, author)
    print(f"✅ Documentation saved to {filename}")

def update_changelog(new_entry, date, author):
    changelog_path = "docs/CHANGELOG.md"
    header = "# Applikon IT Solutions — Project Changelog\n\n"

    existing = ""
    if os.path.exists(changelog_path):
        with open(changelog_path, "r", encoding="utf-8") as f:
            existing = f.read()

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(f"<!-- Last updated: {date} by {author} -->\n\n")
        f.write(new_entry)
        f.write("\n\n---\n\n")
        old_content = existing.replace(header, "").strip()
        if old_content:
            f.write(old_content)

    print(f"✅ CHANGELOG.md updated")

if __name__ == "__main__":
    generate_documentation()
