# Xerolux 2026
"""
Training Queue - Async Model Training Pipeline

Manages asynchronous model training tasks without blocking the request handler.
Lightweight implementation using asyncio and JSON-based task storage.

Features:
- Async training execution (no blocking)
- Task status tracking (queued, running, completed, failed)
- Progress tracking with real-time updates
- Task history with retention policy
- No Redis/Celery required (self-contained)
"""

import os
import json
import asyncio
import uuid
import time
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

logger = structlog.get_logger()

# Task storage location
TASK_STORAGE_DIR = os.environ.get("TASK_STORAGE_DIR", "/var/lib/telemetry/tasks")
TASK_FILE = os.path.join(TASK_STORAGE_DIR, "training_tasks.json")

# Ensure storage directory exists
Path(TASK_STORAGE_DIR).mkdir(parents=True, exist_ok=True)


class TaskStatus(str, Enum):
    """Training task status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TrainingTask:
    """Training task metadata."""
    task_id: str
    status: TaskStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    triggered_by: Optional[str] = None
    progress: int = 0  # 0-100%
    message: str = ""
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    returncode: Optional[int] = None
    duration_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["status"] = self.status.value  # Convert enum to string
        return result


class TrainingQueue:
    """Manages async training tasks."""

    def __init__(self):
        self.tasks: Dict[str, TrainingTask] = {}
        self.current_task: Optional[asyncio.Task] = None
        self.current_task_id: Optional[str] = None
        self._load_tasks()

    def _load_tasks(self):
        """Load tasks from storage."""
        try:
            if os.path.exists(TASK_FILE):
                with open(TASK_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for task_id, task_data in data.items():
                        # Convert status string back to enum
                        task_data["status"] = TaskStatus(task_data["status"])
                        self.tasks[task_id] = TrainingTask(**task_data)
                logger.info("training_tasks_loaded", count=len(self.tasks))
            else:
                logger.info("no_task_file_found", initializing=True)
                self.tasks = {}
        except Exception as e:
            logger.error("task_load_failed", error=str(e))
            self.tasks = {}

    def _save_tasks(self):
        """Save tasks to storage."""
        try:
            # Atomic write with temp file
            temp_file = TASK_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                data = {task_id: task.to_dict() for task_id, task in self.tasks.items()}
                json.dump(data, f, indent=2)
            os.replace(temp_file, TASK_FILE)
            logger.debug("training_tasks_saved", count=len(self.tasks))
        except Exception as e:
            logger.error("task_save_failed", error=str(e))

    async def enqueue_training(
        self,
        triggered_by: str,
        script_path: str = "/app/scripts/train_models.py"
    ) -> str:
        """
        Enqueue a new training task.

        Args:
            triggered_by: Admin ID who triggered the training
            script_path: Path to training script

        Returns:
            Task ID (UUID)
        """
        # Check if training is already running
        if self.current_task and not self.current_task.done():
            raise ValueError("Training is already in progress. Please wait for it to complete.")

        # Generate task ID
        task_id = str(uuid.uuid4())

        # Create task
        task = TrainingTask(
            task_id=task_id,
            status=TaskStatus.QUEUED,
            created_at=datetime.now(timezone.utc).isoformat(),
            triggered_by=triggered_by,
            message="Training queued",
        )

        self.tasks[task_id] = task
        self._save_tasks()

        logger.info(
            "training_task_queued",
            task_id=task_id,
            triggered_by=triggered_by
        )

        # Start training in background
        self.current_task_id = task_id
        self.current_task = asyncio.create_task(
            self._run_training(task_id, script_path)
        )

        return task_id

    async def _run_training(self, task_id: str, script_path: str):
        """
        Run training script asynchronously.

        Args:
            task_id: Task ID
            script_path: Path to training script
        """
        task = self.tasks[task_id]

        try:
            # Update status to running
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc).isoformat()
            task.message = "Training in progress"
            task.progress = 10
            self._save_tasks()

            logger.info("training_started", task_id=task_id)

            # Run training script asynchronously
            start_time = time.time()
            process = await asyncio.create_subprocess_exec(
                "python3",
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/app"
            )

            # Update progress periodically
            progress_task = asyncio.create_task(
                self._update_progress(task_id, start_time)
            )

            # Wait for process to complete
            stdout, stderr = await process.communicate()

            # Cancel progress updater
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass

            # Calculate duration
            duration = time.time() - start_time

            # Update task with results
            task.returncode = process.returncode
            task.stdout = stdout.decode('utf-8') if stdout else None
            task.stderr = stderr.decode('utf-8') if stderr else None
            task.duration_seconds = duration
            task.completed_at = datetime.now(timezone.utc).isoformat()

            if process.returncode == 0:
                task.status = TaskStatus.COMPLETED
                task.progress = 100
                task.message = f"Training completed successfully in {duration:.1f}s"
                logger.info(
                    "training_completed",
                    task_id=task_id,
                    duration=duration
                )
            else:
                task.status = TaskStatus.FAILED
                task.message = f"Training failed with exit code {process.returncode}"
                logger.error(
                    "training_failed",
                    task_id=task_id,
                    returncode=process.returncode,
                    stderr_preview=stderr[:500] if stderr else None
                )

        except asyncio.CancelledError:
            # Task was cancelled
            task.status = TaskStatus.CANCELLED
            task.message = "Training was cancelled"
            task.completed_at = datetime.now(timezone.utc).isoformat()
            logger.warning("training_cancelled", task_id=task_id)
            raise

        except Exception as e:
            # Unexpected error
            task.status = TaskStatus.FAILED
            task.message = f"Training failed: {str(e)}"
            task.completed_at = datetime.now(timezone.utc).isoformat()
            logger.error(
                "training_error",
                task_id=task_id,
                error=str(e)
            )

        finally:
            # Always save final state
            self._save_tasks()
            self.current_task_id = None

    async def _update_progress(self, task_id: str, start_time: float):
        """
        Update progress periodically during training.

        Args:
            task_id: Task ID
            start_time: Training start timestamp
        """
        try:
            while True:
                await asyncio.sleep(5)  # Update every 5 seconds

                task = self.tasks.get(task_id)
                if not task or task.status != TaskStatus.RUNNING:
                    break

                # Estimate progress based on time (assume 5 minutes max)
                elapsed = time.time() - start_time
                estimated_progress = min(90, int((elapsed / 300) * 90) + 10)

                task.progress = estimated_progress
                self._save_tasks()

        except asyncio.CancelledError:
            pass

    def get_task(self, task_id: str) -> Optional[TrainingTask]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status (sanitized for API response)."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        result = task.to_dict()

        # Don't include full stdout/stderr in status response (too large)
        # Only include if task failed and stderr is small
        if task.status != TaskStatus.FAILED or (task.stderr and len(task.stderr) > 1000):
            result["stdout"] = None
            result["stderr"] = None

        return result

    def get_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent training tasks.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            List of tasks (most recent first)
        """
        tasks_list = list(self.tasks.values())
        tasks_list.sort(key=lambda t: t.created_at, reverse=True)

        result = []
        for task in tasks_list[:limit]:
            task_dict = task.to_dict()
            # Don't include stdout/stderr in list view
            task_dict["stdout"] = None
            task_dict["stderr"] = None
            result.append(task_dict)

        return result

    def get_current_task(self) -> Optional[Dict[str, Any]]:
        """Get currently running task."""
        if self.current_task_id:
            return self.get_task_status(self.current_task_id)
        return None

    async def cancel_training(self, task_id: str) -> bool:
        """
        Cancel a training task.

        Args:
            task_id: Task ID

        Returns:
            True if task was cancelled, False if not found or not running
        """
        if task_id != self.current_task_id:
            logger.warning("cancel_training_failed", reason="not_current_task", task_id=task_id)
            return False

        if not self.current_task or self.current_task.done():
            logger.warning("cancel_training_failed", reason="task_not_running", task_id=task_id)
            return False

        # Cancel the task
        self.current_task.cancel()
        logger.info("training_cancellation_requested", task_id=task_id)
        return True

    def cleanup_old_tasks(self, max_age_days: int = 30):
        """
        Clean up old completed/failed tasks.

        Args:
            max_age_days: Maximum age of tasks to keep (default 30 days)
        """
        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        tasks_to_remove = []

        for task_id, task in self.tasks.items():
            # Don't remove current/running tasks
            if task.status in (TaskStatus.QUEUED, TaskStatus.RUNNING):
                continue

            # Parse created_at timestamp
            try:
                created_timestamp = datetime.fromisoformat(task.created_at).timestamp()
                if created_timestamp < cutoff_time:
                    tasks_to_remove.append(task_id)
            except Exception as e:
                logger.error("task_cleanup_parse_error", task_id=task_id, error=str(e))

        # Remove old tasks
        for task_id in tasks_to_remove:
            del self.tasks[task_id]

        if tasks_to_remove:
            self._save_tasks()
            logger.info("old_tasks_cleaned_up", count=len(tasks_to_remove))


# Global training queue instance
training_queue = TrainingQueue()
