# netlab: File Reference

What every file in this repo does, and why it's here.

If you're ever staring at a file and thinking "what on earth is this for," open this document.

---

## 1. The big picture

This repo turns your home lab into **infrastructure as code**. Instead of
typing commands at each device, every setting that runs on every device is
derived from files in this folder. You change a file. You run one command.
Every device reflects the change.

### Why it's organized this way

There are four separate jobs in automation, and each lives in its own place:

| Job              | Question it answers                                                | Folder                       |
| ---------------- | ------------------------------------------------------------------ | ---------------------------- |
| **Inventory**    | Who exists? (device list + addresses)                              | `inventory/hosts.yml`        |
| **Variables**    | What should each device have? (VLANs, IPs, NTP, syslog, etc.)      | `inventory/group_vars/`, `inventory/host_vars/` |
| **Templates**    | How should a config look? (the blueprint)                          | `templates/`                 |
| **Playbooks**    | When and in what order should things happen?                       | `playbooks/`                 |

Plus supporting zones:

| Zone               | Purpose                                                       | Folder                  |
| ------------------ | ------------------------------------------------------------- | ----------------------- |
| **Project config** | How Ansible and linters behave in this project                | root `.` files          |
| **Scripts**        | Pure-Python alternatives and one-off tools                    | `scripts/`              |
| **Docs**           | Human-readable context and design decisions                   | `docs/`                 |
| **CI**             | Automated safety net that runs on every push                  | `.github/workflows/`    |
| **Backups**        | Nightly snapshots of every device's running-config            | `backups/`              |

Keep this mental model: *inventory is who, vars are what, templates are how,
playbooks are when*. Every file fits one of those four roles or supports them.

---

## 2. File-by-file reference

### Project config (root of the repo)

#### `README.md`

The front page of the repo. First thing anyone opens, including future-you
and any hiring manager who clicks your GitHub link.

- **Why it exists:** Every serious repo has one. Without a README, the
  project is a mystery.
- **When you edit it:** When the layout changes, when you add a feature,
  when you complete a milestone and want to update the status checklist.
- **Analogy:** The sign at the front of a store that says what's inside and
  where everything is.

#### `.gitignore`

A list of file and folder patterns that Git must NEVER track.

- **Why it exists:** Some things should never leave your laptop —
  passwords, vault password files, rendered configs that contain secrets,
  editor cache, Python virtual environments. If you commit a password to a
  public repo, you're rotating credentials and possibly making the news.
- **When you edit it:** When a new tool creates cache files, when you
  adopt a new editor, or when you realize something almost slipped through.
- **Analogy:** The "no photos past this line" sign at a secure facility.

#### `ansible.cfg`

Ansible's own settings file for this project.

- **Why it exists:** Ansible has hundreds of settings. Without a local
  config file, it uses global defaults that know nothing about your repo.
  This file tells Ansible where your inventory is, how many devices to
  work on in parallel, how long to wait before giving up, etc.
- **When you edit it:** When you need to tune parallelism (`forks`),
  change timeouts, or switch the output callback.
- **Analogy:** The settings panel of a tool you rarely open but matter
  when defaults are wrong.

#### `requirements.yml`

The list of Ansible *collections* this project depends on.

- **Why it exists:** Ansible core is small. Everything vendor-specific
  (Cisco IOS, Arista EOS, Juniper Junos) lives in a separate collection
  that you install. This file is the shopping list.
- **When you edit it:** When you adopt a new vendor or pin to a newer
  version of a collection.
- **Install command:** `ansible-galaxy collection install -r requirements.yml`
- **Analogy:** `package.json` for Node, `Gemfile` for Ruby.

#### `requirements.txt`

The list of Python packages this project depends on.

- **Why it exists:** Ansible, Netmiko, ansible-lint, yamllint, paramiko —
  all Python packages. This file lets anyone clone the repo and install
  everything in one `pip install -r requirements.txt`.
- **When you edit it:** When you start using a new Python library (e.g.,
  `pynetbox` for NetBox, `napalm` for multi-vendor, `nornir` for parallel
  automation).

#### `.yamllint`

Configuration for `yamllint`, a style checker for YAML files.

- **Why it exists:** YAML is whitespace-sensitive. One wrong indent and
  your playbook silently misbehaves. `yamllint` catches these before you
  run anything. This file customizes which rules are strict.
- **When you edit it:** Rarely — only when a rule fights you in a way
  that's wrong for this project.

