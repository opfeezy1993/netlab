#!/usr/bin/env python3
"""
Backup running-configs from all lab devices using Netmiko.

This is the Python-native alternative to playbooks/backup_configs.yml.
Run it once to see what Ansible is doing under the hood, then use whichever
you prefer for daily work.

Usage:
    export LAB_USER=labadmin
    export LAB_PASS='your-password'
    export LAB_ENABLE='your-enable-secret'
    python3 scripts/backup_netmiko.py
"""
from __future__ import annotations

import concurrent.futures as cf
import os
import pathlib
import sys
from datetime import datetime

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

DEVICES = [
    {"host": "192.168.100.11", "name": "sw1", "device_type": "cisco_ios"},
    {"host": "192.168.100.12", "name": "sw2", "device_type": "cisco_ios"},
    {"host": "192.168.100.13", "name": "sw3", "device_type": "cisco_ios"},
    {"host": "192.168.100.21", "name": "r1",  "device_type": "cisco_ios"},
    {"host": "192.168.100.22", "name": "r2",  "device_type": "cisco_ios"},
    {"host": "192.168.100.23", "name": "r3",  "device_type": "cisco_ios"},
]


def backup_one(
    device: dict,
    out_dir: pathlib.Path,
    username: str,
    password: str,
    secret: str,
) -> tuple[str, bool, str]:
    """Connect, `show running-config`, write to file. Returns (name, ok, info)."""
    conn_args = {
        "device_type": device["device_type"],
        "host": device["host"],
        "username": username,
        "password": password,
        "secret": secret,
        "fast_cli": False,
    }
    try:
        with ConnectHandler(**conn_args) as conn:
            conn.enable()
            running = conn.send_command("show running-config")
        path = out_dir / f"{device['name']}.cfg"
        path.write_text(running + "\n")
        return device["name"], True, str(path)
    except (NetmikoAuthenticationException, NetmikoTimeoutException) as e:
        return device["name"], False, str(e)
    except Exception as e:  # noqa: BLE001
        return device["name"], False, f"unexpected: {e!r}"


def main() -> int:
    user = os.environ.get("LAB_USER")
    pw = os.environ.get("LAB_PASS")
    en = os.environ.get("LAB_ENABLE", pw or "")
    if not user or not pw:
        print("Set LAB_USER and LAB_PASS env vars.", file=sys.stderr)
        return 2

    stamp = datetime.now().strftime("%Y-%m-%d")
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    out = repo_root / "backups" / stamp
    out.mkdir(parents=True, exist_ok=True)

    ok = 0
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(backup_one, d, out, user, pw, en): d for d in DEVICES}
        for fut in cf.as_completed(futures):
            name, success, info = fut.result()
            mark = "OK " if success else "ERR"
            print(f"[{mark}] {name:>4}  {info}")
            if success:
                ok += 1

    print(f"\n{ok}/{len(DEVICES)} devices backed up -> {out}")
    return 0 if ok == len(DEVICES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
