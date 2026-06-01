# Lesson 04: Tailscale and zero-config mesh VPN

The Raspberry Pi sits on a home network behind a residential router with a
private IP — `192.168.8.215`. From anywhere outside that home network, that
IP is unreachable. So how do we SSH into the Pi from a coffee shop, an
airport, or a friend's house?

The traditional answer is "port forwarding" — open a hole in the home router
that maps an external port to the Pi. This is dangerous. Within hours,
automated scanners would find the open port and begin attacking it.

Instead, we installed **Tailscale**, a modern mesh VPN built on WireGuard
that requires no open ports, no firewall configuration, and almost no setup.
The Pi is now reachable from anywhere — including the Mac — via the IP
`100.80.77.106`, which only exists inside the Tailscale network. Nothing on
the public internet can see it.

## What we did

On both the Pi and the Mac:

```
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Each device received a Tailscale-assigned IP in the `100.x.y.z` range. Both
devices are now members of the same private mesh network — even though the
Pi is behind one NAT and the Mac is sometimes behind another (and they may
be on different continents).

Now from anywhere on the Mac:

```
ssh timioyewole@100.80.77.106
```

This works whether the Mac is at home, in another city, or on a plane.

## Why it exists

Three problems Tailscale solves:

1. **NAT traversal.** Most consumer internet connections give you a single
   public IP that's shared among everyone in your home. Inbound connections
   to a specific device require port forwarding or a static IP — both of
   which are increasingly rare and increasingly attacked.

2. **Exposing services to the internet is dangerous.** Even with strong
   authentication, every open port is a target. Brute-force noise,
   zero-day exploits, and credential stuffing constantly hammer any
   service that listens on a public IP. The safest service is one that
   doesn't exist on the public internet at all.

3. **Traditional VPNs are operationally painful.** Setting up OpenVPN or
   IPSec means generating certificates, configuring routing, managing user
   accounts, opening firewall ports — and getting any of it wrong creates
   security holes. The complexity actively pushes people toward less
   secure options.

Tailscale wraps WireGuard (the modern VPN protocol) in a coordination
service that handles all of the painful parts automatically.

## How it works under the hood

There are two parts to Tailscale: the **data plane** (where your traffic
flows) and the **control plane** (which tells devices about each other).

**Data plane: WireGuard, peer-to-peer.**

When the Pi and the Mac want to communicate:

```
Mac ──── encrypted WireGuard tunnel ────► Pi
```

This tunnel uses **state-of-the-art cryptography** (Curve25519, ChaCha20,
Poly1305). It's the same family of primitives behind Signal Messenger and
TLS 1.3. Every packet is authenticated and encrypted. An attacker watching
the wire sees only encrypted noise.

The clever bit: **the tunnel is direct, not through Tailscale's servers.**
Once the Mac knows the Pi's current address, packets flow directly. This
is "peer-to-peer" mesh, not "hub-and-spoke" VPN. Your data doesn't pass
through Tailscale's infrastructure.

**Control plane: the coordination server.**

For peer-to-peer to work, each device needs to know:
- Which other devices are in my network?
- What's their current public-internet address?
- What's their public key for the encrypted tunnel?

This is what Tailscale's **coordination server** does. When a device joins
the network, it tells the coordination server "here I am, here's my public
key, here's my external address." The server distributes this information
to other devices. The devices then establish direct WireGuard tunnels.

**NAT traversal: how the Pi behind a home router becomes reachable.**

This is where it gets clever. Both the Pi (home network) and the Mac
(possibly on a hotel WiFi) are behind NAT. Neither has a directly-routable
public IP. Tailscale solves this with:

1. **STUN.** Both devices contact a Tailscale server to discover their own
   public-facing address as seen from the internet.
2. **Hole punching.** Both devices simultaneously send packets to each
   other's public address. Their NAT routers see outgoing connections and
   open temporary holes for the reply. The packets cross. The tunnel is
   established.
3. **DERP relay (fallback).** If NAT is too strict (some corporate
   networks), traffic falls back to encrypted relay through Tailscale's
   DERP servers. Slower, but it still works. The encryption is end-to-end —
   even Tailscale can't decrypt it.

**Identity: Google OAuth, GitHub OAuth, etc.**

Tailscale doesn't have its own user accounts. You authenticate with an
existing identity provider (Google, GitHub, Microsoft, Okta). Whoever owns
the email/account owns the Tailscale "tailnet." Devices join the tailnet
by completing the same OAuth flow. This means:

- No password to lose or leak.
- 2FA on your Google account = 2FA on your Tailscale.
- Tailscale never sees your password.

**MagicDNS: human-friendly hostnames.**

Tailscale assigns each device a hostname (e.g., `raspberrypi.tail-scale.ts.net`)
that resolves from any other device on the tailnet. So you can `ssh
timioyewole@raspberrypi` instead of memorizing IP addresses.

## Alternatives

- **Port forwarding + dynamic DNS.** Old-school. Open the SSH port on your
  router, register a DuckDNS or No-IP hostname, hope for the best. The
  attacks start within minutes.
- **OpenVPN.** Traditional VPN. Mature, secure, supported everywhere — but
  setup is genuinely painful, certificate management is a hassle, and
  performance is lower than WireGuard.
- **WireGuard, self-hosted.** Same protocol Tailscale uses, but you
  configure it yourself. Each device needs every other device's public
  key. Routing requires manual setup. Doable, but the coordination problem
  is exactly what Tailscale automated away.
- **ZeroTier.** Tailscale's older competitor. Same basic idea, different
  implementation (uses its own protocol rather than WireGuard). Also
  excellent; either works.
- **Headscale.** A self-hosted open-source implementation of Tailscale's
  coordination server. For users who don't want to depend on Tailscale Inc.

Why Tailscale specifically for this lab:
- **Free for personal use** up to 100 devices and 3 users.
- **Zero-config NAT traversal.** Just works behind any consumer router.
- **Mature.** Funded company, active development, used by serious shops
  including some at AWS.
- **WireGuard-based.** The actual cryptography is well-reviewed.

## Security implications

Tailscale's threat model is:

- **Trust the coordination server with metadata** (who's online, what
  addresses they have, public keys). Not the actual traffic — that's
  end-to-end encrypted between peers.
- **Trust the identity provider** (Google, GitHub) for authentication.
- **Don't trust the network in between** — encryption assumes adversaries
  on the wire.

Practical implications for the lab:

- The Pi is **not exposed to the public internet at all.** SSH on port 22
  is closed to anything but the Tailscale network.
- An attacker would need to compromise your Google account (2FA-protected)
  AND get a device authenticated to your tailnet to reach the Pi.
- Even Tailscale Inc. cannot decrypt the SSH traffic between Mac and Pi.

Defense-in-depth additions we layered on top:
- **SSH key authentication** (Lesson 02) — even if someone breached
  Tailscale, they'd still need the private key.
- **fail2ban** — locks out repeated auth failures inside the LAN segment
  too.
- **unattended-upgrades** — auto-patches the SSH daemon and Tailscale
  itself.

## Interview answer

> "Tailscale is a mesh VPN built on WireGuard that requires no open
> firewall ports. Each device authenticates to a Tailscale-managed
> coordination server using OAuth — Google, GitHub, etc. — and the
> coordination server tells devices about each other. Once they know each
> other, they establish direct peer-to-peer encrypted tunnels using
> WireGuard. NAT traversal is automatic via STUN-style hole punching;
> direct connections aren't possible (very strict NAT or corporate
> environments) traffic falls back to encrypted relays. The benefits
> versus traditional VPN are: no inbound ports to attack, no certificate
> management, automatic peer discovery, and identity is delegated to an
> existing IdP. In my lab, the Raspberry Pi is reachable from any of my
> devices via Tailscale IP, with the SSH port completely closed to the
> public internet. The threat model assumes peer-to-peer traffic is
> end-to-end encrypted with WireGuard primitives — Tailscale themselves
> cannot decrypt it, only see metadata."

## See also

- Lesson 02: SSH key-based authentication (used in tandem)
- Lesson 07: fail2ban (defense-in-depth on the Pi side)