---

### Inventory zone (`inventory/`)

#### `inventory/hosts.yml`

The master list of every device Ansible should manage, grouped by role,
with reachable IP addresses.

- **Why it exists:** Automation is useless if the tool doesn't know what
  machines exist. This file is the answer to "who are we managing?"
- **When you edit it:** When you add or remove a device, change an IP,
  or regroup them.
- **Critical detail:** Credentials use `{{ vault_* }}` references.
  Actual passwords live encrypted in `vault.yml`, never in plaintext.
- **Analogy:** The phone book. Without it you can't call anyone.

#### `inventory/group_vars/all/main.yml`

Variables that apply to *every* device — lab domain, NTP servers, DNS
servers, syslog target, MOTD banner.

- **Why it exists:** Many settings are the same everywhere. Without this
  file, you'd copy-paste the NTP server into every device's file, and
  when it changes you'd miss one.
- **When you edit it:** When a lab-wide setting changes.
- **Analogy:** Company-wide HR policy. Applies to everyone unless
  explicitly overridden.

#### `inventory/group_vars/all/vault.yml.example`

A non-secret example of what your encrypted vault should contain.

- **Why it exists:** The real `vault.yml` is encrypted, so you can't peek
  inside. Future contributors (including future-you) need to know what
  variables the vault is supposed to define. The `.example` file
  documents the structure.
- **When you edit it:** When you add a new secret that playbooks need
  (e.g., a TACACS+ key, a RADIUS secret).

#### `inventory/group_vars/switches.yml`

Variables that apply to every switch but not routers — default VLAN list,
management VLAN ID, platform label.

- **Why it exists:** All three 2960s share the same VLANs. Defining them
  once in the group saves repetition and mistakes.
- **When you edit it:** When you add a new lab-wide VLAN or change the
  management VLAN.

#### `inventory/group_vars/routers.yml`

Variables that apply to every router — OSPF process ID, default area,
whether CEF is enabled.

- **Why it exists:** Same rationale as switches.
- **When you edit it:** When you change routing protocol defaults.

#### `inventory/host_vars/sw1.yml` (and sw2, sw3)

Per-switch specifics: hostname, management IP, access ports, trunk ports.

- **Why it exists:** Every device is physically unique even if they share
  a template. sw1 might have a user PC on Fa0/1; sw2 might have a server.
- **When you edit it:** Any time you physically rewire a port, any time
  a port's role changes.
- **Tip:** Think of this as the "reality" file. If sw1's Fa0/5 is
  actually plugged into a printer, this file should say so.

#### `inventory/host_vars/r1.yml` (and r2, r3)

Per-router specifics: hostname, management IP, interface list with IPs
and OSPF area assignments.

- **Why it exists:** Same rationale as switch host vars.
- **When you edit it:** When the IP plan changes, when you enable OSPF on
  a new interface, when you rewire between routers.

---

### Templates zone (`templates/`)

#### `templates/switch_baseline.j2`

A Jinja2 template that, combined with a switch's variables, renders a
complete switch configuration.

- **Why it exists:** Without templates, you'd maintain three nearly
  identical switch config files. Templates let you write the "shape"
  once and fill in specifics per device.
- **When you edit it:** When you want ALL switches to change together —
  new logging destination, new security hardening, new VLAN policy.
- **Key concept:** Jinja2 substitutes `{{ variable }}` with values. It
  loops with `{% for x in list %}...{% endfor %}`. Everything between
  those is the template's logic.
- **Analogy:** A form letter. "Dear ___, Thank you for ___." The
  template is the letter; the variables are the name and the subject.

#### `templates/router_baseline.j2`

Same concept, for routers. Renders hostname, interface configs, OSPF,
SSH, logging, NTP, enable secret, etc.

---

### Playbooks zone (`playbooks/`)

#### `playbooks/gather_facts.yml`

Asks every device "what model are you, what IOS version, what serial
number, how long have you been up?"

- **Why it exists:** First real test that Ansible can reach every device.
  Also useful for inventory auditing — you'd be surprised how often the
  device in rack slot 3 is not the model you thought.
- **When you run it:** As a connectivity smoke test. Before any big
  change. After a hardware swap.
- **Command:** `ansible-playbook playbooks/gather_facts.yml --ask-vault-pass`

#### `playbooks/backup_configs.yml`

Runs `show running-config` on every device and saves the output to
`backups/YYYY-MM-DD/<device>.cfg`.

