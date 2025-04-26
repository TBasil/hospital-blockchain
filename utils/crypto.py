from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import hashlib

def generate_keys():
    private_key = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key.public_key()
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem.decode(), public_pem.decode()

def hash_data(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def sign_data(private_key_pem: str, data: str) -> str:
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None
    )
    signature = private_key.sign(
        data.encode(),
        ec.ECDSA(hashes.SHA256())
    )
    return signature.hex()