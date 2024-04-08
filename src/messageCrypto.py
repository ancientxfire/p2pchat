import codecs
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from constants import Config
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
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
    message = base64.urlsafe_b64encode(bytes(message,"utf-8"),)
    encrypted =  public_key.encrypt(
        message,
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
    plaintext = base64.urlsafe_b64decode(str(plaintext,"utf-8"),)
    
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

class aesCrypto:
    def encrypt(message:str, key:bytes):
        messageBytes = bytes(message, "utf-16")
        print(messageBytes)
        print(key)
        print(b"cccc     "+key)
        try:
            loaded_key = Fernet(key)
            ciphertext = base64Encode(loaded_key.encrypt(messageBytes))
            print(ciphertext)
            return ciphertext
        except Exception as e:
            print(e)
            return None
    def decrypt(message:str, key):
        try:
            loaded_key = Fernet(key)
            message = base64Decode(message)
            return str(loaded_key.decrypt(message), "utf-16")
        except Exception as e:
            print(e)
            return None
    def generateKey():
        return Fernet.generate_key()

if __name__ == "__main__":
    key = b'S2789l-d5kF-fUFu4Vj4P0dHtr5PBmnGmy6l0R9pQK0='
    print(key)
    cyphertext = aesCrypto.encrypt("Message", key)
    print(cyphertext)
    
    cleatext = (aesCrypto.decrypt(cyphertext,key))
    print(cleatext)