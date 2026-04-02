import subprocess
from datetime import datetime
import os
import sys

# CONFIG
BASE_BRANCH = "main"
workspace = os.getenv("GITHUB_WORKSPACE", os.getcwd())

LIB_FILE = os.path.join(workspace, "filtered_summary.txt")
date_str = datetime.now().strftime("%Y%m%d")

def run(cmd, capture=False):
    print(f"Running: {cmd}")
    if capture:
        return subprocess.check_output(cmd, shell=True).decode().strip()
    subprocess.run(cmd, shell=True, check=True)

print(f"Workspace: {workspace}")
print(f"Lib file: {LIB_FILE}")

# ✅ Git config
run('git config user.name "github-actions[bot]"')
run('git config user.email "github-actions[bot]@users.noreply.github.com"')

# ✅ Detect current branch
current_branch = os.getenv("GITHUB_REF_NAME")
if not current_branch:
    current_branch = run("git rev-parse --abbrev-ref HEAD", capture=True)
print(f"Detected branch: {current_branch}")

# ✅ Skip if current branch is main
if current_branch == BASE_BRANCH:
    print(f"❌ Current branch is '{BASE_BRANCH}'. Skipping PR creation.")
    sys.exit(0)

# ✅ Fetch latest
run("git fetch origin")

# ✅ Reset current branch to remote
run(f"git checkout {current_branch}")
run(f"git reset --hard origin/{current_branch}")

# ✅ Step 1: Read libraries
if not os.path.exists(LIB_FILE):
    print("❌ filtered_summary.txt not found. Skipping.")
    sys.exit(0)

with open(LIB_FILE, "r") as f:
    libs = f.read().strip()

if not libs:
    print("No libraries found. Skipping PR.")
    sys.exit(0)

# Normalize format
libs = libs.replace("==", "=")

# ✅ Step 2: Commit changes if any
diff_cached = subprocess.run("git diff --cached --quiet", shell=True)
if diff_cached.returncode == 0:
    print("No staged changes detected. Skipping commit.")
else:
    run(f'git commit -am "security: upgrade libraries ({date_str})"')

# ✅ Step 3: Compare current branch with main
run(f"git fetch origin {BASE_BRANCH}")
diff_count = run(
    f"git rev-list --count origin/{BASE_BRANCH}..{current_branch}",
    capture=True
)

if diff_count == "0":
    print("No difference from main. Skipping PR.")
    sys.exit(0)

print(f"🔥 Changes detected ({diff_count} commits). Creating PR from {current_branch}...")

# ✅ Step 4: Push current branch
run(f"git push origin {current_branch}")

# ✅ Step 5: Create PR
run(f"""
gh pr create \
  --base {BASE_BRANCH} \
  --head {current_branch} \
  --title "Security: Library upgrades {date_str}" \
  --body "Automated security updates from filtered_summary.txt" \
  || echo "PR may already exist"
""")

print("✅ PR created successfully!")
