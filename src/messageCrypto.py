import codecs
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from constants import Config
from cryptography.hazmat.primitives import serialization
import base64

def loadPublicKey(path):
    with open(path, "rb") as key_file:
        return serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

def loadPrivateKey(path):
    with open(path, 'rb') as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

def loadCertificate(path):
    with open(path, 'rb') as cert_file:
        return x509.load_pem_x509_certificate(
            cert_file.read(),
            backend=default_backend()
        )

def publicKeyToString(public_key):
    return base64Encode(public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo))
def publicKeyFromString(public_key_string):
    print(base64Decode(public_key_string))
    return serialization.load_pem_public_key(
            base64Decode(public_key_string),
            backend=default_backend()
        )

def base64Encode(bytes: bytes):
    return str(base64.urlsafe_b64encode(bytes),"utf-8")

def base64Decode(string: str):
    return base64.urlsafe_b64decode(bytes(string, "utf-8")) 
# Encrypt a message

def encryptMessageWithPublicKey(message:str, public_key):
    encrypted =  public_key.encrypt(
        codecs.encode(message,"utf-8"),
        padding.PKCS1v15()
    )
    print(encrypted)
    return base64Encode(encrypted)

# Sign the message
def signMessageWithPrivateKey(message:str, private_key):
    
    signature = private_key.sign(
        codecs.encode(message,"utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    print(signature)
    return base64Encode(signature)



# Decrypt the message
def msgDecript(ciphertext:str, private_key):
    plaintext= private_key.decrypt(
        base64Decode(ciphertext),
        padding.PKCS1v15()
    )
    print(plaintext)
    return str(plaintext, "utf-8")


# Verify the signature
def verifySignature(plaintext:str, public_key, signature:str):
    try:
        public_key.verify(
            base64Decode(signature),
            bytes(plaintext,"utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    

if __name__ == "__main__":
    encoded = base64Encode(b"Testing")
    
    print(encoded)
    
    decoded = base64Decode(encoded)
    
    print(decoded) 