import os
import requests
from tqdm import tqdm

def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    filename = url.split('/')[-1]
    file_path = os.path.join(dest_folder, filename)
    
    if os.path.exists(file_path):
        print(f"File {filename} already exists. Skipping.")
        return file_path

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(file_path, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    
    return file_path

if __name__ == "__main__":
    BASE_URL = "https://dumps.wikimedia.org/plwiki/latest/"
    FILES = [
        "plwiki-latest-page.sql.gz",
        "plwiki-latest-pagelinks.sql.gz"
    ]
    DATA_DIR = "20 Projects/WikiSfera/data"
    
    print("🚀 Starting download from Wikimedia Dumps...")
    for f in FILES:
        download_file(BASE_URL + f, DATA_DIR)
    print("\n✅ Downloads complete.")
