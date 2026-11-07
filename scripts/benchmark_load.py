"""Automated load testing and latency benchmarking script.
Measures p50, p95, p99 latencies, RPS, and error rates across concurrency tiers.
"""

import concurrent.futures
import statistics
import threading
import time

import httpx

BASE_URL = "http://127.0.0.1:8000"
PASSWORD = "DemoPassword123!"

_thread_local = threading.local()


def get_client(token: str | None = None) -> httpx.Client:
    if not hasattr(_thread_local, "client"):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        _thread_local.client = httpx.Client(
            base_url=BASE_URL,
            headers=headers,
            timeout=10.0,
            limits=httpx.Limits(max_keepalive_connections=50, max_connections=100),
        )
    return _thread_local.client


def login(user_id: str = "U_HR") -> str:
    with httpx.Client(base_url=BASE_URL) as client:
        res = client.post("/api/sessions", json={"user_id": user_id, "password": PASSWORD})
        if res.status_code != 200:
            raise RuntimeError(f"Login failed: {res.status_code} {res.text}")
        return res.json()["access_token"]


def benchmark_endpoint(endpoint: str, concurrency: int, total_requests: int, token: str = None):
    latencies = []
    statuses = {}
    start_time = time.perf_counter()

    def send_request():
        client = get_client(token)
        req_start = time.perf_counter()
        try:
            res = client.get(endpoint)
            lat_ms = (time.perf_counter() - req_start) * 1000.0
            return res.status_code, lat_ms
        except Exception as e:
            lat_ms = (time.perf_counter() - req_start) * 1000.0
            return f"ERR:{type(e).__name__}", lat_ms

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_request) for _ in range(total_requests)]
        for f in concurrent.futures.as_completed(futures):
            status, lat = f.result()
            latencies.append(lat)
            statuses[status] = statuses.get(status, 0) + 1

    total_time = time.perf_counter() - start_time
    rps = total_requests / total_time if total_time > 0 else 0
    latencies.sort()

    p50 = statistics.median(latencies) if latencies else 0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
    p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0
    avg = statistics.mean(latencies) if latencies else 0

    return {
        "endpoint": endpoint,
        "concurrency": concurrency,
        "requests": total_requests,
        "total_time_s": round(total_time, 3),
        "rps": round(rps, 1),
        "min_ms": round(min(latencies), 2) if latencies else 0,
        "avg_ms": round(avg, 2),
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2),
        "p99_ms": round(p99, 2),
        "max_ms": round(max(latencies), 2) if latencies else 0,
        "statuses": statuses,
    }


def main():
    print("=" * 75, flush=True)
    print("OnboardIQ Performance & Load Benchmark Suite", flush=True)
    print("=" * 75, flush=True)

    token = login("U_HR")
    print(f"[AUTH] Established Bearer token for U_HR: {token[:10]}...", flush=True)

    scenarios = [
        ("/api/health", 10, 100),
        ("/api/health", 25, 200),
        ("/api/health", 50, 300),
        ("/api/hires", 10, 50),
        ("/api/hires", 25, 100),
        ("/api/analytics/overview", 10, 50),
        ("/api/analytics/overview", 25, 100),
        ("/api/audit-events", 10, 50),
        ("/api/audit-events", 25, 100),
    ]

    results = []
    for ep, conc, count in scenarios:
        print(f"Testing {ep} (conc={conc}, reqs={count})...", end=" ", flush=True)
        res = benchmark_endpoint(ep, conc, count, token=token)
        results.append(res)
        print(
            f"Done in {res['total_time_s']}s (RPS: {res['rps']}, "
            f"p50: {res['p50_ms']}ms, p95: {res['p95_ms']}ms)",
            flush=True,
        )

    print("\n" + "=" * 75, flush=True)
    header = (
        f"{'Endpoint':<26} {'Conc':<6} {'RPS':<8} "
        f"{'p50(ms)':<10} {'p95(ms)':<10} {'p99(ms)':<10} {'Status':<10}"
    )
    print(header, flush=True)
    print("-" * 75, flush=True)
    for r in results:
        status_summary = ", ".join(f"{k}:{v}" for k, v in r["statuses"].items())
        print(
            f"{r['endpoint']:<26} {r['concurrency']:<6} {r['rps']:<8} "
            f"{r['p50_ms']:<10} {r['p95_ms']:<10} {r['p99_ms']:<10} {status_summary}",
            flush=True,
        )
    print("=" * 75, flush=True)


if __name__ == "__main__":
    main()
