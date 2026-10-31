"""Network interfaces, throughput, and packet statistics."""

from __future__ import annotations

import psutil


def collect_network() -> dict:
    try:
        counters = psutil.net_io_counters(pernic=False)
    except (OSError, PermissionError):
        counters = None

    try:
        per_nic_counters = psutil.net_io_counters(pernic=True)
    except (OSError, PermissionError):
        per_nic_counters = {}

    try:
        stats = psutil.net_if_stats()
    except (OSError, PermissionError):
        stats = {}

    try:
        addrs = psutil.net_if_addrs()
    except (OSError, PermissionError):
        addrs = {}

    interfaces = {}
    for nic, stat in stats.items():
        nic_addrs = []
        for addr in addrs.get(nic, []):
            nic_addrs.append({
                "family": str(addr.family),
                "address": addr.address,
                "netmask": addr.netmask,
                "broadcast": addr.broadcast,
            })
        nic_io = per_nic_counters.get(nic)
        interfaces[nic] = {
            "isup": stat.isup,
            "duplex": str(stat.duplex),
            "speed": stat.speed,
            "mtu": stat.mtu,
            "bytes_sent": getattr(nic_io, "bytes_sent", 0),
            "bytes_recv": getattr(nic_io, "bytes_recv", 0),
            "packets_sent": getattr(nic_io, "packets_sent", 0),
            "packets_recv": getattr(nic_io, "packets_recv", 0),
            "errin": getattr(nic_io, "errin", 0),
            "errout": getattr(nic_io, "errout", 0),
            "dropin": getattr(nic_io, "dropin", 0),
            "dropout": getattr(nic_io, "dropout", 0),
            "addresses": nic_addrs,
        }

    return {
        "bytes_sent": getattr(counters, "bytes_sent", 0),
        "bytes_recv": getattr(counters, "bytes_recv", 0),
        "packets_sent": getattr(counters, "packets_sent", 0),
        "packets_recv": getattr(counters, "packets_recv", 0),
        "errin": getattr(counters, "errin", 0),
        "errout": getattr(counters, "errout", 0),
        "dropin": getattr(counters, "dropin", 0),
        "dropout": getattr(counters, "dropout", 0),
        "interfaces": interfaces,
    }