# Xerolux 2026
import os
import asyncio
from typing import List, Dict, Any, Optional
import httpx
import structlog

logger = structlog.get_logger("telemetry-analysis")

VM_QUERY_URL = os.environ.get(
    "VM_QUERY_URL", "http://victoriametrics:8428/api/v1/query"
)
VM_TIMEOUT = int(os.environ.get("VM_TIMEOUT", "5"))  # Configurable timeout in seconds


async def get_community_averages(
    model_name: str,
    metrics: List[str],
    window: str = "24h",
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """
    Fetch aggregated community statistics for a specific heat pump model.

    Args:
        model_name: The heat pump model name (e.g., 'AERO_SLM').
        metrics: List of metric suffixes to query (e.g., ['cop_current', 'temp_outdoor']).
        window: Time window for aggregation (default: '24h').
        client: Optional HTTPX client for async requests.

    Returns:
        Dict containing averages, min, max, and sample size.
    """
    safe_model = model_name.replace(" ", "_")
    results = {"model": model_name, "window": window, "metrics": {}, "sample_size": 0}

    # Ensure we have a client. If not provided, create a temporary one (slower).
    local_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=VM_TIMEOUT)
        local_client = True

    try:
        # 1. Get sample size (approximate number of active installations for this model in window)
        count_query = f'count(count by (installation_id) (count_over_time({{__name__=~"heatpump_metrics_.*", model="{safe_model}"}}[{window}])))'

        response = await client.get(
            VM_QUERY_URL, params={"query": count_query}, timeout=VM_TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            if (
                data.get("status") == "success"
                and data["data"]["result"]
                and data["data"]["result"][0].get("value")
                and len(data["data"]["result"][0]["value"]) > 1
            ):
                results["sample_size"] = int(data["data"]["result"][0]["value"][1])

        # If no data, return early
        if results["sample_size"] == 0:
            return results

        # 2. Get stats for each metric concurrently
        async def fetch_metric_stat(metric: str, stat_type: str, query: str):
            try:
                res = await client.get(
                    VM_QUERY_URL, params={"query": query}, timeout=VM_TIMEOUT
                )
                if res.status_code == 200:
                    d = res.json()
                    if (
                        d.get("status") == "success"
                        and d["data"]["result"]
                        and d["data"]["result"][0].get("value")
                        and len(d["data"]["result"][0]["value"]) > 1
                    ):
                        val = float(d["data"]["result"][0]["value"][1])
                        return metric, stat_type, round(val, 2)
            except Exception as e:
                logger.warning(
                    "metric_fetch_failed",
                    metric=metric,
                    stat=stat_type,
                    error=str(e),
                )
            return metric, stat_type, None

        tasks = []
        for metric in metrics:
            metric_name = (
                f"heatpump_metrics_{metric}"
                if not metric.startswith("heatpump_metrics_")
                else metric
            )
            clean_name = metric.replace("heatpump_metrics_", "")

            # Prepare result structure if not exists
            if clean_name not in results["metrics"]:
                results["metrics"][clean_name] = {}

            queries = {
                "avg": f'avg(avg_over_time({metric_name}{{model="{safe_model}"}}[{window}]))',
                "min": f'min(min_over_time({metric_name}{{model="{safe_model}"}}[{window}]))',
                "max": f'max(max_over_time({metric_name}{{model="{safe_model}"}}[{window}]))',
            }

            for stat_type, query in queries.items():
                tasks.append(fetch_metric_stat(clean_name, stat_type, query))

        # Run all queries concurrently
        if tasks:
            query_results = await asyncio.gather(*tasks)

            # Process results
            for metric, stat_type, val in query_results:
                if val is not None:
                    results["metrics"][metric][stat_type] = val

        # Cleanup empty metrics
        results["metrics"] = {k: v for k, v in results["metrics"].items() if v}

    except Exception as e:
        logger.error("community_analysis_error", model=model_name, error=str(e))
        return {"error": "community_analysis_failed"}
    finally:
        if local_client:
            await client.aclose()

    return results
