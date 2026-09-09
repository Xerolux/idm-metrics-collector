# Xerolux 2026
"""
Template Variables for Dashboards

Allows users to define variables that can be used in queries
(e.g., $circuit, $period, $sensor_id)

Types:
- query: Values fetched from a metric query
- custom: Predefined list of values
- interval: Time intervals (1h, 6h, 24h, 7d, etc.)
"""

from typing import List, Dict, Optional, Any
import requests
import logging
import re

logger = logging.getLogger(__name__)


class Variable:
    """Represents a template variable"""

    # Variable types
    TYPE_QUERY = "query"
    TYPE_CUSTOM = "custom"
    TYPE_INTERVAL = "interval"

    def __init__(
        self,
        var_id: str,
        name: str,
        var_type: str,
        query: Optional[str] = None,
        values: Optional[List[str]] = None,
        default: Optional[str] = None,
        multi: bool = False,
        regex: Optional[str] = None,
    ):
        self.id = var_id
        self.name = name  # Display name (e.g., "Heizkreis")
        self.type = var_type  # 'query', 'custom', 'interval'
        self.query = query  # For type=query: metric query to fetch values
        self.values = values or []  # For type=custom: predefined values
        self.default = default  # Default selected value
        self.multi = multi  # Allow multiple selections
        self.regex = regex  # Regex to filter query results

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "query": self.query,
            "values": self.values,
            "default": self.default,
            "multi": self.multi,
            "regex": self.regex,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Variable":
        """Create from dictionary"""
        return cls(
            var_id=data.get("id"),
            name=data.get("name"),
            var_type=data.get("type"),
            query=data.get("query"),
            values=data.get("values"),
            default=data.get("default"),
            multi=data.get("multi", False),
            regex=data.get("regex"),
        )

    def get_values(self, metrics_url: str) -> List[str]:
        """Get possible values for this variable"""
        if self.type == self.TYPE_QUERY:
            return self._fetch_query_values(metrics_url)
        elif self.type == self.TYPE_INTERVAL:
            return self._get_interval_values()
        elif self.type == self.TYPE_CUSTOM:
            return self.values
        return []

    def _fetch_query_values(self, metrics_url: str) -> List[str]:
        """Fetch values from metric query"""
        if not self.query:
            return []

        try:
            # Query for unique label values
            # This is a simplified version - in production you'd use proper PromQL label_values query
            query_url = f"{metrics_url}/api/v1/query"
            params = {"query": self.query}

            response = requests.get(query_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "success" and data.get("data"):
                result = data["data"].get("result", [])
                # Extract unique values from the result
                values = set()
                for item in result:
                    if "metric" in item:
                        # For label values queries, the metric object contains the labels
                        values.update(item["metric"].values())

                return sorted(list(values))
        except Exception as e:
            logger.warning(f"Failed to fetch variable values: {e}")

        return []

    def _get_interval_values(self) -> List[str]:
        """Get predefined interval values"""
        return ["5m", "15m", "30m", "1h", "6h", "12h", "24h", "7d", "30d"]


class VariableManager:
    """Manages template variables for dashboards"""

    # Predefined interval values
    INTERVAL_VALUES = ["5m", "15m", "30m", "1h", "6h", "12h", "24h", "7d", "30d"]

    def __init__(self, config):
        self.config = config

    def get_all_variables(self) -> List[Variable]:
        """Get all variables"""
        data = self.config.data.get("variables", [])
        return [Variable.from_dict(v) for v in data]

    def get_variable(self, variable_id: str) -> Optional[Variable]:
        """Get a specific variable by ID"""
        variables = self.get_all_variables()
        for var in variables:
            if var.id == variable_id:
                return var
        return None

    def add_variable(
        self,
        var_id: str,
        name: str,
        var_type: str,
        query: str = None,
        values: List[str] = None,
        default: str = None,
        multi: bool = False,
        regex: str = None,
    ) -> Variable:
        """Add a new variable"""
        variable = Variable(
            var_id=var_id,
            name=name,
            var_type=var_type,
            query=query,
            values=values,
            default=default,
            multi=multi,
            regex=regex,
        )

        if "variables" not in self.config.data:
            self.config.data["variables"] = []

        self.config.data["variables"].append(variable.to_dict())
        self.config.save()

        return variable

    def update_variable(self, variable_id: str, **kwargs) -> Optional[Variable]:
        """Update an existing variable"""
        variables = self.config.data.get("variables", [])

        for i, var in enumerate(variables):
            if var["id"] == variable_id:
                for key, value in kwargs.items():
                    if key in var:
                        var[key] = value

                self.config.data["variables"][i] = var
                self.config.save()
                return Variable.from_dict(var)

        return None

    def delete_variable(self, variable_id: str) -> bool:
        """Delete a variable"""
        variables = self.config.data.get("variables", [])

        for i, var in enumerate(variables):
            if var["id"] == variable_id:
                del self.config.data["variables"][i]
                self.config.save()
                return True

        return False

    def get_variable_values(self, variable_id: str, metrics_url: str) -> Dict[str, Any]:
        """Get values for a variable (for dropdown population)"""
        variable = self.get_variable(variable_id)
        if not variable:
            return {"error": "Variable not found"}

        values = variable.get_values(metrics_url)
        return {
            "id": variable_id,
            "name": variable.name,
            "type": variable.type,
            "values": values,
            "default": variable.default,
            "multi": variable.multi,
        }

    def get_all_variable_values(self, metrics_url: str) -> List[Dict[str, Any]]:
        """Get values for all variables"""
        variables = self.get_all_variables()
        result = []

        for var in variables:
            values = var.get_values(metrics_url)
            result.append(
                {
                    "id": var.id,
                    "name": var.name,
                    "type": var.type,
                    "values": values,
                    "default": var.default,
                    "multi": var.multi,
                }
            )

        return result

    def substitute_variables(self, query: str, variable_values: Dict[str, Any]) -> str:
        """
        Substitute variables in a query string.

        Supports:
        - ${var}
        - $var
        - {var} (Grafana style)
        """
        if not query or not variable_values:
            return query

        # Combined regex for all formats
        # Group 1: ${var} -> var is Group 1. Max 100 chars to prevent ReDoS.
        # Group 2: $var   -> var is Group 2
        # Group 3: {var}  -> var is Group 3
        # We limit the length of the variable name to avoid performance issues on malicious inputs
        pattern = r"\$\{([^}]{1,100})\}|\$([a-zA-Z_]\w{0,99})|\{([a-zA-Z_]\w{0,99})\}"

        def replacer(match):
            # Find which group matched
            var_name = match.group(1) or match.group(2) or match.group(3)

            # Special case for {var} which might be part of PromQL like {job="foo"}
            # The regex {([a-zA-Z_]\w*)} might match {job} but PromQL uses {job=".."}
            # If the variable exists in our map, we replace it.
            # If not, we keep the original text to avoid breaking PromQL queries.

            if var_name and var_name in variable_values:
                return str(variable_values[var_name])

            return match.group(0)

        # Pre-compiled patterns are cached by re module, but explicit is better
        return re.sub(pattern, replacer, query)
