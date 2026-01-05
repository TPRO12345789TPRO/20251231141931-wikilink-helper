import hashlib
import base64

def get_id(pubkey_b64):
    # Decode the base64 public key
    pubkey_der = base64.b64decode(pubkey_b64)
    # Get SHA256 hash
    sha256 = hashlib.sha256(pubkey_der).hexdigest()
    # Take first 32 characters
    hex_id = sha256[:32]
    # Map hex characters (0-f) to (a-p)
    ext_id = "".join(chr(int(c, 16) + ord('a')) for c in hex_id)
    return ext_id

key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxqLdGtLnZUG9ZRXXcKIgxPeEFzfJWDFmSQ4ScnxQDwpA+AMXC8ghwvdYg1ADIBuhvtB2d1yEMiWxfDGXaHaEUuVRP6twIYV1bqhNKbWZAvxJXrb9S0hSWM0T3jxe7UtDhq5Fdl8uaPSt9CiNn3c8BUGrVmx7aM0ekiLfnJV+h8t2Yiqy61+voD31yo6cO6o3UDGblet0LClrYspgsSUnJfgg1NmEb+lqghmwUgFICj3qtcoF9DLpQsy5CHAs24QAC2LOO2M20bU5KQmBSJcL0xgK2MeR5P5LeECDDFjx2SVc5rTxiDK4s0A0ZmUzUYfoa4jO+zlcdW5PSLmIZ2JBHwIDAQAB"
print(f"Calculated ID: {get_id(key)}")
print(f"Target ID:     mekebojdkoolcckoibjanfhfckknklhm")
