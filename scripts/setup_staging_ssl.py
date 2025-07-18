#!/usr/bin/env python3
"""Setup SSL/TLS certificates for staging environment."""

import subprocess
from datetime import datetime
from pathlib import Path


def create_ssl_directories(project_root: Path) -> Path:
    """Create SSL directories for staging certificates."""
    ssl_dir = project_root / "ssl" / "staging"
    ssl_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (ssl_dir / "certs").mkdir(exist_ok=True)
    (ssl_dir / "private").mkdir(exist_ok=True)
    (ssl_dir / "config").mkdir(exist_ok=True)

    return ssl_dir


def create_openssl_config(ssl_dir: Path) -> Path:
    """Create OpenSSL configuration for staging certificates."""
    config_content = """# OpenSSL configuration for FLEXT staging environment
[ req ]
default_bits = 4096
prompt = no
distinguished_name = req_distinguished_name
req_extensions = v3_req

[ req_distinguished_name ]
C = US
ST = Development
L = Staging
O = FLEXT Framework
OU = Development Team
CN = internal.invalid

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = internal.invalid
DNS.2 = internal.invalid
DNS.3 = localhost
DNS.4 = 127.0.0.1
IP.1 = 127.0.0.1
IP.2 = ::1
"""

    config_file = ssl_dir / "config" / "staging.conf"
    with Path(config_file).open("w", encoding="utf-8") as f:
        f.write(config_content)

    print(f"✅ OpenSSL config created: {config_file}")
    return config_file


def generate_staging_certificates(
    ssl_dir: Path, config_file: Path,
) -> tuple[Path, Path]:
    """Generate self-signed SSL certificates for staging."""

    # Paths for certificate files
    private_key = ssl_dir / "private" / "staging.key"
    cert_file = ssl_dir / "certs" / "staging.crt"

    # Generate private key
    print("🔑 Generating private key...")
    subprocess.run(
        ["openssl", "genrsa", "-out", str(private_key), "4096"],
        check=True,
        capture_output=True,
    )

    # Set proper permissions for private key
    private_key.chmod(0o600)

    # Generate certificate signing request and self-signed certificate
    print("📜 Generating self-signed certificate...")
    subprocess.run(
        [
            "openssl",
            "req",
            "-new",
            "-x509",
            "-key",
            str(private_key),
            "-out",
            str(cert_file),
            "-days",
            "365",
            "-config",
            str(config_file),
            "-extensions",
            "v3_req",
        ],
        check=True,
        capture_output=True,
    )

    print(f"✅ Private key: {private_key}")
    print(f"✅ Certificate: {cert_file}")

    return private_key, cert_file


def create_nginx_config(ssl_dir: Path, private_key: Path, cert_file: Path) -> None:
    """Create Nginx configuration for staging SSL."""

    nginx_config = f"""# FLEXT Staging Nginx SSL Configuration
# Generated: {datetime.now().isoformat()}

# API Server (SSL)
server {{
    listen 443 ssl http2;
    server_name internal.invalid;

    # SSL Configuration
    ssl_certificate {cert_file};
    ssl_certificate_key {private_key};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Proxy to API server
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }}
}}

# Web Interface (SSL)
server {{
    listen 443 ssl http2;
    server_name internal.invalid;

    # SSL Configuration (same as API)
    ssl_certificate {cert_file};
    ssl_certificate_key {private_key};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Proxy to web server
    location / {{
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }}
}}

# HTTP to HTTPS redirect
server {{
    listen 80;
    server_name internal.invalid internal.invalid;
    return 301 https://$server_name$request_uri;
}}
"""

    nginx_file = ssl_dir / "config" / "nginx-staging-ssl.conf"
    with Path(nginx_file).open("w", encoding="utf-8") as f:
        f.write(nginx_config)

    print(f"✅ Nginx SSL config: {nginx_file}")


def create_hosts_entries(ssl_dir: Path) -> None:
    """Create hosts file entries for staging domains."""

    hosts_content = """# FLEXT Staging SSL Domains
# Add these entries to your /etc/hosts file:

127.0.0.1    internal.invalid
127.0.0.1    internal.invalid
"""

    hosts_file = ssl_dir / "config" / "hosts-staging.txt"
    with Path(hosts_file).open("w", encoding="utf-8") as f:
        f.write(hosts_content)

    print(f"✅ Hosts entries: {hosts_file}")
    print("📝 Add these to your /etc/hosts file:")
    print("    127.0.0.1    internal.invalid")
    print("    127.0.0.1    internal.invalid")


