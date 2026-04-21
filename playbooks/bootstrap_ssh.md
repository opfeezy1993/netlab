# Bootstrap: first-time console setup

For each device, connect via the console cable and paste the relevant block
below. This is the one and only time you configure these devices by hand.
After this, every change is driven from Git via Ansible.

Replace `StrongPasswordHere!` and `StrongEnableSecretHere!` with your real
values (the same values you'll put in `inventory/group_vars/all/vault.yml`).

---

## For a 2960 switch (example: sw1 at 192.168.100.11)

```
enable
configure terminal

hostname sw1
ip domain-name lab.local
no ip domain-lookup

username labadmin privilege 15 secret StrongPasswordHere!
enable secret StrongEnableSecretHere!

crypto key generate rsa modulus 2048
ip ssh version 2

line vty 0 15
 transport input ssh
 login local
exit

vlan 99
 name MGMT
exit

interface Vlan99
 ip address 192.168.100.11 255.255.255.0
 no shutdown
exit

ip default-gateway 192.168.100.1

! Pick one port, put it in VLAN 99, plug your laptop/jump-host into it
interface FastEthernet0/24
 switchport mode access
 switchport access vlan 99
 no shutdown
exit

end
write memory
```

Repeat with `sw2` / `192.168.100.12` and `sw3` / `192.168.100.13`.

---

## For a 2600 series router (example: r1 at 192.168.100.21)

```
enable
configure terminal

hostname r1
ip domain-name lab.local
no ip domain-lookup

username labadmin privilege 15 secret StrongPasswordHere!
enable secret StrongEnableSecretHere!

crypto key generate rsa modulus 2048
ip ssh version 2

line vty 0 4
 transport input ssh
 login local
exit

! In-band management via Fa0/0 for now. Ansible will take over after this.
interface FastEthernet0/0
 ip address 192.168.100.21 255.255.255.0
 no shutdown
exit

end
write memory
```

Repeat with `r2` / `192.168.100.22` and `r3` / `192.168.100.23`.

> Note: the 2600 (non-XM) is very old. If `crypto key generate rsa` errors
> out, your IOS image may not be a k9 (crypto) image and won't support SSH.
> In that case, either flash a k9 image or use Telnet temporarily while you
> hunt down one. SSH is the target; don't stop until you get there.

---

## Verify from your laptop / jump host

```bash
ssh labadmin@192.168.100.11   # sw1
ssh labadmin@192.168.100.21   # r1
# ...etc
```

Once SSH works to all six, run:

```bash
ansible all -m cisco.ios.ios_facts --ask-vault-pass
```

If that prints facts for all six devices, the console cable is retired and
the repo owns your lab.
