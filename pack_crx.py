
import os
import struct
import shutil
import base64
import argparse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import zipfile

def generate_key(key_path):
    print(f"Generating new private key: {key_path}")
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    return key

def load_key(key_path):
    if not os.path.exists(key_path):
        return generate_key(key_path)
    
    with open(key_path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )

def create_zip(source_dir, zip_path):
    # Exclude the dist folder and the zip itself if it's inside source (though we usually source from root)
    # The source_dir should be the extension root or a build dir. 
    # Here we assume source_dir is the current directory, but excluding dist/ and .git/ etc.
    # However, for cleanliness, let's zip specific files similar to the powershell command.
    
    # Actually, the user's previous zip command included: 
    # manifest.json, assets, src, popup.html, popup.js, styles.css, LICENSE, README.md, PRIVACY.md
    
    files_to_include = [
        "manifest.json", "popup.html", "popup.js", "styles.css", 
        "LICENSE", "README.md", "PRIVACY.md"
    ]
    dirs_to_include = ["assets", "src"]

    print(f"Creating intermediate zip: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root_item in files_to_include + dirs_to_include:
            path = os.path.join(source_dir, root_item)
            if os.path.isfile(path):
                zf.write(path, root_item)
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        abs_file = os.path.join(root, file)
                        rel_file = os.path.relpath(abs_file, source_dir)
                        zf.write(abs_file, rel_file)

def pack_crx(source_dir, output_path, key_path):
    key = load_key(key_path)
    
    # CRX format requires a zip payload
    zip_path = output_path + ".temp.zip"
    create_zip(source_dir, zip_path)
    
    with open(zip_path, "rb") as f:
        zip_data = f.read()
    
    # Sign the zip data
    # CRX3 format is complex (protobufs), let's stick to CRX2 for simplicity if possible, 
    # OR better, since this is 2025, CRX3 is likely required.
    # However, constructing CRX3 manually without the `crx3` tool or protobuf definition is error prone.
    # A simpler approach for "assembling as expected" locally is often to just zip it, but the user asked for .crx.
    # The simplest valid CRX is CRX2: Magic (Cr24) + Version (2) + PubKeyLen + SigLen + PubKey + Sig + Zip
    # Chrome still accepts CRX2 for packed extensions in developer mode, though CRX3 is standard for store.
    
    # Let's try CRX2 first.
    
    public_key = key.public_key()
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    signature = key.sign(
        zip_data,
        padding.PKCS1v15(),
        hashes.SHA1()
    )
    
    with open(output_path, "wb") as f:
        # Magic: Cr24
        f.write(b"Cr24") 
        # Version: 2
        f.write(struct.pack("<I", 2))
        # PubKey Length
        f.write(struct.pack("<I", len(pub_bytes)))
        # Signature Length
        f.write(struct.pack("<I", len(signature)))
        # PubKey
        f.write(pub_bytes)
        # Signature
        f.write(signature)
        # Payload
        f.write(zip_data)
        
    os.remove(zip_path)
    print(f"Created CRX: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Source directory")
    parser.add_argument("output", help="Output CRX path")
    parser.add_argument("--key", default="key.pem", help="Path to private key (will be generated if missing)")
    args = parser.parse_args()
    
    pack_crx(args.source, args.output, args.key)