- **Why it exists:** This is your history book. If a config breaks
  something at 2pm and was working at 10am, you diff the two backups.
- **When you run it:** On a schedule (cron/systemd timer). Before and
  after big changes. After someone says "I didn't change anything."
- **Analogy:** A time machine for your network. Every day at midnight,
  it takes a photograph.

#### `playbooks/push_baseline.yml`

The big one. Renders each device's baseline config from its template +
variables, then pushes the result onto the device.

- **Why it exists:** This is the step that turns "config as code" into
  "config as reality." Without this playbook, the repo is just nice files.
- **When you run it:** When you change templates, group vars, or host
  vars and want those changes reflected on the devices.
- **Safety tip:** Always run with `--check --diff` first. That simulates
  the push and shows exactly what would change without changing anything.

#### `playbooks/bootstrap_ssh.md`

NOT a playbook. It's a markdown runbook containing the manual console
commands you paste once per device during initial setup.

- **Why it exists:** Ansible needs SSH. Brand-new devices have no SSH.
  There's a chicken-and-egg problem: you must configure SSH *before*
  Ansible can configure anything. This document solves it.
- **When you use it:** Exactly once per device, at the very start of its
  life in your lab.

---

### Scripts zone (`scripts/`)

#### `scripts/backup_netmiko.py`

A pure Python script that does the same job as `backup_configs.yml`, but
using the Netmiko library directly instead of Ansible.

- **Why it exists:** Two reasons. First, it's a teaching tool — you see
  what Ansible is doing under the hood. Second, sometimes you need to do
  something Ansible can't easily express, and Python is your escape hatch.
- **When you run it:** When you're debugging why Ansible won't connect
  (does raw SSH via Netmiko work?). Or when you want a lean, fast backup
  without Ansible overhead.
- **Analogy:** Ansible and this script are two keys to the same door. If
  one key sticks, try the other while you figure out what's wrong.

---

### Docs zone (`docs/`)

#### `docs/topology.md`

A human-readable description of your physical and logical lab — which
device connects to which, which cables go where, how subnets fit together.

- **Why it exists:** Six months from now, you will not remember why
  sw2's Gi0/2 connects to sw3's Gi0/1. This file is a note to future-self.
- **When you edit it:** Every time you rewire something.

#### `docs/ip-plan.md`

The master IP-addressing reference, in markdown tables. Every subnet,
every management IP, every point-to-point link.

- **Why it exists:** Without a plan, you double-assign IPs and lose
  sleep debugging phantom connectivity issues.
- **When you edit it:** When you add or remove a subnet, add a device,
  change the plan.

#### `docs/secrets.md`

A runbook for using ansible-vault in this project — create, edit, run
playbooks with encrypted credentials.

- **Why it exists:** ansible-vault is easy once you remember the syntax.
  This document is the "I forget the syntax" safety net.

#### `docs/file-reference.md`

This document.

---

### Misc files

#### `backups/.gitkeep`

An empty file whose only purpose is to exist.

- **Why it exists:** Git ignores empty directories. If you want the
  `backups/` folder to exist in the repo before any backups are written,
  you need at least one file inside. `.gitkeep` is the conventional name
  — not a Git feature, just a widely recognized marker.
- **When you edit it:** Never. It's a placeholder.

#### `.github/workflows/lint.yml`

A GitHub Actions workflow. Every time you push code to GitHub, this file
tells GitHub to spin up a fresh Ubuntu VM, install Ansible, and run
`yamllint` and `ansible-lint` on the repo.

- **Why it exists:** Automation's safety net. If a typo sneaks into a
  playbook, the PR gets a red X before it's merged. You catch mistakes
  before they hit production.
- **When you edit it:** When you want to add more checks (syntax-check,
  dry-run, unit tests) or change Python versions.
- **Analogy:** The bouncer at the door. Nothing bad gets into `main`
  without passing.

---

## 3. How they all work together

When you run `ansible-playbook playbooks/push_baseline.yml --ask-vault-pass`,
here's exactly what happens:

1. Ansible reads `ansible.cfg` for project-wide defaults (inventory
   location, timeouts, parallelism).
2. Ansible loads the device list from `inventory/hosts.yml` and sees six
   devices in two groups: `switches` and `routers`.
3. For each device, Ansible merges variables in this order, with later
   sources overriding earlier ones:
   - `group_vars/all/main.yml` (lab-wide)
   - `group_vars/all/vault.yml` (decrypted credentials)
   - `group_vars/switches.yml` or `group_vars/routers.yml` (role-specific)
   - `host_vars/<device>.yml` (device-specific)
