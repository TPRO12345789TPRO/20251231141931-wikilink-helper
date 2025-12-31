
import os
import shutil
import subprocess
import argparse
import sys

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

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
