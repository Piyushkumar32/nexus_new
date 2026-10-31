export interface SystemInfo {
  os: string;
  os_version: string;
  platform: string;
  hostname: string;
  python_version: string;
  cpu_model: string;
  logical_cores: number;
  physical_cores: number;
  total_ram_bytes: number;
  uptime_seconds: number;
}

export interface MetricSnapshot {
  captured_at: number;
  cpu: {
    percent: number;
    logical_cores: number;
    frequency_mhz?: number;
    load_average?: number[];
  };
  memory: {
    total_bytes: number;
    used_bytes: number;
    percent: number;
    swap_percent: number;
  };
  disks: Array<{
    mountpoint: string;
    percent: number;
    used_bytes: number;
    total_bytes: number;
  }>;
  network: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
  };
  sensors?: {
    battery?: { percent: number; power_plugged: boolean };
  };
  gpu?: Array<{
    name: string;
    utilization_percent: number;
    memory_percent: number;
  }>;
}

export interface Finding {
  id: string;
  severity: string;
  category: string;
  description: string;
  value?: number;
  suggested_action?: string;
}

export interface Container {
  id: string;
  name: string;
  image: string;
  status: string;
  state: string;
}

export const fetchMetrics = async (): Promise<MetricSnapshot> => {
  const res = await fetch('/api/v1/system/metrics');
  const json = await res.json();
  return json.data;
};

export const fetchSystemInfo = async (): Promise<SystemInfo> => {
  const res = await fetch('/api/v1/system/info');
  const json = await res.json();
  return json.data;
};

export const fetchDiagnostics = async (): Promise<Finding[]> => {
  const res = await fetch('/api/v1/diagnostics');
  const json = await res.json();
  return json.data;
};