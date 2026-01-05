import hashlib
import base64
import os

# Note: This is a hacky way to get the public key part from a PEM private key 
# Without a full cryptography library, we can try to find the sequence.
# But usually, it's easier to just trust the public_key.pem if it exists.

def get_id(pubkey_der):
    sha256 = hashlib.sha256(pubkey_der).hexdigest()
    hex_id = sha256[:32]
    ext_id = "".join(chr(int(c, 16) + ord('a')) for c in hex_id)
    return ext_id

def read_pem(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        lines = f.readlines()
        # Remove headers and joins
        content = "".join([l.strip() for l in lines if "-----" not in l])
        return base64.b64decode(content)

# The calculation for ID is actually from the SPKI DER data.
# public_key.pem should be that.

pk_der = read_pem("public_key.pem")
if pk_der:
    print(f"public_key.pem ID: {get_id(pk_der)}")

# Let's check if there's any other key
target_id = "mekebojdkoolcckoibjanfhfckknklhm"
print(f"Target ID:         {target_id}")
