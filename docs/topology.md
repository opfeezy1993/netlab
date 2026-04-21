# Lab topology

Filled in once the 16U rack arrives and physical layout is finalized.

## Planned sections

- Rack elevation — what sits in which U
- Logical L2 topology — VLANs, trunks, spanning-tree root
- Logical L3 topology — OSPF areas, point-to-point links, route summary
- Cable schedule — every cable end-to-end, with color code
- Power plan — which PDU outlet feeds which device, UPS runtime estimate

## Cable color convention

- Blue: access / host
- Yellow: trunk (switch-to-switch)
- Green: management
- Red: WAN / uplink to the outside

## Starting topology (to be validated)

```
            r1 ---- r2 ---- r3
            |       |       |
            |       |       |
           sw1 --- sw2 --- sw3
```

- r1/r2/r3: full-mesh WAN-style L3 links, OSPF area 0
- sw1/sw2/sw3: triangle L2, one spanning-tree root (sw2), VLANs 10/20/30/99
- Each router has one LAN interface to its local switch
