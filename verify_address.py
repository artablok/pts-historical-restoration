import hashlib
from ecdsa import SigningKey, SECP256k1
from ecdsa.util import number_to_string

priv_hex = "c06a0a2b50ea96c1e5416379fd015e2f55c4fa009c986c70e6008bc9c60700aa"
expected_pts_address = "PYvLDeNVkH3yPCQSCqTbdxH8GBnm7MBfvt"

priv_bytes = bytes.fromhex(priv_hex)
sk = SigningKey.from_string(priv_bytes, curve=SECP256k1)
vk = sk.get_verifying_key()

# Compressed pubkey (SEC format): 0x02/0x03 prefix + 32-byte X coordinate
point = vk.pubkey.point
x = point.x()
y = point.y()
prefix = b'\x02' if y % 2 == 0 else b'\x03'
compressed_pubkey = prefix + x.to_bytes(32, 'big')

print("Compressed pubkey (hex):", compressed_pubkey.hex())

# Algorithm from pts_address.cpp:
# sha2 = sha256(compressed_pubkey)
# rep = ripemd160(sha2)
# addr[0] = version (56)
# addr[1:21] = rep
# check = sha256(sha256(addr[0:21]))[0:4]
# addr[21:25] = check
# base58(addr)

sha2 = hashlib.sha256(compressed_pubkey).digest()
rep = hashlib.new('ripemd160', sha2).digest()

version = bytes([56])
addr_no_checksum = version + rep  # 21 bytes
check = hashlib.sha256(hashlib.sha256(addr_no_checksum).digest()).digest()[:4]
full_addr_bytes = addr_no_checksum + check  # 25 bytes

print("Full address bytes (hex):", full_addr_bytes.hex())

# Base58 encode (standard Bitcoin-style base58, with leading-zero handling)
B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def base58_encode(b: bytes) -> str:
    n = int.from_bytes(b, 'big')
    res = ''
    while n > 0:
        n, r = divmod(n, 58)
        res = B58_ALPHABET[r] + res
    # leading zero bytes -> leading '1's
    n_leading_zeros = len(b) - len(b.lstrip(b'\x00'))
    return B58_ALPHABET[0] * n_leading_zeros + res

computed_address = base58_encode(full_addr_bytes)

print("\n=== RESULT ===")
print("Computed pts address: ", computed_address)
print("Expected pts address: ", expected_pts_address)
print("MATCH:", computed_address == expected_pts_address)
