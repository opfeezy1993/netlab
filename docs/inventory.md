# Lab Inventory

Asset register for the home networking lab. One entry per device with model,
serial number, IOS version, license tier, and health snapshot captured at
initial bring-up. Source data is the `show inventory`, `show version`,
`show post`, and `show env all` output from each device's console.

This document is built device-by-device during the rack-day process. Devices
with `TBD` fields are pending console capture.

## Summary

| Role         | Hostname  | Model            | Serial       | IOS / IOS-XE        | License                      | Status   |
|--------------|-----------|------------------|--------------|---------------------|------------------------------|----------|
| R-EDGE       | r1        | ISR 4331         | FLM2151V106  | IOS-XE 16.6.6       | Foundation + AppX + Sec + IPB | Healthy  |
| R-CORE       | r2        | ISR 4331         | FLM2151V015  | IOS-XE 16.6.6       | Foundation + AppX + Sec + IPB | Healthy  |
| SW-CORE      | sw1       | Catalyst 3560X-24P | FDO1642R28V | IOS 15.2(4)E6       | LAN Base (RTU upgrade plan)  | Healthy  |
| SW-ACC-LAB   | sw3       | Catalyst 2960-24TT-L | FOC1248V4DM | IOS 15.0(1)SE1   | LAN Base                     | Healthy  |
| SW-ACC-1     | sw-acc-1  | Catalyst 2960-48TC-L | FOC1404Y3LP | IOS 12.2(44)SE6 | LAN Base                     | Healthy  |
| SW-L3-LAB    | sw-l3-lab | Catalyst 3550-24PWR-SMI | CHK0707V01L | IOS 12.2(44)SE6 | IP Services (PoE)        | Healthy  |

---

## R-EDGE — Cisco ISR 4331 (router 1)

- **Role:** WAN edge router — internet termination, NAT, optional zone-based firewall.
- **Chassis PID:** ISR4331/K9 (Integrated Services Router 4331, crypto-enabled).
- **Serial:** FLM2151V106
- **IOS:** IOS-XE 16.6.6 "Everest", UNIVERSALK9 image.
- **License tier:** Foundation Suite K9, AppX K9, Security K9, IP Base K9 — all Permanent, Active, In Use.
- **Power supply:** PWR-4330-AC, 250W AC (SN: DCA214B153N).
- **Fan tray:** ACS-4330-FANASSY.
- **Front-panel interfaces:** 3× Gigabit Ethernet (NIM subslot 0/0, PID ISR4331-3x1GE) — G0/0/0, G0/0/1, G0/0/2.
- **Installed transceiver:** Avago ABCU-5710RZ-CS4 "GE T" (1000BASE-T copper SFP, SN: AGM1743211U).
- **Service Module slot (module 1):** Empty.
- **Route Processor SN:** FD021470NHC.
- **POST / health:** All self-tests passed at acquisition.
- **Configuration register:** 0x2102 (normal boot).
- **Acquired:** May 2026 (eBay).
- **Notes:** Fully unlocked feature set — supports OSPF/EIGRP/BGP, IPsec, ZBFW, AppX features. Modern IOS-XE platform with NETCONF/RESTCONF/YANG support; primary automation target for the `cisco.ios` Ansible collection and Netmiko.

## R-CORE — Cisco ISR 4331 (router 2)

- **Role:** Core router — inter-VLAN routing, OSPF lab, automation target.
- **Chassis PID:** ISR4331/K9.
- **Serial:** FLM2151V015
- **IOS:** IOS-XE 16.6.6 "Everest", UNIVERSALK9 image.
- **License tier:** Foundation Suite K9, AppX K9, Security K9, IP Base K9 — all Permanent, Active, In Use.
- **Power supply:** PWR-4330-AC, 250W AC (SN: DCA214B1652).
- **Fan tray:** ACS-4330-FANASSY.
- **Front-panel interfaces:** 3× Gigabit Ethernet (NIM subslot 0/0, PID ISR4331-3x1GE).
- **Installed transceiver:** Avago ABCU-5710RZ-CS4 "GE T" (1000BASE-T copper SFP, SN: AGM17432162).
- **Service Module slot (module 1):** Empty.
- **Route Processor SN:** FD021470PFS.
- **POST / health:** All self-tests passed at acquisition.
- **Configuration register:** 0x2102 (normal boot).
- **Acquired:** May 2026 (eBay).
- **Notes:** Identical hardware to R-EDGE. Paired with R-EDGE for OSPF area 0 lab work and as a redundant automation target.

