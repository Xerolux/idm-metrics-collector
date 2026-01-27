import schedule
import time
import logging
import os
from scripts.train_model import train_model

# Setup Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("telemetry-trainer")

# Configuration
MODEL_DIR = os.environ.get("MODEL_DIR", "/app/models")
TARGET_MODELS = os.environ.get("TARGET_MODELS", "AERO_SLM").split(",")
TRAINING_TIME = os.environ.get("TRAINING_TIME", "03:00")  # 3 AM default


def run_training_job():
    logger.info("Starting scheduled model training...")

    for model_name in TARGET_MODELS:
        model_name = model_name.strip()
        if not model_name:
            continue

        logger.info(f"Training model: {model_name}")

        safe_model_name = model_name.replace(" ", "_").replace("/", "_")
        output_file = os.path.join(MODEL_DIR, f"{safe_model_name}.pkl")

        try:
            success = train_model(model_name=model_name, output_file=output_file)

            if success:
                logger.info(f"Successfully trained {model_name}")

                # Encrypt/Sign the model (using export_model script logic would be better but simple call here)
                # We need to call export_model from here or duplicate logic.
                # Let's import export_model function if available or run via subprocess?
                # Importing is better.
                try:
                    from scripts.export_model import export_model

                    export_model(output_file, MODEL_DIR)
                    # Clean up raw pickle
                    if os.path.exists(output_file):
                        os.remove(output_file)
                except Exception as e:
                    logger.error(f"Failed to export/encrypt model {model_name}: {e}")
            else:
                logger.warning(f"Training failed or insufficient data for {model_name}")

        except Exception as e:
            logger.error(f"Exception during training {model_name}: {e}")

    logger.info("Training job finished.")


def main():
    logger.info("Telemetry Training Scheduler started")
    logger.info(f"Target models: {TARGET_MODELS}")
    logger.info(f"Schedule: Daily at {TRAINING_TIME}")

    # Schedule the job
    schedule.every().day.at(TRAINING_TIME).do(run_training_job)

    # Run once on startup if requested (e.g. for testing)
    if os.environ.get("RUN_ON_STARTUP", "false").lower() == "true":
        logger.info("Running initial training on startup...")
        run_training_job()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
