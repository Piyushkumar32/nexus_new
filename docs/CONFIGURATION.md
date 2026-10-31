# NEXUS Configuration Guide

NEXUS looks for configuration in YAML format. By default, it runs with safe, tested defaults. You can specify a custom configuration file using the `--config` flag:

```bash
nexus --config /path/to/config.yaml <command>
```

## Sample Configuration (`config/default.yaml`)

```yaml
app:
  name: NEXUS
  database_path: ~/.nexus/nexus.db
  report_directory: ./reports

monitoring:
  interval_seconds: 2
  process_limit: 20

thresholds:
  cpu_warning: 80
  memory_warning: 85
  disk_warning: 90
  process_cpu_warning: 80
  process_memory_warning: 20
  repeated_log_errors: 3
  resource_spike_delta: 25

health_weights:
  cpu: 0.35
  memory: 0.35
  disk: 0.30

health_thresholds:
  healthy: 80
  degraded: 60

logging:
  level: INFO
  file: ~/.nexus/nexus.log
```
