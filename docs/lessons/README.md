# Lab Lessons

A growing library of deep-dive explanations for every concept used in this
lab. Each lesson follows the same five-layer structure:

1. **What we did** — the concrete action.
2. **Why it exists** — the problem it solves.
3. **How it works under the hood** — the mechanism and moving parts.
4. **Alternatives** — what other ways exist, and the trade-offs.
5. **Interview answer** — a one-paragraph elevator response for technical
   screens and stakeholder conversations.

The goal of these lessons is to turn a working lab into a teaching artifact.
Anyone reading this repo — recruiter, hiring engineer, future-me — should
walk away understanding not just *what* was built, but *why* each piece is
necessary and what the engineering trade-offs were.

## Available lessons

| # | Topic | Status |
|---|---|---|
| 01 | Config-as-code: the foundational philosophy | Written |
| 02 | SSH: from password authentication to key-based auth | Written |
| 03 | The Ansible inventory model | Written |
| 04 | Tailscale and zero-config mesh VPN | Written |
| 05 | The console port: RJ-45, FTDI chips, and baud rates | Planned |
| 06 | Jinja2 templates and idempotency | Planned |
| 07 | fail2ban: proactive defense against brute force | Planned |
| 08 | Cisco IOS evolution: legacy IOS vs IOS-XE | Planned |
| 09 | Smart Licensing, RTU, and the license tier model | Planned |
| 10 | The three-tier network architecture | Planned |
| 11 | Color-coded cabling and labeling discipline | Planned |
| 12 | PoE: Power over Ethernet standards and use cases | Planned |
| 13 | Day 0 / Day 1 / Day 2 operations framework | Planned |
| 14 | NETCONF, RESTCONF, and YANG vs CLI automation | Planned |
| 15 | OSPF: multi-area design and ABR selection | Planned |

## How to use this folder

These lessons supplement the operational documentation in `docs/`. Read them
in the order written — each builds on prior lessons.

A topic moves from "Planned" to "Written" when its corresponding numbered
file appears in this directory. Pull requests adding new lessons are welcome.
