"""
Background task system for sending email notifications asynchronously.
"""
import threading
import queue
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Callable
import time

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.worker_thread = None
        self.is_running = False
        self.stats = {
            'tasks_total': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'started_at': None
        }

    def start(self):
        """Start the background worker thread."""
        if not self.is_running:
            self.is_running = True
            self.stats['started_at'] = datetime.now(timezone.utc)
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info("Background task manager started")

    def stop(self):
        """Stop the background worker thread."""
        self.is_running = False
        if self.worker_thread:
            # Add a stop signal to the queue
            self.task_queue.put(None)
            self.worker_thread.join(timeout=5)
            logger.info("Background task manager stopped")

    def add_task(self, task_func: Callable, *args, **kwargs):
        """Add a task to the background queue."""
        try:
            task = {
                'func': task_func,
                'args': args,
                'kwargs': kwargs,
                'created_at': datetime.now(timezone.utc),
                'task_id': f"{task_func.__name__}_{int(time.time() * 1000)}"
            }

            self.task_queue.put(task)
            self.stats['tasks_total'] += 1
            logger.debug(f"Added task {task['task_id']} to queue")

        except Exception as e:
            logger.error(f"Error adding task to queue: {str(e)}")

    def _worker_loop(self):
        """Main worker loop that processes tasks from the queue."""
        logger.info("Background task worker started")

        while self.is_running:
            try:
                # Get task with timeout to check if we should stop
                task = self.task_queue.get(timeout=1)

                # Check for stop signal
                if task is None:
                    break

                # Execute the task
                self._execute_task(task)

            except queue.Empty:
                # No task available, continue loop
                continue
            except Exception as e:
                logger.error(f"Error in worker loop: {str(e)}")

        logger.info("Background task worker stopped")

    def _execute_task(self, task: Dict[str, Any]):
        """Execute a single task."""
        task_id = task.get('task_id', 'unknown')

        try:
            logger.debug(f"Executing task {task_id}")

            # Execute the task function
            result = task['func'](*task['args'], **task['kwargs'])

            self.stats['tasks_completed'] += 1
            logger.debug(f"Task {task_id} completed successfully")

            return result

        except Exception as e:
            self.stats['tasks_failed'] += 1
            logger.error(f"Task {task_id} failed: {str(e)}")

        finally:
            self.task_queue.task_done()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about task processing."""
        return {
            **self.stats,
            'queue_size': self.task_queue.qsize(),
            'is_running': self.is_running,
            'worker_alive': self.worker_thread.is_alive() if self.worker_thread else False
        }


# Global task manager instance
task_manager = BackgroundTaskManager()


def send_email_async(email_service, method_name: str, *args, **kwargs):
    """Helper function to send emails asynchronously."""
    def email_task():
        try:
            method = getattr(email_service, method_name)
            return method(*args, **kwargs)
        except Exception as e:
            logger.error(f"Async email task failed: {str(e)}")
            return False

    task_manager.add_task(email_task)


def init_background_tasks(app):
    """Initialize background task system with Flask app."""

    # Start task manager when app starts
    task_manager.start()

    # Register cleanup on app teardown
    import atexit
    atexit.register(task_manager.stop)

    logger.info("Background task system initialized")


# Convenience functions for common email tasks
def send_grade_notification_async(student_id: int, subject_id: int, semester: str, academic_year: str):
    """Send grade release notification asynchronously."""
    from app.services.email_notification_service import email_service

    def notification_task():
        return email_service.notify_grade_release(
            student_id, subject_id, semester, academic_year
        )

    task_manager.add_task(notification_task)


def send_bulk_grade_notifications_async(subject_id: int, semester: str, academic_year: str, released_by_user):
    """Send bulk grade release notifications asynchronously."""
    from app.services.email_notification_service import email_service

    def bulk_notification_task():
        return email_service.notify_bulk_grade_release(
            subject_id, semester, academic_year, released_by_user
        )

    task_manager.add_task(bulk_notification_task)