---
url: "https://tls.ulfheim.net/"
title: "The Illustrated TLS Connection"
source: "pocket-export"
date_processed: 2026-04-02
confidence: high
insight_summary: "Byte-by-byte explanation of every step in a TLS 1.2 handshake, making the protocol internals tangible by showing the actual hex values exchanged between client and server."
concepts:
  - "security"
  - "networking"
---

# The Illustrated TLS Connection

> [Original](https://tls.ulfheim.net/)

## Key Insight

Byte-by-byte explanation of every step in a TLS 1.2 handshake, making the protocol internals tangible by showing the actual hex values exchanged between client and server.

## Takeaways

- A TLS 1.2 handshake involves 4 messages (ClientHello, ServerHello, key exchange, Finished) before any application data flows, adding 2 round-trips of latency.
- The cipher suite negotiation determines the entire security profile: key exchange algorithm, bulk encryption cipher, and MAC algorithm are all selected in one decision.
- The pre-master secret is encrypted with the server's RSA public key, meaning the server's private key can decrypt all past sessions (no forward secrecy) unless ephemeral Diffie-Hellman is used.
- Every byte in the handshake has a purpose. Understanding the protocol at this level makes debugging TLS failures (certificate errors, cipher mismatches, version conflicts) straightforward instead of mysterious.

## Context

This page takes the approach of showing the actual bytes exchanged during a TLS connection, making an otherwise opaque protocol completely transparent. It's become a standard reference for anyone needing to understand TLS at the implementation level rather than just the conceptual level.

---

The Illustrated TLS Connection: Every Byte Explained
QUIC
DTLS
TLS 1.3
TLS 1.2
The Illustrated TLS 1.2 Connection
Every byte explained and reproduced
In this demonstration a client connects to a server,
    negotiates a TLS 1.2 session, sends "ping", receives "pong",
    and then terminates the session. Click below to begin
    exploring.
Open All
Client Hello
The session begins with the client saying "Hello".
    The client provides the following:
protocol version
client random data (used later in the handshake)
an optional session id to resume
a list of cipher suites
a list of compression methods
a list of extensions
Record Header
16 03 01 00 a5
TLS sessions are broken into the sending
            and receiving of "records", which are blocks
            of data with a type, a protocol version,
            and a length.
16
- type is 0x16 (handshake record)
03 01
- protocol version is 3.1 (also known as TLS 1.0)
00 a5
- 0xA5 (165) bytes of handshake message follows
Interestingly the version is 3.1 (TLS 1.0) instead
            of the expected "3,3" (TLS 1.2).  Looking through the
            golang crypto/tls library we find the following
            comment:
if vers == 0 {
    // Some TLS servers fail if the record version is
    // greater than TLS 1.0 for the initial ClientHello.
    vers = VersionTLS10
}
Handshake Header
01 00 00 a1
Each handshake message starts with a type and a length.
01
- handshake message type 0x01 (client hello)
00 00 a1
- 0xA1 (161) bytes of client hello follows
Client Version
03 03
The protocol version of "3,3" (meaning TLS 1.2) is given.
The unusual version number ("3,3" representing
            TLS 1.2) is due to TLS 1.0 being a minor
            revision of the SSL 3.0 protocol.  Therefore
            TLS 1.0 is represented by "3,1", TLS 1.1 is
            "3,2", and so on.
Client Random
00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f
The client provides 32 bytes of random data.
            In this example we've made the random data a predictable string.
The TLS 1.2 spec says that the first 4 bytes
            should be the current time in seconds-since-1970
            but this is
now recommended against
as it enables fingerprinting of hosts and servers.
Session ID
00
The client can provide the ID of a previous
            TLS session against this server which it
            is able to resume.  For this to work both
            the server and client will have remembered
            key information from the previous connection
            in memory.  Resuming a connection saves a
            lot of computation and network round-trip
            time so it is performed whenever possible.
00
- length of zero (no session id is provided)
Cipher Suites
00 20 cc a8 cc a9 c0 2f c0 30 c0 2b c0 2c c0 13 c0 09 c0 14 c0 0a 00 9c 00 9d 00 2f 00 35 c0 12
 00 0a
The client provides an ordered list of which
            cryptographic methods it will support for
            key exchange, encryption with that exchanged
            key, and message authentication.
            The list is in the order preferred by the
            client, with highest preference first.
00 20
- 0x20 (32) bytes of cipher suite data
cc a8
- assigned value for
TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
cc a9
- assigned value for
TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
c0 2f
- assigned value for
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
c0 30
- assigned value for
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
c0 2b
- assigned value for
TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
c0 2c
- assigned value for
TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
c0 13
- assigned value for
TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA
c0 09
- assigned value for
TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA
c0 14
- assigned value for
TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA
c0 0a
- assigned value for
TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA
00 9c
- assigned value for
TLS_RSA_WITH_AES_128_GCM_SHA256
00 9d
- assigned value for
TLS_RSA_WITH_AES_256_GCM_SHA384
00 2f
- assigned value for
TLS_RSA_WITH_AES_128_CBC_SHA
00 35
- assigned value for
TLS_RSA_WITH_AES_256_CBC_SHA
c0 12
- assigned value for
TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA
00 0a
- assigned value for
TLS_RSA_WITH_3DES_EDE_CBC_SHA
Compression Methods
01 00
The client provides an ordered list of which
            compression methods it will support.  This
            compression would be applied before encryption
            (as encrypted data is usually incompressible).
01
- 0x1 (1) bytes of compression methods follows
00
- assigned value for no compression
Compression has characteristics that can weaken
            the security of the encrypted data
            (see
CRIME
).
            so this feature has been removed from future TLS protocols.
Extensions Length
00 58
The client has provided a list of optional
            extensions which the server can use to
            take action or enable new features.
00 58
- the extensions will take 0x58 (88) bytes of data
Each extension will start with two bytes
            that indicate which extension it is, followed
            by a two-byte content length field, followed
            by the contents of the extension.
Extension - Server Name
00 00 00 18 00 16 00 00 13 65 78 61 6d 70 6c 65 2e 75 6c 66 68 65 69 6d 2e 6e 65 74
The client has provided the name of the
            server it is contacting, also known as SNI
            (Server Name Indication).
Without this extension a HTTPS server would
            not be able to provide service for multiple
            hostnames on a single IP address (virtual
            hosts) because it couldn't know which
            hostname's certificate to send until
            after the TLS session was negotiated and the
            HTTP request was made.
00 00
- assigned value for extension "server name"
00 18
- 0x18 (24) bytes of "server name" extension data follows
00 16
- 0x16 (22) bytes of first (and only) list entry follows
00
- list entry is type 0x00 "DNS hostname"
00 13
- 0x13 (19) bytes of hostname follows
65 78 61 ... 6e 65 74
- "example.ulfheim.net"
Extension - Status Request
00 05 00 05 01 00 00 00 00
The client provides permission for the
            server to provide OCSP information in its response.
            OCSP can be used to check whether a certificate
            has been revoked.
This form of the client sending an empty
            extension is necessary because
            it is a fatal error for the server
            to reply with an extension that the client
            did not provide first.  Therefore the client
            sends an empty form of the extension, and
            the server replies with the extension
            populated with data.
00 05
- assigned value for extension "status request"
00 05
- 0x5 (5) bytes of "status request" extension data follows
01
- assigned value for "certificate status type: OCSP"
00 00
- 0x0 (0) bytes of responderID information
00 00
- 0x0 (0) bytes of request extension information
Extension - Supported Groups
00 0a 00 0a 00 08 00 1d 00 17 00 18 00 19
The client has indicated that it supports
            elliptic curve (EC) cryptography for 4
            curves.  This extension was originally
            named "elliptic curves" but has been renamed
            "supported groups" to be generic to other
            cryptography types.
00 0a
- assigned value for extension "supported groups"
00 0a
- 0xA (10) bytes of "supported groups" extension data follows
00 08
- 0x8 (8) bytes of data are in the curves list
00 1d
- assigned value for the curve "x25519"
00 17
- assigned value for the curve "secp256r1"
00 18
- assigned value for the curve "secp384r1"
00 19
- assigned value for the curve "secp521r1"
Extension - EC Point Formats
00 0b 00 02 01 00
During elliptic curve (EC) cryptography the
            client and server will exchange information
            on the points selected, in either compressed
            or uncompressed form.  This extension
            indicates that the client can only parse
            uncompressed information from the server.
In the next version of TLS the ability to
            negotiate points does not exist (instead a
            single point is pre-selected for each curve),
            so this extension would not be sent.
00 0b
- assigned value for extension "EC points format"
00 02
- 0x2 (2) bytes of "EC points format" extension data follows
01
- 0x1 (1) bytes of data are in the supported formats list
00
- assigned value for uncompressed form
Extension - Signature Algorithms
00 0d 00 12 00 10 04 01 04 03 05 01 05 03 06 01 06 03 02 01 02 03
As TLS has developed it has become necessary to
            support stronger signature algorithms such
            as SHA-256 while still supporting earlier
            implementations that used MD5 and SHA1.
            This extension indicates which signature
            algorithms the client is capable of
            understanding and may influence the choice
            of certificate that the server sends to the
            client.
00 0d
- assigned value for extension "Signature Algorithms"
00 12
- 0x12 (18) bytes of "Signature Algorithms" extension data follows
00 10
- 0x10 (16) bytes of data are in the following list of algorithms
04 01
- assigned value for RSA/PKCS1/SHA256
04 03
- assigned value for ECDSA/SECP256r1/SHA256
05 01
- assigned value for RSA/PKCS1/SHA384
05 03
- assigned value for ECDSA/SECP384r1/SHA384
06 01
- assigned value for RSA/PKCS1/SHA512
06 03
- assigned value for ECDSA/SECP521r1/SHA512
02 01
- assigned value for RSA/PKCS1/SHA1
02 03
- assigned value for ECDSA/SHA1
Extension - Renegotiation Info
ff 01 00 01 00
The presence of this extension prevents
a type of attack
performed with TLS renegotiation.
The ability to renegotiate a connection has been removed from the next version of this
            protocol (TLS 1.3) so this extension will no longer be necessary in the future.
ff 01
- assigned value for extension "Renegotiation Info"
00 01
- 0x1 (1) bytes of "Renegotiation Info" extension data follows
00
- length of renegotiation data is zero, because this is a new connection
Extension - SCT
00 12 00 00
The client provides permission for the
            server to return a signed certificate
            timestamp.
This form of the client sending an empty
            extension is necessary because
            it is a fatal error for the server
            to reply with an extension that the client
            did not provide first.  Therefore the client
            sends an empty form of the extension, and
            the server replies with the extension
            populated with data, or changes behavior
            based on the client having sent the
            extension.
00 12
- assigned value for extension "signed certificate timestamp"
00 00
- 0x0 (0) bytes of "signed certificate timestamp" extension data follows
Server Hello
The server says "Hello" back.  The server provides the following:
the selected protocol version
server random data (used later in the handshake)
the session id
the selected cipher suite
the selected compression method
a list of extensions
Record Header
16 03 03 00 31
TLS sessions are broken into the sending
            and receiving of "records", which are blocks
            of data with a type, a protocol version,
            and a length.
16
- type is 0x16 (handshake record)
03 03
- protocol version is "3,3" (TLS 1.2)
00 31
- 0x31 (49) bytes of handshake message follows
Handshake Header
02 00 00 2d
Each handshake message starts with a type and a length.
02
- handshake message type 0x02 (server hello)
00 00 2d
- 0x2D (45) bytes of server hello data follows
Server Version
03 03
The protocol version of "3,3" (TLS 1.2) is given.
The unusual version number ("3,3" representing
            TLS 1.2) is due to TLS 1.0 being a minor
            revision of the SSL 3.0 protocol.  Therefore
            TLS 1.0 is represented by "3,1", TLS 1.1 is
            "3,2", and so on.
Server Random
70 71 72 73 74 75 76 77 78 79 7a 7b 7c 7d 7e 7f 80 81 82 83 84 85 86 87 88 89 8a 8b 8c 8d 8e 8f
The server provides 32 bytes of random data.
            In this example we've made the random data a predictable string.
The TLS 1.2 spec says that the first 4 bytes
            should be the current time in seconds-since-1970
            but this is
now recommended against
as it enables fingerprinting of hosts and servers.
Session ID
00
The server can provide an ID for this session
            which a client can provide on a later session
            negotiation in an attempt to re-use the key
            data and skip most of the TLS negotiation
            process.  For this to work both the server
            and client will store key information from
            the previous connection in memory.  Resuming
            a connection saves a lot of computation and
            network round-trip time so it is performed
            whenever possible.
00
- length of zero (no session id is used)
Cipher Suite
c0 13
The server has selected cipher suite 0xC013
            (TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA) from the
            list of options given by the client.
Compression Method
00
The server has selected compression method
            0x00 ("Null", which performs no compression)
            from the list of options given by the client.
Extensions Length
00 05
The server has returned a list of extensions
            to the client.  Because the server is
            forbidden from replying with an extension
            that the client did not send in its hello
            message, the server knows that the client
            will support all extensions listed.
00 05
- the extensions will take 0x5 (5) bytes of data
Extension - Renegotiation Info
ff 01 00 01 00
The presence of this extension prevents
a type of attack
performed with TLS renegotiation.
The ability to renegotiate a connection has been removed from the next version of this
            protocol (TLS 1.3) so this extension will no longer be necessary in the future.
ff 01
- assigned value for extension "Renegotiation Info"
00 01
- 0x1 (1) bytes of "Renegotiation Info" extension data follows
00
- length of renegotiation data is zero, because this is a new connection
Server Certificate
The server provides a certificate containing the following:
the hostname of the server
the public key used by this server
proof from a trusted third party that the owner of this hostname holds the private key for this public key
Explore the server certificate
.
Record Header
16 03 03 03 2f
TLS sessions are broken into the sending
            and receiving of "records", which are blocks
            of data with a type, a protocol version,
            and a length.
16
- type is 0x16 (handshake record)
03 03
- protocol version is "3,3" (TLS 1.2)
03 2f
- 0x32F (815) bytes of handshake message follows
Handshake Header
0b 00 03 2b
Each handshake message starts with a type and a length.
0b
- handshake message type 