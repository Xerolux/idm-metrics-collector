from dataclasses import dataclass, field
from typing import List
import os


def _parse_list(value: str, item_type: type = str) -> List:
    if not value or not value.strip():
        return []
    return [item_type(x.strip()) for x in value.split(",") if x.strip()]


@dataclass
class MLConfig:
    metrics_url: str = field(
        default_factory=lambda: os.environ.get(
            "METRICS_URL", "http://victoriametrics:8428"
        )
    )
    measurement_name: str = field(
        default_factory=lambda: os.environ.get("MEASUREMENT_NAME", "idm_heatpump")
    )
    update_interval: int = field(
        default_factory=lambda: int(os.environ.get("UPDATE_INTERVAL", "30"))
    )

    anomaly_threshold: float = field(
        default_factory=lambda: float(os.environ.get("ANOMALY_THRESHOLD", "0.85"))
    )
    min_data_ratio: float = field(
        default_factory=lambda: float(os.environ.get("MIN_DATA_RATIO", "0.1"))
    )
    model_save_interval: int = field(
        default_factory=lambda: int(os.environ.get("MODEL_SAVE_INTERVAL", "300"))
    )
    model_path: str = field(
        default_factory=lambda: os.environ.get(
            "MODEL_PATH", "/app/data/model_state.pkl"
        )
    )

    enable_alerts: bool = field(
        default_factory=lambda: os.environ.get("ENABLE_ALERTS", "true").lower()
        == "true"
    )
    alert_cooldown: int = field(
        default_factory=lambda: int(os.environ.get("ALERT_COOLDOWN", "3600"))
    )
    warmup_updates: int = field(
        default_factory=lambda: int(os.environ.get("WARMUP_UPDATES", "200"))
    )
    alarm_consecutive_hits: int = field(
        default_factory=lambda: int(os.environ.get("ALARM_CONSECUTIVE_HITS", "5"))
    )
    idm_logger_url: str = field(
        default_factory=lambda: os.environ.get(
            "IDM_LOGGER_URL", "http://idm-logger:5000"
        )
    )
    internal_api_key: str = field(
        default_factory=lambda: os.environ.get("INTERNAL_API_KEY", "")
    )

    ae_hidden_dim: int = field(
        default_factory=lambda: int(os.environ.get("AE_HIDDEN_DIM", "32"))
    )
    ae_latent_dim: int = field(
        default_factory=lambda: int(os.environ.get("AE_LATENT_DIM", "8"))
    )
    ae_learning_rate: float = field(
        default_factory=lambda: float(os.environ.get("AE_LEARNING_RATE", "0.001"))
    )
    ae_train_steps: int = field(
        default_factory=lambda: int(os.environ.get("AE_TRAIN_STEPS", "3"))
    )
    ae_ema_alpha: float = field(
        default_factory=lambda: float(os.environ.get("AE_EMA_ALPHA", "0.02"))
    )

    retry_base_delay: float = field(
        default_factory=lambda: float(os.environ.get("RETRY_BASE_DELAY", "1.0"))
    )
    retry_max_delay: float = field(
        default_factory=lambda: float(os.environ.get("RETRY_MAX_DELAY", "60.0"))
    )
    retry_multiplier: float = field(
        default_factory=lambda: float(os.environ.get("RETRY_MULTIPLIER", "2.0"))
    )
    retry_max_attempts: int = field(
        default_factory=lambda: int(os.environ.get("RETRY_MAX_ATTEMPTS", "3"))
    )

    ml_circuits: List[str] = field(
        default_factory=lambda: _parse_list(os.environ.get("ML_CIRCUITS", "A"))
    )
    ml_zones: List[int] = field(
        default_factory=lambda: _parse_list(os.environ.get("ML_ZONES", ""), int)
    )

    modes: List[str] = field(
        default_factory=lambda: ["heating", "cooling", "water", "standby"]
    )

    def update_threshold(self, new_threshold: float) -> bool:
        if abs(new_threshold - self.anomaly_threshold) > 0.001:
            self.anomaly_threshold = new_threshold
            return True
        return False


config = MLConfig()
