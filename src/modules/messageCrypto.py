from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
# server
# Load private key from PEM file
with open("private_key_server.pem", "rb") as key_file:
    private_key_server = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

# Load certificate from PEM file
with open("certificate_server.pem", "rb") as cert_file:
    certificate_server = x509.load_pem_x509_certificate(
        cert_file.read(),
        backend=default_backend()
    )

# Load public key from PEM file
with open("public_key_server.pem", "rb") as key_file:
    public_key_server = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )
# client
# Load private key from PEM file
with open("private_key.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

# Load certificate from PEM file
with open("certificate.pem", "rb") as cert_file:
    certificate = x509.load_pem_x509_certificate(
        cert_file.read(),
        backend=default_backend()
    )

# Load public key from PEM file
with open("public_key.pem", "rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )

# Encrypt a message
message = b"the secret message"
def encryptMessageWithPublicKey(message, public_key):
    return public_key.encrypt(
        message,
        padding.PKCS1v15()
    )

# Sign the message
def signMessageWithPrivateKey(message, private_key):
    
    return private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )



# Decrypt the message
def msgDecript(ciphertext, private_key):
    return private_key.decrypt(
        ciphertext,
        padding.PKCS1v15()
    )



# Verify the signature
def verifySignature(plaintext, public_key, signature):
    try:
        public_key.verify(
            signature,
            plaintext,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
ciphertext= encryptMessageWithPublicKey(message, public_key_server)

signature = signMessageWithPrivateKey(message, private_key)
plaintext = msgDecript(ciphertext=ciphertext,private_key=private_key_server)
print(verifySignature(plaintext, public_key=public_key,signature=signature))

print(plaintext)
