# The Illustrated TLS 1.2 Connection

**Source:** https://tls.ulfheim.net/ (redirects to https://tls12.xargs.org/)
**Tags:** security
**Saved:** 2024-03-31

## TLS 1.2 Handshake Steps

### 1. Client Hello
Client initiates contact, offering cipher suites, supported curves, and extensions. Uses TLS 1.0 version (3,1) in the record layer for backward compatibility while negotiating TLS 1.2 (3,3).

### 2. Server Hello
Server selects cipher suite and confirms protocol version.

### 3. Server Certificate
Server presents its X.509 certificate containing its public key.

### 4. Server Key Exchange
Server generates an ephemeral keypair, sends the public key signed with its certificate's private key. This signature proves certificate ownership.

### 5. Server Hello Done
Signals the server has finished its hello messages.

### 6. Client Key Exchange
Client generates its own ephemeral keypair and sends its public key.

### 7. Key Derivation (both sides independently)
- Both perform elliptic curve multiplication (curve25519) using their private key and the peer's public key
- Both arrive at identical PreMasterSecret (32 bytes)
- PreMasterSecret expands into MasterSecret via HMAC-SHA256 in a PRF
- MasterSecret expands into final keys: MAC keys, cipher keys, and IVs

### 8. Change Cipher Spec
Both parties signal they're switching to encrypted communication.

### 9. Finished Messages
Both send authenticated handshake verification data (hash of all handshake messages), confirming the handshake wasn't tampered with.

### 10. Application Data
Encrypted payload exchange begins using AES-128-CBC with SHA-1 MAC.

## Record Types

| Type | Hex | Purpose |
|------|-----|---------|
| Handshake | 0x16 | Handshake messages |
| Application | 0x17 | Encrypted payload |
| Alert | 0x15 | Error/warning signals |

## Practical Notes

- Compression is disabled due to CRIME attack vulnerability
- Session resumption is supported (both sides cache session data) but not used in the illustrated example
- The ephemeral key exchange provides forward secrecy: compromising the certificate's private key later cannot decrypt previously captured traffic
