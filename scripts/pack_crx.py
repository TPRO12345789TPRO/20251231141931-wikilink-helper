
import os
import shutil
import subprocess
import argparse
import sys


def get_chrome_path():
    if sys.platform == "win32":
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
        ]
        for p in paths:
            if os.path.exists(p):
                return p
    elif sys.platform == "darwin":
        path = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(path):
            return path
    elif sys.platform.startswith("linux"):
        for name in ["google-chrome", "chromium", "chromium-browser"]:
            path = shutil.which(name)
            if path:
                return path
    return None

CHROME_PATH = get_chrome_path()

if not CHROME_PATH:
    print("Error: Chrome executable not found.")
    sys.exit(1)

def pack_crx(source_dir, output_path, key_path):
    # Prepare a clean build directory to avoid packing unwanted files
    build_dir = "build_tmp"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    print(f"Preparing clean build in {build_dir}...")
    
    files_to_include = [
        "manifest.json", "popup.html", "popup.js", "styles.css", 
        "LICENSE", "README.md", "PRIVACY.md"
    ]
    dirs_to_include = ["assets", "src"]
    
    # Copy files
    for root_item in files_to_include:
        src = os.path.join(source_dir, root_item)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(build_dir, root_item))
    
    for root_item in dirs_to_include:
        src = os.path.join(source_dir, root_item)
        if os.path.exists(src):
            shutil.copytree(src, os.path.join(build_dir, root_item))
    
    # Strip "key" from manifest.json in the build directory to avoid Web Store errors
    import json
    manifest_path = os.path.join(build_dir, "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        if "key" in manifest:
            del manifest["key"]
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

    # Ensure key exists absolute path
    abs_key_path = os.path.abspath(key_path)
    abs_build_dir = os.path.abspath(build_dir)
    
    print(f"Packing extension using Chrome...")
    # chrome.exe --pack-extension=C:\path\to\ext --pack-extension-key=C:\path\to.pem
    cmd = [
        CHROME_PATH,
        f"--pack-extension={abs_build_dir}",
        f"--pack-extension-key={abs_key_path}"
    ]
    
    # chrome.exe runs asynchronously for GUI, but CLI args usually block or detach. 
    # Whatever, it produces the file in the parent dir of pack-extension dir.
    # i.e. build_tmp.crx next to build_tmp folder.
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Chrome packing output location:
    # If packed dir is 'build_tmp', output is 'build_tmp.crx' in the SAME FOLDER as 'build_tmp' (i.e. root)
    generated_crx = build_dir + ".crx"
    
    if os.path.exists(generated_crx):
        print(f"Chrome successfully created {generated_crx}")
        # Move to requested output path
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # Ensure output dir exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        shutil.move(generated_crx, output_path)
        print(f"Moved to: {output_path}")

        # Also create a Source ZIP for Web Store
        zip_output_path = output_path.replace(".crx", ".zip")
        if os.path.exists(zip_output_path):
            os.remove(zip_output_path)
        
        print(f"Creating source zip: {zip_output_path}")
        shutil.make_archive(zip_output_path.replace(".zip", ""), 'zip', build_dir)
        
        # Cleanup
        shutil.rmtree(build_dir)
        print("Cleanup done.")
    else:
        print("Error: CRX file was not generated.")
        print("Chrome stderr:", result.stderr)
        print("Chrome stdout:", result.stdout)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Source directory")
    parser.add_argument("output", help="Output CRX path")
    parser.add_argument("--key", default="key.pem", help="Path to private key")
    args = parser.parse_args()
    
    import datetime
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # If output is a directory, construct filename. If it's a file, prepend timestamp to basename.
    # Actually, simplistic approach: explicit output path is usually expected.
    # But user wants "2025...-wikilink-helper...crx"
    
    dir_name = os.path.dirname(args.output)
    base_name = os.path.basename(args.output)
    
    # Prepend timestamp
    new_name = f"{timestamp}-{base_name}"
    final_output = os.path.join(dir_name, new_name)
    
    pack_crx(args.source, final_output, args.key)
