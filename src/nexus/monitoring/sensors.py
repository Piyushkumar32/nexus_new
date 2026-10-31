"""Hardware sensor monitoring (Battery, Temperature, Fans) with graceful platform degradation."""

from __future__ import annotations

from typing import Any

import psutil


def collect_sensors() -> dict[str, Any]:
    """Collect hardware sensor information where supported by OS."""
    data: dict[str, Any] = {
        "battery": None,
        "temperatures": {},
        "fans": {},
    }

    # Battery
    try:
        battery = psutil.sensors_battery()
        if battery:
            data["battery"] = {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "secsleft": None if battery.secsleft < 0 else battery.secsleft,
            }
    except (AttributeError, NotImplementedError, OSError):
        pass

    # Temperatures (Linux/macOS)
    if hasattr(psutil, "sensors_temperatures"):
        try:
            raw_temps = psutil.sensors_temperatures()
            if raw_temps:
                for name, entries in raw_temps.items():
                    data["temperatures"][name] = [
                        {
                            "label": e.label or name,
                            "current": e.current,
                            "high": e.high,
                            "critical": e.critical,
                        }
                        for e in entries
                    ]
        except (AttributeError, NotImplementedError, OSError):
            pass

    # Fans (Linux/macOS)
    if hasattr(psutil, "sensors_fans"):
        try:
            raw_fans = psutil.sensors_fans()
            if raw_fans:
                for name, entries in raw_fans.items():
                    data["fans"][name] = [
                        {"label": e.label or name, "current": e.current}
                        for e in entries
                    ]
        except (AttributeError, NotImplementedError, OSError):
            pass

    return data