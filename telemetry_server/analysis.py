import os
import logging
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger("telemetry-analysis")

VM_QUERY_URL = os.environ.get("VM_QUERY_URL", "http://victoriametrics:8428/api/v1/query")

def get_community_averages(model_name: str, metrics: List[str], window: str = "24h") -> Dict[str, Any]:
    """
    Fetch aggregated community statistics for a specific heat pump model.

    Args:
        model_name: The heat pump model name (e.g., 'AERO_SLM').
        metrics: List of metric suffixes to query (e.g., ['cop_current', 'temp_outdoor']).
        window: Time window for aggregation (default: '24h').

    Returns:
        Dict containing averages, min, max, and sample size.
    """
    safe_model = model_name.replace(" ", "_")
    results = {
        "model": model_name,
        "window": window,
        "metrics": {},
        "sample_size": 0
    }

    try:
        # 1. Get sample size (approximate number of active installations for this model in window)
        # count(count_over_time(heatpump_metrics{model="AERO_SLM"}[24h]))
        count_query = f'count(count_over_time(heatpump_metrics{{model="{safe_model}"}}[{window}]))'

        response = requests.get(VM_QUERY_URL, params={"query": count_query}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                results["sample_size"] = int(data["data"]["result"][0]["value"][1])

        # If no data, return early
        if results["sample_size"] == 0:
            return results

        # 2. Get stats for each metric
        for metric in metrics:
            metric_name = f"heatpump_metrics_{metric}" if not metric.startswith("heatpump_metrics_") else metric
            clean_name = metric.replace("heatpump_metrics_", "")

            # Construct queries for Avg, Min, Max
            # Avg: avg(avg_over_time(...)) - average of averages to handle different sampling rates equally?
            # Or just avg_over_time of the aggregate?
            # Ideally: avg(last_over_time(...)) across series?
            # Let's use simple aggregation: avg(metric{model="..."}) returns instantaneous avg across fleet.
            # But we want average over the window.
            # avg_over_time(avg(metric{model="..."})[24h]) ?
            # Simpler: avg(avg_over_time(metric{model="..."}[24h]))

            queries = {
                "avg": f'avg(avg_over_time({metric_name}{{model="{safe_model}"}}[{window}]))',
                "min": f'min(min_over_time({metric_name}{{model="{safe_model}"}}[{window}]))',
                "max": f'max(max_over_time({metric_name}{{model="{safe_model}"}}[{window}]))'
            }

            metric_stats = {}
            for stat_type, query in queries.items():
                try:
                    res = requests.get(VM_QUERY_URL, params={"query": query}, timeout=5)
                    if res.status_code == 200:
                        d = res.json()
                        if d.get("status") == "success" and d["data"]["result"]:
                            val = float(d["data"]["result"][0]["value"][1])
                            metric_stats[stat_type] = round(val, 2)
                except Exception as e:
                    logger.warning(f"Failed to fetch {stat_type} for {metric}: {e}")

            if metric_stats:
                results["metrics"][clean_name] = metric_stats

    except Exception as e:
        logger.error(f"Error analyzing community data for {model_name}: {e}")
        return {"error": str(e)}

    return results
