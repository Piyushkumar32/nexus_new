# NEXUS 2.0 Deployment & Infrastructure Guide

## Standalone Deployment
```bash
pip install -e .[dev]
nexus api start --host 127.0.0.1 --port 8000
```

## Web Control Center Deployment
```bash
cd web
npm install
npm run dev
# Open http://localhost:3000
```
