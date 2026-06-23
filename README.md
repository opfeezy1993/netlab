# netlab

Home networking lab automation for 3x Cisco Catalyst 2960 switches and 3x Cisco 2600 series routers.


## Goal

Every device in this lab is configured, backed up, and auditable from this repo. No manual CLI drift. Every change is reviewed in Git, validated in CI, and rolled out via Ansible.

## Layout

```
netlab/
├── ansible.cfg                 # Ansible defaults for this project
├── requirements.txt            # Python deps (ansible, netmiko, lint)
├── requirements.yml            # Ansible collections (cisco.ios, netcommon)
├── inventory/
│   ├── hosts.yml               # Device inventory (6 devices)
│   ├── group_vars/
│   │   ├── all/
│   │   │   ├── main.yml        # Lab-wide, non-secret vars
│   │   │   └── vault.yml       # Encrypted credentials (created by you)
│   │   ├── switches.yml        # Switch-group defaults (VLANs, mgmt)
│   │   └── routers.yml         # Router-group defaults (OSPF, CEF)
│   └── host_vars/
│       ├── sw1.yml … sw3.yml   # Per-switch specifics
│       └── r1.yml … r3.yml     # Per-router specifics
├── playbooks/
│   ├── gather_facts.yml        # show version + model + serial
│   ├── backup_configs.yml      # Pull running-config from all devices
│   ├── push_baseline.yml       # Render + push full baseline config
│   └── bootstrap_ssh.md        # Manual console steps for first boot
├── templates/
│   ├── switch_baseline.j2      # 2960 baseline Jinja2 template
│   └── router_baseline.j2      # 2600 baseline Jinja2 template
├── scripts/
│   └── backup_netmiko.py       # Python/Netmiko backup — the "other way"
├── backups/                    # Nightly configs (gitignored early, committed later)
├── docs/
│   ├── topology.md             # Physical + logical topology (WIP)
│   ├── ip-plan.md              # IP addressing plan
│   └── secrets.md              # How to use ansible-vault
└── .github/workflows/lint.yml  # CI: yamllint + ansible-lint on every PR
```

## Quickstart

```bash
# 1. Clone
git clone <this-repo> netlab && cd netlab

# 2. Python venv + deps
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Ansible collections
ansible-galaxy collection install -r requirements.yml

# 4. Create the encrypted credentials vault (see docs/secrets.md)
ansible-vault create inventory/group_vars/all/vault.yml

# 5. On each device, run the console bootstrap once (see playbooks/bootstrap_ssh.md)

# 6. Test Ansible can reach every device
ansible all -m cisco.ios.ios_facts --ask-vault-pass

# 7. First real playbook — back up every running-config into backups/YYYY-MM-DD/
ansible-playbook playbooks/backup_configs.yml --ask-vault-pass
```

## Conventions

- Hostnames: `sw1, sw2, sw3, r1, r2, r3`
- Management network: `192.168.100.0/24`
- Credentials: local user `labadmin` + enable secret, both stored encrypted in `inventory/group_vars/all/vault.yml`
- Cable colors: blue = access, yellow = trunk, green = mgmt, red = WAN
- Everything lives in Git. If it isn't in the repo, it doesn't exist.

## Status

- [x] Repo scaffolding
- [x] Physical rack build (awaiting 16U rack delivery)
- [x] Console bootstrap on all 6 devices
- [x] SSH reachability to all 6 devices from laptop
- [x] `gather_facts.yml` returns clean output for every device
- [x] `backup_configs.yml` writes 6 files into today's backup dir
- [x] `push_baseline.yml` renders and pushes without error
- [x] Nightly backup cron on jump host (Pi)
- [ ] NetBox source of truth wired into Ansible dynamic inventory
- [ ] CI: yamllint + ansible-lint passing on `main`
- [ ] Dry-run (`--check --diff`) gating every push