## SW-CORE — Catalyst 3560X-24P

- **Role:** Layer-3 distribution switch — inter-VLAN routing, PoE+ endpoint power, automation target.
- **Chassis PID:** WS-C3560X-24P-L (24-port Gigabit, PoE+, LAN Base license shipped).
- **Serial:** FDO1642R28V
- **Base MAC address:** AC:F2:C5:20:95:80
- **IOS:** 15.2(4)E6, C3560E-UNIVERSALK9-M image (universal binary — feature set gated by license).
- **License tier:** LAN Base, Permanent (next-reload also LAN Base). **Lab plan:** promote to IP Services via `license boot level ipservices` (Right-to-Use, lab-only) to unlock OSPF/EIGRP and full L3 routing.
- **Processor / memory:** PowerPC405 with 256 MB DRAM, 512 KB flash NVRAM.
- **Hardware:** Motherboard SN FDO16420BZN (P/N 73-12555-08), daughterboard SN FDO162923GT (P/N 800-32786-02), Top Assembly P/N 800-31329-07, CLEI Code COMJS00ARD, hardware board revision 0x04.
- **Interface count (per `show version`):** 1× FastEthernet (management), 28× Gigabit Ethernet (24 access ports + 4 SFP uplinks via C3KX-NM-1G), 2× Ten Gigabit Ethernet slots (chassis-reported; populated only if a C3KX-NM-10G module is installed).
- **Password recovery:** Enabled.
- **Power supply:** C3KX-PWR-350WAC, 350W AC, modular (SN: LIT182610T3).
- **Uplink module:** C3KX-NM-1G — 4× SFP slots at 1 Gbps (SN: FDO16371DG4).
- **PoE:** PoE+, up to 30W per port (24 ports).
- **POST / health:** All self-tests passed (CPU MIC, MA BIST, TCAM BIST, SF ASIC BIST, Switch Fabric Memory, CPU MIC interface, PortASIC ring/port loopback, Inline Power Controller, Thermal/Fan, PortASIC Macsec loopback, EMAC loopback).
- **Environment (live):** Chassis FAN 1 and FAN 2 OK, PSU FAN PS-1 OK, FAN PS-2 not present (single-PSU configuration). System temperature 20°C, GREEN state (yellow threshold 46°C, red threshold 60°C). RPS: not present.
- **Configuration register:** 0xF.
- **Acquired:** May 2026 (eBay).
- **Notes:** 24 PoE+ ports allow direct power for IP phones, wireless APs, and PoE-HAT-equipped Raspberry Pis without separate power supplies. Universal image plus RTU promotion makes this a full L3 distribution switch for the lab topology.

## SW-ACC-LAB — Catalyst 2960-24TT-L

- **Role:** Sandbox access switch — for breaking-things experimentation kept off the production path.
- **Chassis PID:** WS-C2960-24TT-L.
- **Serial:** FOC1248V4DM
- **Base MAC address:** 00:24:50:46:A6:80
- **IOS:** 15.0(1)SE1, C2960-LANBASEK9-M image.
- **License tier:** LAN Base (pure Layer 2; no L3 routing protocols supported).
- **Processor:** PowerPC405 with 64 MB DRAM, 64 KB flash NVRAM.
- **Interfaces:** 24× FastEthernet (10/100), 2× Gigabit Ethernet uplinks, 1× Virtual Ethernet.
- **Motherboard SN:** FOC1248374J.
- **Power supply SN:** DCA124286N6 (P/N 341-0097-02).
- **POST / health:** All self-tests passed (CPU MIC, PortASIC memory and CAM, ring/port loopback). `show env all` to be verified.
- **Configuration register:** 0xF.
- **Password recovery:** Enabled.
- **Acquired:** May 2026 (eBay).
- **Notes:** Slower than the 2960S/X (FastEthernet access ports, gigabit only on the two uplinks). Designated as the sandbox where templates and playbooks can be tested destructively without affecting the production path.

---

