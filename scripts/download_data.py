# download_data.py
import requests
import os
import time

# direct  download links from PatentsView's AWS servers
# These are the actual working URLs from PatentsView
DOWNLOAD_URLS = {
    "g_patent":                   "https://s3.amazonaws.com/data.patentsview.org/download/g_patent.tsv.zip",
    "g_inventor_disambiguated":   "https://s3.amazonaws.com/data.patentsview.org/download/g_inventor_disambiguated.tsv.zip",
    "g_assignee_disambiguated":   "https://s3.amazonaws.com/data.patentsview.org/download/g_assignee_disambiguated.tsv.zip",
    "g_patent_inventor":          "https://s3.amazonaws.com/data.patentsview.org/download/g_patent_inventor.tsv.zip",
    "g_patent_assignee":          "https://s3.amazonaws.com/data.patentsview.org/download/g_patent_assignee.tsv.zip",
    "g_location_disambiguated":   "https://s3.amazonaws.com/data.patentsview.org/download/g_location_disambiguated.tsv.zip",
}

SAVE_DIR = "data/raw"
os.makedirs(SAVE_DIR, exist_ok=True)

def download_file(name, url):
    save_path = os.path.join(SAVE_DIR, f"{name}.tsv.zip")
    if os.path.exists(save_path):
        print(f" Already downloaded: {name}")
        return

    print(f"⬇ Downloading {name}... (this may take a while, files are large)")
    retries = 0
    while retries < 5:
        try:
            response = requests.get(url, stream=True, timeout=120)
            if response.status_code == 200:
                total = int(response.headers.get('content-length', 0))
                downloaded = 0
                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                        f.write(chunk)
                        downloaded += len(chunk)
                        mb = downloaded / (1024 * 1024)
                        print(f"\r   {mb:.1f} MB downloaded...", end="")
                print(f"\n Saved: {save_path}")
                return
            elif response.status_code == 429:
                print("Rate limited. Waiting 10s...")
                time.sleep(10)
                retries += 1
            else:
                print(f"Failed with status {response.status_code}")
                break
        except Exception as e:
            print(f"Error: {e}")
            retries += 1
            time.sleep(5)

if __name__ == "__main__":
    print("Starting PatentsView bulk data download...")
    print("WARNING: These files are large (100MB - 1GB each). Make sure you have space!\n")
    for name, url in DOWNLOAD_URLS.items():
        download_file(name, url)
    print("\n All downloads complete!")