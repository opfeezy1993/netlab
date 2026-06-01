# Lab Cable Map

Every cable, every port, every purpose. This document is the source-of-truth
for the physical layer. If a cable comes out of the rack, this tells you
where it goes back.

## Color discipline

| Color  | Purpose                              | Cable count |
|--------|--------------------------------------|-------------|
| Red    | WAN / external uplinks               | 2           |
| Yellow | Inter-device trunks and L3 uplinks   | 5           |
| Green  | Management (mgmt VRF, mgmt VLAN)     | 3           |
| Gray   | Console (USB-to-RJ45, as needed)     | 0 permanent |
| Black  | AC power (each device → PDU)         | 6           |

If you don't have colored cables on hand, use plain Cat6 and label each end
with a sticker or sharpie. Labels are mandatory; colors are nice-to-have.

## Cable inventory (10 patch cables + 6 power)

### Red: WAN path

| # | From            | Port      | To              | Port    | Length | Notes |
|---|-----------------|-----------|-----------------|---------|--------|-------|
| 1 | Wall jack       | (RJ-45)   | Slate AX        | WAN     | 50 ft  | Building uplink — long run through wall |
| 2 | Slate AX        | LAN 1     | R-EDGE          | G0/0/0  | 2 ft   | Slate AX hands public/NAT'd address to R-EDGE |

### Yellow: Routing backbone and switch trunks

| # | From            | Port      | To              | Port      | Length | Notes |
|---|-----------------|-----------|-----------------|-----------|--------|-------|
| 3 | R-EDGE          | G0/0/1    | R-CORE          | G0/0/0    | 1 ft   | P2P /30 link, OSPF area 0 backbone |
| 4 | R-CORE          | G0/0/1    | SW-CORE         | Gi1/0/1   | 1 ft   | L3 router-to-switch uplink (no switchport, routed interface) |
| 5 | SW-CORE         | Gi1/0/24  | SW-L3-LAB       | Gi0/1     | 2 ft   | 802.1Q trunk, all VLANs |
| 6 | SW-CORE         | Gi1/0/23  | SW-ACC-1        | Gi0/1     | 2 ft   | 802.1Q trunk, all VLANs |
| 7 | SW-CORE         | Gi1/0/22  | SW-ACC-LAB      | Gi0/1     | 2 ft   | 802.1Q trunk, all VLANs |

### Green: Management plane

| # | From            | Port      | To              | Port      | Length | Notes |
|---|-----------------|-----------|-----------------|-----------|--------|-------|
| 8 | R-EDGE          | Gi0 (mgmt)| SW-CORE         | Gi1/0/48  | 1 ft   | Dedicated out-of-band mgmt port; Cisco uses Gi0 for mgmt VRF |
| 9 | R-CORE          | Gi0 (mgmt)| SW-CORE         | Gi1/0/47  | 1 ft   | Same as above |
|10 | Pi 5            | eth0      | SW-CORE         | Gi1/0/2   | 3 ft   | Pi reaches the shelf; cable runs down |

Switches (SW-L3-LAB, SW-ACC-1, SW-ACC-LAB) do NOT need a dedicated
management cable — their management traffic rides the trunk on VLAN 99 (the
management VLAN). The SVI `interface Vlan99` carries their IP.

### Black: Power

| # | Device          | Outlet | Notes |
|---|-----------------|--------|-------|
|P1 | R-EDGE          | PDU 1  | C13 → C14, ~3 ft cord |
|P2 | R-CORE          | PDU 2  | C13 → C14 |
|P3 | SW-CORE         | PDU 3  | C13 → C14 |
|P4 | SW-L3-LAB       | PDU 4  | C13 → C14 |
|P5 | SW-ACC-1        | PDU 5  | C13 → C14 |
|P6 | SW-ACC-LAB      | PDU 6  | C13 → C14 |

Pi 5 powered separately via USB-C from a wall wart (not the PDU). The Slate
AX uses its own DC barrel-jack adapter.

## Port assignments on SW-CORE (3560X-24P, 24 ports + 4 SFP)

