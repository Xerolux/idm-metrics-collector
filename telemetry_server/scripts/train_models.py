# Xerolux 2026
"""
Batch training entrypoint for telemetry admin operations.

Supports:
- training all configured models (TARGET_MODELS)
- training a specific model
- training from one installation only
"""

import argparse
import os
import sys
from pathlib import Path

from train_model import train_model


def _parse_models(target_model: str | None) -> list[str]:
    if target_model:
        return [target_model.strip()]

    env_models = os.environ.get("TARGET_MODELS", "")
    return [m.strip() for m in env_models.split(",") if m.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Train one or more telemetry models")
    parser.add_argument("--target-model", type=str, default=None)
    parser.add_argument("--target-installation-id", type=str, default=None)
    parser.add_argument("--min-points", type=int, default=int(os.environ.get("MIN_POINTS", "50000")))
    parser.add_argument(
        "--min-installations",
        type=int,
        default=int(os.environ.get("MIN_INSTALLATIONS_FOR_MODEL", "5")),
    )
    parser.add_argument("--lookback-days", type=int, default=30)
    parser.add_argument("--model-dir", type=str, default=os.environ.get("MODEL_DIR", "/app/models"))
    args = parser.parse_args()

    models = _parse_models(args.target_model)
    if not models:
        print("No models configured. Set TARGET_MODELS or provide --target-model.", file=sys.stderr)
        return 1

    Path(args.model_dir).mkdir(parents=True, exist_ok=True)

    # If we train from exactly one installation, we explicitly allow single-installation training.
    effective_min_installations = (
        1 if args.target_installation_id else max(1, int(args.min_installations))
    )

    all_ok = True
    for model_name in models:
        safe_name = model_name.replace(" ", "_").replace("/", "_")
        output_file = str(Path(args.model_dir) / f"{safe_name}.pkl")
        ok = train_model(
            model_name=model_name,
            output_file=output_file,
            min_points=max(1, int(args.min_points)),
            min_installations=effective_min_installations,
            lookback_days=max(1, int(args.lookback_days)),
            training_installation_id=args.target_installation_id,
        )
        all_ok = all_ok and ok

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
