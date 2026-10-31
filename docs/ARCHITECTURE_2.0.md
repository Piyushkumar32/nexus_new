# NEXUS 2.0 Architectural Specification & System Blueprints

## 1. System Vision & Operational Principles
NEXUS 2.0 extends host diagnostics into a comprehensive, production-grade observability and infrastructure intelligence platform. 

### Core Architecture Layers:
1. **Hardware & OS Sensor Layer**: Kernel metrics (CPU per-core, memory, swap, virtual pages, partition capacity, disk I/O, network throughput, battery and temperature sensors).
2. **Infrastructure Discovery Layer**: Container runtimes (Docker daemon, Kubernetes cluster nodes, pods, and namespaces) and host socket listeners.
3. **Deterministic Diagnostic Engine**: Rule-based bottleneck classification, multi-metric correlation (CPU/RAM thrashing), and confidence-scored incident detection.
4. **Offline AI Advisory Layer**: Explainable natural-language telemetry summaries and structured troubleshooting playbooks.
5. **Defensive Security Layer**: Unexpected port scanning, suspicious process pattern matching, and cryptographic file integrity auditing (SHA-256).
6. **Web Control Center**: Modern React 18, Vite, and Tailwind CSS observability frontend with live telemetry polling and responsive diagnostic inspection.
7. **Resilient Persistence**: SQLite with Write-Ahead Logging (WAL), indexed queries, and retention cleanup policies.