| Port      | Role                               | VLAN config              |
|-----------|------------------------------------|--------------------------|
| Gi1/0/1   | Uplink to R-CORE                   | `no switchport` (L3 routed) |
| Gi1/0/2   | Pi management                      | access, VLAN 99          |
| Gi1/0/3-21| Reserved / future endpoints        | (unassigned for now)     |
| Gi1/0/22  | Trunk to SW-ACC-LAB                | trunk, allow 10,20,30,99 |
| Gi1/0/23  | Trunk to SW-ACC-1                  | trunk, allow 10,20,30,99 |
| Gi1/0/24  | Trunk to SW-L3-LAB                 | trunk, allow 10,20,30,99 |
| Gi1/0/47  | R-CORE management                  | access, VLAN 99          |
| Gi1/0/48  | R-EDGE management                  | access, VLAN 99          |
| SFP 1-4   | Reserved for future fiber uplinks  | (unused)                 |

## Bring-up order

Wire the cables in this order. Do not power-on devices until all cables
are seated.

1. **Power cords first.** Plug every device's IEC C13 cable into the PDU,
   but **keep the PDU master switch OFF**. This lets you wire cleanly
   without anything booting.
2. **Management cables (green).** R-EDGE mgmt → SW-CORE Gi1/0/48,
   R-CORE mgmt → SW-CORE Gi1/0/47, Pi → SW-CORE Gi1/0/2.
3. **Inter-switch trunks (yellow).** SW-CORE → each access switch on
   Gi1/0/22, 23, 24.
4. **Router backbone (yellow).** R-EDGE G0/0/1 → R-CORE G0/0/0.
5. **R-CORE → SW-CORE uplink (yellow).** G0/0/1 → Gi1/0/1.
6. **WAN (red).** Slate AX → R-EDGE G0/0/0. Wall jack → Slate AX WAN
   (the 50 ft cable).
7. **Power on:** flip PDU master switch.
8. **Devices boot.** SW-CORE first (it carries everything). Then routers.
   Then access switches. Then the Pi.

Order matters because:
- If a switch is unpowered when its uplink switch boots, the trunk forms
  later but with a delayed convergence — STP recalculates.
- If a router boots before its downstream switch is up, OSPF neighbors
  form when the link comes up; not a problem.
- Powering everything on simultaneously is fine too, but staggering
  reduces inrush current on the PDU and is gentler on aging gear.

## Where each VLAN lives (preview)

| VLAN | Name        | Subnet             | Gateway       |
|------|-------------|--------------------|---------------|
| 10   | USERS       | 10.10.10.0/24      | 10.10.10.1 on SW-CORE SVI |
| 20   | SERVERS     | 10.10.20.0/24      | 10.10.20.1 on SW-CORE SVI |
| 30   | VOICE       | 10.10.30.0/24      | 10.10.30.1 on SW-CORE SVI |
| 99   | MGMT        | 192.168.100.0/24   | 192.168.100.1 on SW-CORE SVI (also default gw for Pi) |
| 999  | NATIVE-UNUSED | unrouted         | (security best practice — no traffic should ride native) |

VLANs 10/20/30/99 are created on every switch. SW-CORE has the SVIs (the
L3 interfaces) for each. Access switches just forward Layer-2 frames.

## Verification after cabling

After power-on, the link lights tell you the cabling story:

- **Green LED on the port** → physical layer up. Cable is good, far-end
  device is detecting your signal.
- **Amber LED** → port in STP listening/learning state (normal for ~30 sec
  after a switch boots, then green).
- **Green blinking** → traffic flowing. Good.
- **No light** → cable bad, far-end device powered off, or port shut down
  on either side.

If a port shows no light, suspect (in order):
1. Far-end device not powered on.
2. Cable not seated fully on either end (push until you hear the click).
3. Cable bad — swap it.
4. Port administratively shut down — `show interface` on the device.

## Related lessons

- Lesson 11: Color-coded cabling and labeling discipline (planned)
- Lesson 10: The three-tier network architecture (planned)
