# Lesson 03: The Ansible inventory model

When you look at the `inventory/` folder in this repo, you see a YAML file
listing devices, plus subfolders called `group_vars/` and `host_vars/`. This
hierarchy isn't arbitrary — it's the **Ansible inventory model**, a
deliberate structure that scales from six devices to six thousand without
fundamentally changing.

Understanding this model is the difference between writing automation that
works for one playbook and writing automation that's maintainable across a
career.

## What we did

We built this structure:

```
inventory/
├── hosts.yml                       # Master inventory: which devices exist
├── group_vars/
│   ├── all/
│   │   ├── main.yml                # Variables every device gets
│   │   └── vault.yml.example       # Encrypted secrets template
│   ├── switches.yml                # Variables only for switches
│   └── routers.yml                 # Variables only for routers
└── host_vars/
    ├── sw1.yml                     # Per-device config for SW-CORE
    ├── sw2.yml                     # Per-device config for SW-L3-LAB
    ├── ...
    ├── r1.yml                      # Per-device config for R-EDGE
    └── r2.yml                      # Per-device config for R-CORE
```

In `hosts.yml`, devices are organized into groups:

```yaml
all:
  children:
    switches:
      hosts:
        sw1:
          ansible_host: 192.168.100.11
        sw2:
          ansible_host: 192.168.100.12
        sw3:
          ansible_host: 192.168.100.13
    routers:
      hosts:
        r1:
          ansible_host: 192.168.100.21
        r2:
          ansible_host: 192.168.100.22
```

When Ansible runs a playbook against `sw1`, it composes the variables for
that device from three layers (in order of precedence):

1. `host_vars/sw1.yml`  — most specific
2. `group_vars/switches.yml`  — group-level
3. `group_vars/all/main.yml`  — global default

Lower-precedence values are overridden by higher-precedence ones.

## Why it exists

If every device's configuration was hard-coded into a single playbook, three
things would break immediately:

1. **Duplication.** Every device needs an NTP server, a DNS server, a syslog
   host. If you hard-code these into the playbook, changing them means
   editing every play. With the inventory model, you change `group_vars/all/
   main.yml` once and every device gets the new value.

2. **Differentiation.** A switch needs VLANs; a router doesn't. A core
   switch has trunk uplinks; an access switch has user ports. The inventory
   model lets each device have only the variables relevant to its role.

3. **Scale.** Six devices is small. Sixty is medium. Six thousand is real
   enterprise. The same inventory model handles all three without
   restructuring.

The model is also self-documenting. Reading `hosts.yml` tells you what
devices exist. Reading `group_vars/switches.yml` tells you what *every*
switch shares. Reading `host_vars/sw1.yml` tells you what makes sw1
distinct. This separation makes troubleshooting and onboarding
dramatically faster.

## How it works under the hood

The variable composition happens at **task execution time**. When Ansible
runs a task against a host, it merges all applicable variables into a
single namespace (using Ansible's documented precedence rules — about 22
distinct levels, but the four most important are):

```
Priority (low to high):
1. group_vars/all/*.yml            ← global defaults
2. group_vars/<groupname>.yml      ← group-specific
3. host_vars/<hostname>.yml        ← per-host
4. -e cli args / set_fact          ← runtime overrides
```

So if `group_vars/all/main.yml` has `ntp_server: 1.1.1.1` and
`host_vars/sw1.yml` has `ntp_server: 192.168.100.5`, sw1 uses the latter;
every other host uses the former.

Inside templates, this is invisible. A Jinja2 template just references
`{{ ntp_server }}` — and gets whichever value is correct for the host
being rendered. You don't write per-host logic. You write a *template*,
and let the inventory model resolve the values.

When `ansible-playbook` is invoked, the workflow is:

```
1. Read hosts.yml → know which devices to target.
2. For each device in scope:
   a. Walk group_vars/all/*.yml  → load defaults.
   b. Walk group_vars/<each-group-host-is-in>/*.yml  → override.
   c. Walk host_vars/<hostname>.yml  → final override.
3. Render templates with the composed variable set.
4. Apply the resulting config to the device over SSH.
```

This means the same playbook produces different (correct) configs for every
device — without any per-device conditional logic in the playbook itself.

## Alternatives

- **Single hard-coded playbook.** Works for one device. Falls apart at two.
- **Spreadsheet → script converter.** What many shops did pre-Ansible:
  maintain an Excel sheet, run a Python script to generate per-device
  configs. Works, but lacks composition, validation, and idempotency.
- **NetBox + dynamic inventory.** The next-step evolution: instead of a
  static YAML file, you query NetBox (a network source-of-truth database)
  for the device list, IPs, and roles. NetBox is the inventory; the YAML
  files become caches. Many enterprises use this combination.
- **Terraform.** Treats infrastructure as declarative state. More popular
  for cloud and virtual gear; usable for some networking equipment, but
  the ecosystem isn't as mature for legacy Cisco IOS.

Why we use Ansible's native model for this lab:
- **Zero external dependencies.** No database, no API, just YAML files in
  git. Easier to grasp and demo.
- **Pairs with the config-as-code philosophy.** Inventory is just more
  code in the repo.
- **Pluggable later.** Once NetBox is added, the inventory just becomes a
  dynamic pull from NetBox — but the templates and playbooks don't change.

## A concrete example

Suppose you decide every switch should log to syslog server 192.168.100.10.

In `group_vars/all/main.yml`:
```yaml
syslog_host: 192.168.100.10
```

In the template `templates/switch_baseline.j2`:
```
logging host {{ syslog_host }}
```

Now apply to all switches:
```
ansible-playbook playbooks/push_baseline.yml --limit switches
```

Every switch gets `logging host 192.168.100.10` in its config. Three months
later, the syslog server is moved to 192.168.100.99. You update one line in
`group_vars/all/main.yml`, rerun the playbook, every switch updates. No
device-by-device editing. No "I forgot sw5." Mathematically guaranteed
consistency.

## Interview answer

> "Ansible's inventory model uses a layered hierarchy: global defaults in
> `group_vars/all/`, group-level overrides in `group_vars/<group>.yml`, and
> per-host specifics in `host_vars/<hostname>.yml`. At runtime Ansible
> merges these into a single variable namespace per host, with more
> specific layers overriding less specific. This separates the *intent*
> (what we want every device, or every switch, or this specific device, to
> look like) from the *templates* (the configuration code itself) and the
> *playbooks* (the orchestration). The benefit is composability — global
> changes happen in one place, and the same templates handle every device
> in the fleet. It scales without changing structure: the same model that
> manages six lab devices manages thousands of devices at companies like
> Cisco's customers or major service providers. In larger deployments,
> static YAML inventory is replaced by a dynamic inventory plugin that
> queries NetBox or another source-of-truth database, but the templates
> and playbooks remain unchanged."

## See also

- Lesson 01: Config-as-code
- Lesson 06: Jinja2 templates and idempotency
