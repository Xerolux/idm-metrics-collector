import requests

# Global session for connection pooling
# This significantly reduces overhead by reusing TCP connections
# for repeated API calls to the same host (like VictoriaMetrics or Grafana).
http_client = requests.Session()
