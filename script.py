import subprocess
from datetime import datetime
import os
import sys

# CONFIG
BASE_BRANCH = "main"
workspace = os.getenv("GITHUB_WORKSPACE", os.getcwd())

LIB_FILE = os.path.join(workspace, "filtered_summary.txt")
# DOCKERFILE_PATH = os.path.join(workspace, "Dockerfile1")

date_str = datetime.now().strftime("%Y%m%d")
new_branch = f"feature/securityupdate-{date_str}"

def run(cmd, capture=False):
    print(f"Running: {cmd}")
    if capture:
        return subprocess.check_output(cmd, shell=True).decode().strip()
    subprocess.run(cmd, shell=True, check=True)

print(f"Workspace: {workspace}")
print(f"Lib file: {LIB_FILE}")
# print(f"Dockerfile: {DOCKERFILE_PATH}")

# ✅ Git config
run('git config user.name "github-actions[bot]"')
run('git config user.email "github-actions[bot]@users.noreply.github.com"')

# ✅ Detect current branch (important for future branches)
current_branch = os.getenv("GITHUB_REF_NAME")

if not current_branch:
    # fallback (local or edge cases)
    current_branch = run("git rev-parse --abbrev-ref HEAD", capture=True)

print(f"Detected branch: {current_branch}")

# ✅ Fetch latest
run("git fetch origin")

# ✅ Checkout current branch properly
run(f"git checkout {current_branch}")
run(f"git reset --hard origin/{current_branch}")

# ✅ Create new branch FROM current branch
run(f"git checkout -B {new_branch}")

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

# ✅ Step 2: Update Dockerfile (avoid duplicates)
# install_command = f"RUN apk add --no-cache --no-docs {libs}"

# if not os.path.exists(DOCKERFILE_PATH):
#     print("❌ Dockerfile not found.")
#     sys.exit(1)

# with open(DOCKERFILE_PATH, "r") as f:
#     content = f.read()

# if install_command in content:
#     print("✅ Dockerfile already updated. Skipping PR.")
#     sys.exit(0)

# Append
# with open(DOCKERFILE_PATH, "a") as f:
#     f.write("\n" + install_command + "\n")

# print("✅ Dockerfile updated.")

# ✅ Step 3: Commit
# run(f"git add {DOCKERFILE_PATH}")

diff_cached = subprocess.run("git diff --cached --quiet", shell=True)
if diff_cached.returncode == 0:
    print("No changes detected. Skipping PR.")
    sys.exit(0)

run(f'git commit -m "security: upgrade libraries ({date_str})"')

# ✅ Step 4: Compare with main
run(f"git fetch origin {BASE_BRANCH}")

diff_count = run(
    f"git rev-list --count origin/{BASE_BRANCH}..HEAD",
    capture=True
)

if diff_count == "0":
    print("No difference from main. Skipping PR.")
    sys.exit(0)

print(f"🔥 Changes detected ({diff_count} commits). Creating PR...")

# ✅ Step 5: Push
run(f"git push origin {new_branch} --force")

# ✅ Step 6: Create PR
run(f"""
gh pr create \
  --base {BASE_BRANCH} \
  --head {new_branch} \
  --title "Security: Library upgrades {date_str}" \
  --body "Automated security updates from filtered_summary.txt (source: {current_branch})" \
  || echo "PR may already exist"
""")

print("✅ PR created successfully!")