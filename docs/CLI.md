# NEXUS CLI Documentation

NEXUS provides a rich terminal interface powered by Typer and Rich.

## Usage & Help

```bash
nexus --help
```

## Commands

### System Information
```bash
nexus info
```

### Metrics Monitoring
```bash
# Point-in-time metrics check
nexus monitor

# Continuous live-refresh monitor
nexus monitor --watch --interval 2.0
```

### Health Score Calculation
```bash
nexus health
```

### Process Inspection
```bash
# Top CPU consuming processes
nexus processes --sort cpu --limit 15

# Top memory consuming processes
nexus processes --sort memory --limit 15
```

### Diagnostics & Findings
```bash
nexus diagnose
```

### Anomalies Inspection
```bash
nexus anomalies
```

### Alerts History
```bash
nexus alerts
```

### Log File Analysis
```bash
nexus logs analyze /path/to/logfile.log
```

### Report Generation & Inspection
```bash
# Generate executive HTML report
nexus reports generate -o executive_report.html

# Generate JSON report
nexus reports generate -o report.json --format json

# List historical snapshot records
nexus reports list
```

### REST API Server
```bash
nexus api start --host 127.0.0.1 --port 8000
```

### Configuration Validation
```bash
nexus config validate
```
