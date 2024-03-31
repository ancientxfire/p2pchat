import os
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.x509.oid import ExtensionOID, NameOID
from datetime import datetime, timedelta

from constants import Config

def generate_self_signed_certificate_and_keys(cert_file, private_key_file, public_key_file):
    # Generate a private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Extract the public key from the private key
    public_key = private_key.public_key()

    # Create a self-signed certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'My Organization'),
        x509.NameAttribute(NameOID.COMMON_NAME, 'My NAME')
    ])

    certificate_builder = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        public_key
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)  # Valid for 1 year
    )

    certificate = certificate_builder.sign(
        private_key,
        SHA256(),
        default_backend()
    )

    # Save the private key to a file in PKCS#8 format with the "-----BEGIN PRIVATE KEY-----" header
    with open(private_key_file, 'wb') as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Save the public key to a file in PEM format
    with open(public_key_file, 'wb') as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    # Save the certificate to a file in PEM format
    with open(cert_file, 'wb') as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))

    print(f'Private key saved to {private_key_file}')
    print(f'Public key saved to {public_key_file}')
    print(f'Certificate saved to {cert_file}')

def generateCertChainForServerAndClient():
    cert_file_server = Config.crypto.cert_file_server
    private_key_file_server = Config.crypto.private_key_file_server
    public_key_file_server = Config.crypto.public_key_file_server
    generate_self_signed_certificate_and_keys(cert_file_server, private_key_file_server, public_key_file_server)
    cert_file_client = Config.crypto.cert_file_client
    private_key_file_client = Config.crypto.private_key_file_client
    public_key_file_client = Config.crypto.public_key_file_client
    generate_self_signed_certificate_and_keys(cert_file_client, private_key_file_client, public_key_file_client)

def deleteCertChainForServerAndClient():
    cert_file_server = Config.crypto.cert_file_server
    private_key_file_server = Config.crypto.private_key_file_server
    public_key_file_server = Config.crypto.public_key_file_server
    cert_file_client = Config.crypto.cert_file_client
    private_key_file_client = Config.crypto.private_key_file_client
    public_key_file_client = Config.crypto.public_key_file_client
    os.remove(cert_file_server)
    os.remove(private_key_file_server)
    os.remove(public_key_file_server)
    os.remove(cert_file_client)
    os.remove(private_key_file_client)
    os.remove(public_key_file_client)

if __name__ == '__main__':
    generateCertChainForServerAndClient()