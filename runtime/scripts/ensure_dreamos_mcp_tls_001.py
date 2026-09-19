#!/usr/bin/env python3
"""Ensure localhost TLS materials for Dream.OS MCP OAuth (harpoon requires https)."""

from __future__ import annotations

import argparse
import datetime
import ipaddress
from pathlib import Path

DEFAULT_DIR = Path.home() / ".local" / "state" / "tunnel-client" / "tls"
DEFAULT_CERT = DEFAULT_DIR / "dreamos-mcp-local.crt"
DEFAULT_KEY = DEFAULT_DIR / "dreamos-mcp-local.key"


def ensure_tls_materials(cert_path: Path, key_path: Path) -> tuple[Path, Path]:
    cert_path.parent.mkdir(parents=True, exist_ok=True)
    if cert_path.is_file() and key_path.is_file():
        return cert_path, key_path

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    now = datetime.datetime.now(datetime.UTC)
    san = x509.SubjectAlternativeName(
        [
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(days=825))
        .add_extension(san, critical=False)
        .sign(key, hashes.SHA256())
    )

    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    return cert_path, key_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure Dream.OS MCP localhost TLS cert")
    parser.add_argument("--cert", default=str(DEFAULT_CERT))
    parser.add_argument("--key", default=str(DEFAULT_KEY))
    args = parser.parse_args()
    cert, key = ensure_tls_materials(Path(args.cert), Path(args.key))
    print(f"CERT={cert}")
    print(f"KEY={key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