def update_staging_ssl_config(
    project_root: Path, private_key: Path, cert_file: Path,
) -> None:
    """Update staging environment configuration with SSL settings."""

    # Update API staging config
    api_env_file = project_root / "flext-api" / ".env.staging"

    # Read current config
    with Path(api_env_file).open(encoding="utf-8") as f:
        config_content = f.read()

    # Add SSL configuration
    ssl_config = f"""
# SSL/TLS Configuration (staging)
FLEXT_API_USE_SSL=true
FLEXT_API_SSL_CERT_PATH={cert_file}
FLEXT_API_SSL_KEY_PATH={private_key}
FLEXT_API_SSL_VERIFY_MODE=false  # Self-signed for staging
FLEXT_API_FORCE_HTTPS=true
"""

    # Append SSL config if not already present
    if "SSL/TLS Configuration" not in config_content:
        with Path(api_env_file).open("a", encoding="utf-8") as f:
            f.write(ssl_config)
        print(f"✅ Updated API SSL config: {api_env_file}")

    # Update Web staging config
    web_env_file = project_root / "flext-web" / ".env.staging"

    # Update web config to use HTTPS
    with Path(web_env_file).open(encoding="utf-8") as f:
        web_content = f.read()

    # Enable SSL security settings
    web_content = web_content.replace(
        "SECURE_SSL_REDIRECT=false", "SECURE_SSL_REDIRECT=true",
    )
    web_content = web_content.replace(
        "SESSION_COOKIE_SECURE=false", "SESSION_COOKIE_SECURE=true",
    )
    web_content = web_content.replace(
        "CSRF_COOKIE_SECURE=false", "CSRF_COOKIE_SECURE=true",
    )

    with Path(web_env_file).open("w", encoding="utf-8") as f:
        f.write(web_content)

    print(f"✅ Updated Web SSL config: {web_env_file}")


def create_ssl_test_script(ssl_dir: Path) -> None:
    """Create script to test SSL configuration."""

    test_script = f"""#!/bin/bash
# Test FLEXT staging SSL configuration

echo "🔒 Testing FLEXT Staging SSL Configuration"
echo "=================================================="

# Test certificate validity
echo "📜 Testing certificate validity..."
openssl x509 -in {ssl_dir}/certs/staging.crt -text -noout | grep -E "(Subject:|DNS:|IP Address:)"

echo ""
echo "🌐 Testing SSL endpoints..."

# Test API endpoint
echo "Testing API (https://internal.invalid/REDACTED)..."
curl -k -s -o /dev/null -w "Status: %{{http_code}}\\n" https://internal.invalid/REDACTED || echo "❌ API not responding"

# Test Web endpoint
echo "Testing Web (https://internal.invalid/REDACTED)..."
curl -k -s -o /dev/null -w "Status: %{{http_code}}\\n" https://internal.invalid/REDACTED || echo "❌ Web not responding"

echo ""
echo "🔍 SSL Certificate Information:"
echo "Certificate: {ssl_dir}/certs/staging.crt"
echo "Private Key: {ssl_dir}/private/staging.key"
echo "Nginx Config: {ssl_dir}/config/nginx-staging-ssl.conf"

echo ""
echo "📝 Setup Instructions:"
echo "1. Add hosts entries to /etc/hosts:"
echo "   sudo bash -c 'cat {ssl_dir}/config/hosts-staging.txt >> /etc/hosts'"
echo "2. Install/configure Nginx with SSL config"
echo "3. Start FLEXT services with staging environment"
echo "4. Test with: curl -k https://internal.invalid/REDACTED"
"""

    test_file = ssl_dir / "test-ssl.sh"
    with Path(test_file).open("w", encoding="utf-8") as f:
        f.write(test_script)

    # Make executable
    test_file.chmod(0o755)

    print(f"✅ SSL test script: {test_file}")


def main():
    """Setup complete SSL/TLS configuration for staging."""
    print("🔒 FLEXT STAGING SSL/TLS SETUP")
    print("=" * 50)

    project_root = Path(__file__).parent.parent

    # Check if OpenSSL is available
    try:
        subprocess.run(["openssl", "version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ OpenSSL not found. Please install OpenSSL first.")
        return

    # Create SSL directory structure
    print("📁 Creating SSL directory structure...")
    ssl_dir = create_ssl_directories(project_root)

    # Create OpenSSL configuration
    print("⚙️ Creating OpenSSL configuration...")
    config_file = create_openssl_config(ssl_dir)

    # Generate certificates
    print("🔐 Generating SSL certificates...")
    private_key, cert_file = generate_staging_certificates(ssl_dir, config_file)

    # Create Nginx configuration
    print("🌐 Creating Nginx SSL configuration...")
    create_nginx_config(ssl_dir, private_key, cert_file)

    # Create hosts entries
    print("📝 Creating hosts file entries...")
    create_hosts_entries(ssl_dir)

    # Update staging configuration
    print("⚙️ Updating staging environment configuration...")
    update_staging_ssl_config(project_root, private_key, cert_file)

    # Create test script
    print("🧪 Creating SSL test script...")
    create_ssl_test_script(ssl_dir)

    print("\n" + "=" * 50)
    print("🎉 STAGING SSL/TLS SETUP COMPLETED!")

    print("\n🔒 SSL CERTIFICATE DETAILS:")
    print(f"  📜 Certificate: {cert_file}")
    print(f"  🔑 Private Key: {private_key}")
    print("  📅 Valid for: 365 days")
    print("  🌐 Domains: internal.invalid, internal.invalid")

    print("\n📝 NEXT STEPS:")
    print(
        "  1. Add hosts entries: sudo bash -c 'cat ssl/staging/config/hosts-staging.txt >> /etc/hosts'",
    )
    print("  2. Install Nginx and use ssl/staging/config/nginx-staging-ssl.conf")
    print("  3. Start FLEXT services with staging environment")
    print("  4. Test SSL: ./ssl/staging/test-ssl.sh")

    print("\n⚠️  SECURITY NOTES:")
    print("  • These are self-signed certificates for staging only")
    print("  • Browsers will show security warnings - this is expected")
    print("  • Use proper CA-signed certificates for production")


if __name__ == "__main__":
    main()
