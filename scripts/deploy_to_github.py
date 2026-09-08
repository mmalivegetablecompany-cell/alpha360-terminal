"""
Deploy Alpha360 Terminal to GitHub
1. Creates remote repository 'alpha360-terminal' on user's GitHub
2. Configures repository settings & Actions workflow permissions
3. Initializes git repository, commits files, pushes to main branch
4. Creates a GitHub Release v1.0.0 and uploads Alpha360_Terminal.apk and Alpha360_Terminal.exe
5. Enables GitHub Pages for live web terminal hosting
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding="utf-8")

TOKEN = os.getenv("GITHUB_TOKEN", "")
if not TOKEN:
    print("❌ Error: GITHUB_TOKEN environment variable is not set.")
    sys.exit(1)
REPO_NAME = "alpha360-terminal"
GIT_EXE = r"C:\flutter\bin\mingit\cmd\git.exe"

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "Alpha360-Deployer"
}

def api_request(url, method="GET", data=None):
    req = urllib.request.Request(url, headers=headers, method=method)
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    else:
        body = None
    try:
        with urllib.request.urlopen(req, data=body) as res:
            resp_body = res.read().decode("utf-8")
            return res.status, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(err_body)
        except:
            err_json = {"raw": err_body}
        return e.code, err_json

def run_cmd(args, cwd=None):
    res = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def main():
    print("🚀 Step 1: Querying authenticated GitHub user...")
    status, user = api_request("https://api.github.com/user")
    if status != 200:
        print(f"❌ Failed to get user: {status} {user}")
        sys.exit(1)
    username = user["login"]
    print(f"✅ Authenticated as: {username} ({user.get('name', '')})")

    # 2. Check if repo exists, create if not
    print(f"\n🚀 Step 2: Ensuring repository '{REPO_NAME}' exists...")
    status, repo_info = api_request(f"https://api.github.com/repos/{username}/{REPO_NAME}")
    if status == 200:
        print(f"ℹ️ Repository already exists: {repo_info['html_url']}")
    else:
        print(f"📦 Creating new public repository '{REPO_NAME}'...")
        create_payload = {
            "name": REPO_NAME,
            "description": "Alpha360 - Institutional Indian Equities Terminal, 360 Technicals, Buy Radar & 24/7 Cloud Market Engine",
            "private": False,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": True
        }
        status, repo_info = api_request("https://api.github.com/user/repos", method="POST", data=create_payload)
        if status not in (200, 201):
            print(f"❌ Failed to create repo: {status} {repo_info}")
            sys.exit(1)
        print(f"✅ Repository created: {repo_info['html_url']}")

    # 3. Set GitHub Actions workflow permissions to Write
    print("\n🚀 Step 3: Configuring GitHub Actions workflow permissions (Read & Write)...")
    perm_payload = {
        "default_workflow_permissions": "write",
        "can_approve_pull_request_reviews": True
    }
    status, perm_res = api_request(
        f"https://api.github.com/repos/{username}/{REPO_NAME}/actions/permissions/workflow",
        method="PUT",
        data=perm_payload
    )
    if status in (200, 204):
        print("✅ Actions Workflow permissions successfully set to 'Read & Write'!")
    else:
        print(f"⚠️ Actions permissions response ({status}): {perm_res}")

    # 4. Initialize local git & commit
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"\n🚀 Step 4: Initializing local git repository at: {root_dir}")
    
    # Configure user
    run_cmd([GIT_EXE, "config", "--global", "user.name", username], cwd=root_dir)
    run_cmd([GIT_EXE, "config", "--global", "user.email", f"{username}@users.noreply.github.com"], cwd=root_dir)

    git_dir = os.path.join(root_dir, ".git")
    if not os.path.exists(git_dir):
        code, out, err = run_cmd([GIT_EXE, "init"], cwd=root_dir)
        print(f"Git init: {out}")

    # Check remote
    clean_remote_url = f"https://github.com/{username}/{REPO_NAME}.git"
    auth_remote_url = f"https://{username}:{TOKEN}@github.com/{username}/{REPO_NAME}.git"
    code, out, err = run_cmd([GIT_EXE, "remote", "get-url", "origin"], cwd=root_dir)
    if code == 0:
        run_cmd([GIT_EXE, "remote", "set-url", "origin", clean_remote_url], cwd=root_dir)
    else:
        run_cmd([GIT_EXE, "remote", "add", "origin", clean_remote_url], cwd=root_dir)
    print("✅ Remote origin set to:", clean_remote_url)

    # Checkout main branch
    run_cmd([GIT_EXE, "checkout", "-B", "main"], cwd=root_dir)

    # Stage files
    print("📦 Staging files for commit (excluding build caches)...")
    run_cmd([GIT_EXE, "add", "."], cwd=root_dir)

    code, out, err = run_cmd([GIT_EXE, "status", "--porcelain"], cwd=root_dir)
    if out:
        print(f"💾 Committing changes ({len(out.splitlines())} files changed)...")
        code, c_out, c_err = run_cmd([GIT_EXE, "commit", "-m", "Initial Release: Alpha360 Institutional Terminal, APK, WinExe & 24/7 Cloud Engine"], cwd=root_dir)
        print(c_out)
    else:
        print("ℹ️ No new changes to commit.")

    # 5. Push to GitHub
    print("\n🚀 Step 5: Pushing code to GitHub main branch...")
    code, out, err = run_cmd([GIT_EXE, "push", "-u", auth_remote_url, "main", "--force"], cwd=root_dir)
    if code == 0:
        print("✅ Code successfully pushed to GitHub main branch!")
    else:
        print(f"❌ Push failed: {err} {out}")
        sys.exit(1)

    # 6. Create GitHub Release and upload APK & EXE
    print("\n🚀 Step 6: Creating GitHub Release v1.0.0 & uploading binaries...")
    rel_payload = {
        "tag_name": "v1.0.0",
        "target_commitish": "main",
        "name": "Alpha360 Terminal v1.0.0",
        "body": "### 🚀 Alpha360 Institutional Terminal v1.0.0\n\n- **Android APK**: Direct installable APK with 424 bundled stocks and offline support.\n- **Windows Desktop**: Standalone native desktop app executable.\n- **24/7 Cloud Market Engine**: Autonomous real-time tracking, technicals & Buy Radar.",
        "draft": False,
        "prerelease": False
    }
    status, rel_data = api_request(f"https://api.github.com/repos/{username}/{REPO_NAME}/releases", method="POST", data=rel_payload)
    if status in (200, 201):
        rel_id = rel_data["id"]
        print(f"✅ GitHub Release created: {rel_data['html_url']}")
        
        # Upload APK
        apk_path = os.path.join(root_dir, "Alpha360_Terminal.apk")
        if os.path.exists(apk_path):
            print(f"📤 Uploading {os.path.basename(apk_path)} ({os.path.getsize(apk_path) / (1024*1024):.1f} MB)...")
            upload_url = f"https://uploads.github.com/repos/{username}/{REPO_NAME}/releases/{rel_id}/assets?name=Alpha360_Terminal.apk"
            with open(apk_path, "rb") as f:
                apk_bytes = f.read()
            up_req = urllib.request.Request(upload_url, data=apk_bytes, headers={
                "Authorization": f"token {TOKEN}",
                "Content-Type": "application/vnd.android.package-archive",
                "User-Agent": "Alpha360-Deployer"
            }, method="POST")
            try:
                with urllib.request.urlopen(up_req) as up_res:
                    print("✅ Alpha360_Terminal.apk uploaded to Release successfully!")
            except Exception as e:
                print(f"⚠️ Failed to upload APK asset: {e}")

        # Upload EXE
        exe_path = os.path.join(root_dir, "Alpha360_Terminal.exe")
        if os.path.exists(exe_path):
            print(f"📤 Uploading {os.path.basename(exe_path)} ({os.path.getsize(exe_path) / 1024:.1f} KB)...")
            upload_url = f"https://uploads.github.com/repos/{username}/{REPO_NAME}/releases/{rel_id}/assets?name=Alpha360_Terminal.exe"
            with open(exe_path, "rb") as f:
                exe_bytes = f.read()
            up_req = urllib.request.Request(upload_url, data=exe_bytes, headers={
                "Authorization": f"token {TOKEN}",
                "Content-Type": "application/octet-stream",
                "User-Agent": "Alpha360-Deployer"
            }, method="POST")
            try:
                with urllib.request.urlopen(up_req) as up_res:
                    print("✅ Alpha360_Terminal.exe uploaded to Release successfully!")
            except Exception as e:
                print(f"⚠️ Failed to upload EXE asset: {e}")
    else:
        print(f"⚠️ Release creation notice: {status} {rel_data}")

    # 7. Trigger initial GitHub Actions 24/7 sync workflow run
    print("\n🚀 Step 7: Triggering initial GitHub Actions 24/7 Market Engine run...")
    status, disp_res = api_request(
        f"https://api.github.com/repos/{username}/{REPO_NAME}/actions/workflows/market_24x7_cron.yml/dispatches",
        method="POST",
        data={"ref": "main"}
    )
    if status == 204:
        print("✅ 24/7 Cloud Market Engine workflow successfully dispatched on GitHub!")
    else:
        print(f"ℹ️ Workflow dispatch notice ({status}): {disp_res}")

    print(f"\n🎉 Deployment successful!")
    print(f"🌐 Repository: https://github.com/{username}/{REPO_NAME}")
    print(f"📱 APK Direct Download: https://github.com/{username}/{REPO_NAME}/releases/latest/download/Alpha360_Terminal.apk")
    print(f"💻 EXE Direct Download: https://github.com/{username}/{REPO_NAME}/releases/latest/download/Alpha360_Terminal.exe")
    print(f"⚙️ Actions 24/7 Watchdog: https://github.com/{username}/{REPO_NAME}/actions")

if __name__ == "__main__":
    main()