## Pending devices

The five devices below are existing lab gear acquired before the eBay purchase
and have not yet been consoled for inventory capture. Entries will be filled in
as each device is bench-tested.

## SW-ACC-1 — Catalyst 2960-48TC-L

- **Role:** Primary access switch — endpoint connectivity for end users and devices.
- **Chassis PID:** WS-C2960-48TC-L (48-port FastEthernet, 2× Gigabit uplinks, LAN Base).
- **Serial:** FOC1404Y3LP
- **Base MAC address:** 30:37:A6:37:AE:80
- **IOS:** 12.2(44)SE6, C2960-LANBASEK9-M image.
- **License tier:** LAN Base (Layer 2 only).
- **Processor / memory:** PowerPC405 with 60 MB DRAM + 4 MB packet buffer, 64 KB flash NVRAM.
- **Hardware:** Motherboard SN FOC14044AY1 (P/N 73-9835-10), revision G0/B0; PSU SN AZS140201MR (P/N 341-0097-02); Top Assembly P/N 800-26672-05; CLEI Code COMFW00BRA.
- **Interfaces:** 48× FastEthernet (10/100) access ports, 2× Gigabit Ethernet uplinks, 1× Virtual Ethernet.
- **Password recovery:** Enabled.
- **Configuration register:** 0xF.
- **Device state on console connect:** "Press RETURN to get started!" prompt — indicates no saved configuration (factory state or post-wipe).
- **Status:** Healthy on boot; full POST output and `show env all` to be captured.
- **Notes:** Older IOS (12.2(44)SE6, circa 2010); upgrade to a 15.0(2)SE-series release is possible if needed. FastEthernet access ports are slower than gigabit but the 48-port density makes this a good primary endpoint switch.

## SW-L3-LAB — Catalyst 3550-24PWR-SMI

- **Role:** Legacy Layer-3 lab switch — paired with SW-CORE (3560X) to learn OSPF/EIGRP across two switch generations. Doubles as a secondary PoE access switch when needed.
- **Chassis PID:** WS-C3550-24PWR-SMI (24-port FastEthernet, PoE, 2× Gigabit uplinks, Standard Multilayer Image hardware).
- **Serial:** CHK0707V01L
- **Base MAC address:** 00:0C:30:3B:B4:80
- **IOS:** 12.2(44)SE6, **C3550-IPSERVICESK9-M** image — highest license tier for the 3550 platform. Compiled 09-Mar-2009.
- **License tier:** IP Services — full L3 feature set: OSPF, EIGRP, BGP, IS-IS, multicast (PIM/IGMP), HSRP/VRRP/GLBP, VRF-lite, policy-based routing, QoS.
- **Processor / memory:** PowerPC with 64 MB DRAM + 8 MB packet buffer, 384 KB flash NVRAM.
- **Hardware:** Motherboard SN CAT070604J7 (P/N 73-8100-09); PSU P/N 341-0029-02; revision A0.
- **Interfaces:** 24× FastEthernet (10/100, PoE-capable on all ports), 2× Gigabit Ethernet uplinks.
- **PoE:** Yes — provided by the larger 341-0029-02 power supply (PoE variant).
- **Password recovery:** Enabled.
- **Device state on console connect:** Has saved configuration from prior owner — boot log shows `%SYS-5-CONFIG_I: Configured from memory by console`, `%SSH-5-ENABLED: SSH 2.0`. Will need a `write erase` + `reload` before adding to the new topology, or selective config purge if some elements are worth keeping.
- **Status:** Healthy on boot; running and serviceable.
- **Notes:** A 3550 running IP Services is the best-case scenario for this platform — it had the largest feature gap between SMI and EMI/IP-Services tiers of any Cisco access switch generation. Pairing this with the 3560X-24P gives the lab two distinct L3 switch generations (2003 vs 2012 era) for direct comparison — a strong portfolio differentiator.

## Excluded from active fleet

### Legacy router (decommissioned)

A previously-owned legacy Cisco router was evaluated for inclusion but produces excessive fan noise unsuitable for a home environment. Decision: exclude from active lab. Legacy IOS practice will be done in **GNS3** on the Lenovo workstation instead, where the same classic IOS images can be run virtually without noise, heat, or power draw.
