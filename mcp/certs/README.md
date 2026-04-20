# SSL Certificates

Place your TLS key and certificate here:

- `key.pem`  — private key
- `cert.pem` — certificate (self-signed or CA-issued)

## Generate a self-signed certificate (development only)

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
  -days 365 -nodes -subj "/CN=localhost"
```

These files are excluded from version control (see root `.gitignore`).
