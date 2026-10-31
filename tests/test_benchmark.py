"""Performance benchmark tests for metric collection overhead."""

import time

from nexus.monitoring.system import collect_metrics


def test_metric_collection_benchmark():
    start = time.perf_counter()
    metrics = collect_metrics()
    duration = time.perf_counter() - start
    assert metrics is not None
    assert duration < 2.0  # Collection overhead must remain strictly bounded under 2 seconds