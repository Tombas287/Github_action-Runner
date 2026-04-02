import subprocess
from datetime import datetime
import os

DOCKERFILE_PATH = "Dockerfile1"
workspace = os.getcwd() 

LIB_FILE = os.path.join(workspace, "filtered_summary.txt")
DOCKERFILE_PATH = os.path.join(workspace, "Dockerfile1")

print(f"Workspace: {workspace}")
print(f"Lib file path: {LIB_FILE}")
print(f"Dockerfile path: {DOCKERFILE_PATH}")

date_str = datetime.now().strftime("%Y%m%d")
branch_name = f"feature/securityupdate-{date_str}"

def run(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

# ✅ जरूरी: Git पहचान सेट करो (Actions में missing होता है)
run('git config user.name "github-actions[bot]"')
run('git config user.email "github-actions[bot]@users.noreply.github.com"')

# Step 1: Ensure we are on latest main
run("git fetch origin main")
run("git checkout main")
run("git reset --hard origin/main")

# Step 2: Create branch (avoid failure if exists)
run(f"git checkout -B {branch_name}")

# Step 3: Read libraries
if not os.path.exists(LIB_FILE):
    raise FileNotFoundError(f"{LIB_FILE} not found")

with open(LIB_FILE, "r") as f:
    libs = f.read().strip()

if not libs:
    print("No libraries found. Skipping PR.")
    exit(0)

libs = libs.replace("==", "=")

# Step 4: Update Dockerfile
install_command = f"\nRUN apk add --no-cache --no-docs {libs}\n"

with open(DOCKERFILE_PATH, "a") as f:
    f.write(install_command)

print("Dockerfile updated.")

# Step 5: Commit (only if changes exist)
run("git add Dockerfile")

# Check if anything changed
result = subprocess.run("git diff --cached --quiet", shell=True)
if result.returncode == 0:
    print("No changes detected. Skipping PR.")
    exit(0)

run(f'git commit -m "security: upgrade libraries ({date_str})"')

# Step 6: Push using GITHUB_TOKEN
run(f"git push origin {branch_name} --force")

# Step 7: Create PR using GitHub CLI
run(f"""
gh pr create \
  --base main \
  --head {branch_name} \
  --title "Security: Library upgrades {date_str}" \
  --body "Automated security updates for system libraries." \
  || echo "PR may already exist"
""")

print("✅ PR step completed!")
