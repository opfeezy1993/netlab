# Lesson 01: Config-as-code

The single most important philosophical decision in this entire lab is that
**device configurations are not entered by hand on the device** — they are
written as code, stored in git, and applied by automation. Every other choice
in this repository flows from that one.

## What we did

We built a git repository (`netlab/`) that contains:

- **Inventory** — a structured list of every device with its IP, role, and
  per-device variables (interfaces, IPs, OSPF areas, etc.).
- **Templates** — Jinja2 templates that render Cisco configurations
  programmatically based on the inventory.
- **Playbooks** — Ansible workflows that pull the inventory, render the
  templates, and push the resulting configs to each device.
- **Documentation** — everything from the IP plan to the asset register.

Then we pushed the entire repository to GitHub. Every change, from now
forward, is a commit. Every commit has an author, a timestamp, a
message, and a diff.

## Why it exists

Network engineering before config-as-code looked like this:

- You SSH into a switch.
- You type `configure terminal`.
- You make changes — sometimes correctly, sometimes not.
- You hope you remembered to `write memory`.
- You forget which changes you made.
- The switch fails. Nobody can rebuild it from scratch.
- A coworker makes a "small change." Nobody knows. Service breaks.

This is sometimes called *"snowflake infrastructure"* — every device is a
unique, hand-crafted artifact that nobody can reproduce. Snowflakes melt.

The alternative is *"cattle, not pets":* devices are interchangeable, their
configurations live in a single source-of-truth outside the device, and the
device is just an executor of that truth. If a switch dies, you replace it,
push the same config from the repository, and you're back online in
minutes — not days.

For this lab specifically, the value is even more direct:

- **Reproducibility.** If a 4331 dies, I push a new one to AWS, console in,
  run the bootstrap, run the Ansible play, and it's identical to the dead
  one within an hour.
- **Auditability.** Every config change is a git commit. I can answer
  *"who changed VLAN 20 last Tuesday?"* with a single command.
- **Code review.** Before pushing changes to a real device, someone else
  (or future-me) can review the diff. Catching mistakes pre-deployment is
  cheaper than rolling back post-outage.
- **Portfolio.** The repository itself is the evidence of skill. A hiring
  engineer can read the templates and inventory and conclude — within
  minutes — whether the candidate understands the craft.

## How it works under the hood

The pipeline is layered:

```
   inventory/hosts.yml + host_vars/*.yml
                |
                v
   templates/*.j2   ──>  Ansible renders the per-device config
                |
                v
   ansible-playbook push_baseline.yml
                |
                v
   SSH to each device, apply the rendered config, save
                |
                v
   git commit -am "deployed baseline to r1, r2, sw1"
   git push
```

The repository contains the *intent* — what the network should look like.
Ansible reconciles the device's *actual* state with the intent. If the device
already matches, Ansible does nothing (this is **idempotency** — see Lesson
06). If it doesn't, Ansible applies only the delta.

The data flow is unidirectional: **git → device, never device → git.** If
someone changes a device by hand, the next Ansible run will overwrite their
changes. This is a feature, not a bug — it forces all changes through the
repository, where they're reviewed and tracked.

## Alternatives

- **Hand configuration.** Type into the CLI. Works for one device. Breaks at
  scale. Used to be the only way; now considered an anti-pattern in any
  shop with more than a handful of devices.
- **NETCONF/RESTCONF/YANG (model-driven automation).** Modern alternative to
  Ansible's CLI-driven approach. The device exposes a structured API based
  on YANG models. Tools like `cisco.iosxr.iosxr_facts` or vendor SDKs
  interact with this. Better long-term, more complex to set up. See Lesson 14.
- **Vendor-specific platforms** (Cisco DNA Center, NetBox + Nautobot,
  Juniper Mist, Arista CloudVision). All of these are config-as-code with
  proprietary GUIs and APIs on top. Same philosophy, different surface.
- **GitOps with Argo or Flux.** Used in the Kubernetes world but increasingly
  applicable to network gear. The git commit is the trigger; a controller
  watches the repo and reconciles continuously. Probably where the industry
  heads next.

Why we chose Ansible + Jinja2 + git for this lab:
- **Ansible** has the largest community and the deepest support for the
  Cisco gear in this lab (especially the legacy 2960/3550).
- **Jinja2** is the lingua franca of network configuration templating.
  Skills transfer across vendors.
- **Git** is universal.
- The combination is what every mid-sized enterprise actually runs today,
  even at AWS-scale shops, alongside more modern tooling.

## Interview answer

> "Config-as-code is the practice of storing network device configurations
> in a version-controlled repository — typically git — and applying them
> via automation rather than by hand. The repository is the source of
> truth; the device is just an executor. The benefits are reproducibility
> (you can rebuild a failed device from the repo), auditability (every
> change is a commit with an author and timestamp), and reviewability
> (changes can be peer-reviewed before deployment). In my home lab, I
> implement this with Ansible playbooks that render Jinja2 templates from
> a YAML inventory and push the result via SSH. The same pattern scales
> from six devices to six thousand — the philosophy doesn't change, just
> the orchestration layer."

## See also

- Lesson 03: The Ansible inventory model
- Lesson 06: Jinja2 templates and idempotency
- Lesson 14: NETCONF, RESTCONF, and YANG vs CLI automation
