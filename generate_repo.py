import urllib.request
import json
import os
import sys
import re

SOURCE_REPO = "arichornlover/TrollStore-DEBs"
OUTPUT_FILE = "apps.json"

def clean_app_name(filename):
    name = re.sub(r'\.ipa$', '', filename, flags=re.IGNORECASE)
    name = name.replace('_', ' ').replace('-', ' ')
    return name.strip()

def generate_bundle_id(name):
    clean = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    return f"com.trollstore.{clean}"

def fetch_latest_release():
    url = f"https://api.github.com/repos/{SOURCE_REPO}/releases/latest"
    headers = {'User-Agent': 'ESign-Auto-Builder'}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers['Authorization'] = f'Bearer {token}'
        
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def main():
    print(f"Đang quét toàn bộ danh sách IPA từ {SOURCE_REPO}...")
    try:
        release = fetch_latest_release()
    except Exception as e:
        print(f"Lỗi khi kết nối GitHub API: {e}")
        sys.exit(1)

    tag_version = release.get("tag_name", "").lstrip("v")
    pub_date = release.get("published_at", "").split("T")[0]
    assets = release.get("assets", [])

    apps_list = []

    for asset in assets:
        filename = asset.get("name", "")
        if not filename.lower().endswith(".ipa"):
            continue

        download_url = asset.get("browser_download_url")
        size = asset.get("size", 0)
        app_name = clean_app_name(filename)
        bundle_id = generate_bundle_id(app_name)

        apps_list.append({
            "name": app_name,
            "bundleIdentifier": bundle_id,
            "version": tag_version,
            "versionDate": pub_date,
            "size": size,
            "downloadURL": download_url,
            "iconURL": "https://raw.githubusercontent.com/arichornlover/TrollStore-DEBs/main/icon.png",
            "localizedDescription": f"Bản build mod {app_name} từ kho TrollStore-DEBs."
        })

    repo_structure = {
        "name": "TrollStore Community Apps",
        "identifier": "com.trollstore.community.repo",
        "apps": apps_list
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(repo_structure, f, indent=2, ensure_ascii=False)

    print(f"Đã tạo thành công {len(apps_list)} ứng dụng vào file {OUTPUT_FILE}!")

if __name__ == "__main__":
    main()