4. The playbook iterates over every device. For each one:
   - The `template` task reads the appropriate `.j2` file and renders it
     against the merged variables, producing `rendered/<device>.cfg`.
   - The `ios_config` task opens an SSH connection using the vault
     credentials and pushes the rendered config to the device.
   - If any lines changed, `save_when: modified` writes to NVRAM.
5. Ansible prints a per-device summary of what changed.

Every file in the repo plays a role in that single command. That's the
point.

---

## 4. Glossary

| Term | One-line meaning |
| ---- | ---------------- |
| **YAML** | A markup language for structured data. Indentation matters. |
| **Jinja2** | A templating language Ansible uses for `.j2` files. |
| **Ansible** | Agentless automation tool — runs on your laptop, pushes over SSH. |
| **Playbook** | A YAML file describing tasks to run. |
| **Inventory** | Ansible's list of devices to manage. |
| **Group** | A named collection of hosts in the inventory. |
| **Variable / var** | A piece of data Ansible uses to customize tasks per device. |
| **Vault** | Ansible's encryption system for secrets. |
| **Collection** | A shareable bundle of Ansible modules (e.g., `cisco.ios`). |
| **Module** | A pre-built, idempotent task (e.g., `ios_config`). |
| **Idempotent** | Running it twice produces the same result as running it once. |
| **Netmiko** | Python library for SSH-ing to network devices. |
| **NAPALM** | Multi-vendor network library with a unified API. |
| **YANG** | A modeling language for network configuration (modern gear). |
| **NETCONF** | A protocol for sending YANG models to devices (modern gear). |
| **gNMI** | A newer streaming protocol for telemetry and config. |
| **Git** | Version control. Every change tracked, nothing lost. |
| **Repo** | A folder Git watches. |
| **Commit** | A snapshot of the repo at a moment in time. |
| **Branch** | A parallel line of development. |
| **CI** | Continuous Integration — checks that run automatically on push. |
| **Linter** | A tool that checks style and common errors. |

---

## 5. Command cheat sheet

### First-time setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
ansible-vault create inventory/group_vars/all/vault.yml
```

### Daily commands

```bash
# Smoke test - can Ansible talk to every device?
ansible all -m cisco.ios.ios_facts --ask-vault-pass

# Back up every running-config
ansible-playbook playbooks/backup_configs.yml --ask-vault-pass

# DRY RUN - what WOULD change if I pushed? (safe, no writes)
ansible-playbook playbooks/push_baseline.yml --ask-vault-pass --check --diff

# Actually push baseline configs
ansible-playbook playbooks/push_baseline.yml --ask-vault-pass

# Lint YAML before committing
yamllint .

# Lint Ansible specifically
ansible-lint playbooks/

# Python backup alternative
LAB_USER=labadmin LAB_PASS='yourpass' python3 scripts/backup_netmiko.py
```

### Git basics

```bash
git status                  # what's changed?
git diff                    # show the changes
git add <file>              # stage a file
git commit -m "message"     # commit staged changes
git push                    # upload to GitHub
git log --oneline           # show history
git checkout -b feat/xyz    # start a new branch
```

### Ansible-vault

```bash
ansible-vault create inventory/group_vars/all/vault.yml   # first time
ansible-vault edit inventory/group_vars/all/vault.yml     # change contents
ansible-vault view inventory/group_vars/all/vault.yml     # read without opening editor
ansible-vault rekey inventory/group_vars/all/vault.yml    # change the password
```

---

## 6. Rules of thumb

1. **Never type into a device by hand** — after bootstrap. If you find
   yourself doing it, stop and ask: "why isn't this in a playbook?"
2. **Git commit early, commit often** — each small change a separate
   commit with a clear message. Future-you will thank present-you.
3. **Dry-run before pushing** — `--check --diff` on every
   `push_baseline` run until you trust yourself, then still do it anyway.
4. **Never commit secrets** — if a password lands in Git, rotate the
   credential immediately and rewrite history (it's on the internet now).
5. **Backups are cheap; downtime isn't** — run `backup_configs.yml`
   before every change, not just on a schedule.
6. **Prefer deletion to comments** — if code isn't used, remove it. Git
   remembers.
7. **Read error messages top to bottom** — Ansible errors can be verbose
   but the actual cause is usually in the first 10 lines.
