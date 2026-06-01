# Lesson 02: SSH key-based authentication

When the Raspberry Pi was first set up, it had a username and a password.
Anyone who could reach port 22 (the SSH port) over the network could try to
guess that password forever. Within hours of going online, automated bots
began doing exactly that.

We replaced password authentication with **SSH key authentication** —
mathematically impossible to brute-force, immune to password leaks, and the
foundation for every secure remote access workflow used in production
infrastructure today.

## What we did

On the Mac:

```
ssh-keygen -t ed25519
```

This generated a **key pair** — two cryptographically linked files:
- `~/.ssh/id_ed25519` — the **private key**. Stays on the Mac. Never leaves.
- `~/.ssh/id_ed25519.pub` — the **public key**. Safe to share anywhere.

Then we copied the public key to the Pi:

```
ssh-copy-id timioyewole@raspberrypi.local
```

This appended the public key to `~/.ssh/authorized_keys` on the Pi. From
that moment, the Pi recognized the Mac's key as trusted.

Then we hardened the Pi's SSH daemon:

```
sudo nano /etc/ssh/sshd_config
# Changed:
PasswordAuthentication no
sudo systemctl restart ssh
```

Password authentication is now completely disabled on the Pi. Even the
correct password wouldn't get you in. Only a device holding the matching
private key can authenticate.

## Why it exists

Passwords have three fatal weaknesses:

1. **Brute-forceability.** A six-character password can be exhaustively
   tried in seconds with modern hardware. Even strong passwords succumb to
   dictionary attacks, credential stuffing, and rainbow tables.
2. **Replayability.** If a password is intercepted (man-in-the-middle on a
   compromised network, keylogger on an infected machine, phishing), the
   attacker can use it to log in indefinitely.
3. **Reusability across systems.** Humans reuse passwords. One breach can
   compromise many accounts.

SSH keys solve all three:

1. **Brute-force is infeasible.** Ed25519 keys have ~256 bits of effective
   security. Even with every computer on Earth running until heat-death of
   the universe, you couldn't guess one.
2. **The private key never leaves the client machine.** The actual
   authentication uses a challenge-response protocol — the server sends a
   random challenge, the client signs it with the private key, the server
   verifies the signature with the public key. No secret material crosses
   the wire.
3. **Per-device keys** mean a single compromise affects only one machine.
   Lose your laptop? Revoke its public key from every server. Done.

For automated systems (like the Ansible playbooks that will run from your
Pi), keys are the *only* practical authentication method — you can't have
a human typing a password every time a script wants to log into a router.

## How it works under the hood

Ed25519 (and RSA, the older standard) are based on **asymmetric
cryptography**. Two mathematically linked keys are generated together. The
key insight: given the public key, computing the matching private key is
computationally infeasible — even though they were generated as a pair.

For Ed25519 specifically, the math is based on **elliptic curve
cryptography** — specifically, the Curve25519 elliptic curve, designed by
Daniel J. Bernstein for fast, side-channel-resistant signing. (RSA uses
integer factorization, which is older, slower, and requires much larger
key sizes for equivalent security.)

The SSH handshake when you connect:

```
1. Client (Mac):  "I want to authenticate as timioyewole using key X."
2. Server (Pi):   Looks up X in ~timioyewole/.ssh/authorized_keys.
                  Generates a random challenge (e.g., a 256-byte nonce).
                  Encrypts the challenge with public key X.
3. Server (Pi):   "Here's an encrypted challenge. Decrypt it and sign it."
4. Client (Mac):  Uses private key to decrypt the challenge.
                  Signs it with the private key.
                  Sends signature back.
5. Server (Pi):   Verifies signature using public key X.
                  If valid: grants session.
                  If invalid: rejects.
```

Critically: **the private key never crosses the wire.** It only ever proves
its own existence by producing valid signatures that the public key can
verify.

The public key in `~/.ssh/authorized_keys` looks like:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILxxxxxxxxxxxxxxx user@hostname
```

The middle blob is the actual base64-encoded public key material. The comment
on the end is just a human label.

## Alternatives

- **Passwords alone.** What we replaced. Not viable for production.
- **Passwords + 2FA (TOTP, U2F).** A defensible approach for human-facing
  shells. Doesn't work for automation.
- **Kerberos / GSSAPI.** Enterprise single-sign-on. Common in large
  organizations with Active Directory. More complex to set up; great when
  you have it.
- **Certificate-based SSH.** Like keys, but each public key is signed by a
  certificate authority (CA), and the CA controls who is trusted. Used at
  scale (Facebook, Netflix, Uber publicized their implementations). The
  next-level pattern after raw keys.
- **Hardware tokens (YubiKey).** Private key lives on a USB device that
  must be physically present. Even if your laptop is stolen, the attacker
  can't authenticate without the token.

Why Ed25519 over RSA:
- **Faster.** Ed25519 signing is ~10x faster than RSA-2048.
- **Smaller.** Ed25519 keys are 256 bits; RSA equivalents are 2048-3072 bits.
- **Side-channel resistant.** The math is designed to leak no timing
  information about the private key.
- **Quantum vulnerability is similar to RSA.** Both fall to a sufficiently
  large quantum computer. Post-quantum signature schemes (Dilithium,
  Falcon) are being standardized but not yet widely deployed.

## Interview answer

> "SSH key authentication replaces passwords with a public-private key pair.
> The private key stays on the client and never crosses the network; the
> public key is installed on every server you want to access. Authentication
> works by the server sending a random challenge, the client signing it with
> the private key, and the server verifying the signature with the public
> key. This is more secure than passwords because there's no shared secret
> to intercept, no entropy limit to brute-force, and revocation is granular
> — losing a laptop means revoking one public key, not changing passwords
> on every system. In my lab, I generate Ed25519 keys on the Mac, install
> the public key on every server (Pi, jump host, future automation
> controllers), and disable password authentication entirely in
> sshd_config. Ed25519 specifically because it's faster, smaller, and more
> side-channel-resistant than RSA."

## See also

- Lesson 04: Tailscale and zero-config mesh VPN (how to make SSH reachable
  without exposing port 22 to the internet)
- Lesson 07: fail2ban (defense-in-depth — even with keys, you want to block
  the brute-force noise)
