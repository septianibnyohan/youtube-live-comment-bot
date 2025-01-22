"""
Scheduler module for YouTube Live Comment Bot.

This module handles task scheduling and timing management.
"""

import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timedelta
import threading
import time
from queue import PriorityQueue

from . import SchedulerError

logger = logging.getLogger(__name__)


class Scheduler:
    """Task scheduler class."""

    def __init__(self):
        """Initialize scheduler."""
        self.tasks = PriorityQueue()
        self.scheduled_tasks: Dict[str, dict] = {}
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def schedule(self,
                 schedule_time: datetime,
                 callback: Callable,
                 task_id: str,
                 *args,
                 **kwargs) -> None:
        """Schedule a task for execution.

        Args:
            schedule_time: When to execute the task.
            callback: Function to call.
            task_id: Unique task identifier.
            *args: Positional arguments for callback.
            **kwargs: Keyword arguments for callback.

        Raises:
            SchedulerError: If scheduling fails.
        """
        try:
            if schedule_time < datetime.now():
                raise SchedulerError("Cannot schedule task in the past")

            task = {
                'time': schedule_time,
                'callback': callback,
                'args': args,
                'kwargs': kwargs,
                'id': task_id
            }

            with self._lock:
                self.tasks.put((schedule_time.timestamp(), task))
                self.scheduled_tasks[task_id] = task

            logger.debug(f"Scheduled task {task_id} for {schedule_time}")

            if not self._running:
                self.start()

        except Exception as e:
            raise SchedulerError(f"Failed to schedule task: {e}")

    def schedule_after(self,
                       delay: int,
                       callback: Callable,
                       task_id: str,
                       *args,
                       **kwargs) -> None:
        """Schedule a task to run after a delay.

        Args:
            delay: Delay in seconds.
            callback: Function to call.
            task_id: Unique task identifier.
            *args: Positional arguments for callback.
            **kwargs: Keyword arguments for callback.
        """
        schedule_time = datetime.now() + timedelta(seconds=delay)
        self.schedule(schedule_time, callback, task_id, *args, **kwargs)

    def schedule_interval(self,
                          interval: int,
                          callback: Callable,
                          task_id: str,
                          *args,
                          **kwargs) -> None:
        """Schedule a task to run at regular intervals.

        Args:
            interval: Interval in seconds.
            callback: Function to call.
            task_id: Unique task identifier.
            *args: Positional arguments for callback.
            **kwargs: Keyword arguments for callback.
        """

        def wrapped_callback(*args, **kwargs):
            try:
                callback(*args, **kwargs)
            finally:
                # Reschedule next run
                next_time = datetime.now() + timedelta(seconds=interval)
                self.schedule(next_time, wrapped_callback, task_id, *args, **kwargs)

        # Schedule first run
        self.schedule_after(interval, wrapped_callback, task_id, *args, **kwargs)

    def cancel(self, task_id: str) -> None:
        """Cancel a scheduled task.

        Args:
            task_id: Task identifier.

        Raises:
            SchedulerError: If task cancellation fails.
        """
        try:
            with self._lock:
                if task_id in self.scheduled_tasks:
                    # Remove from scheduled tasks
                    del self.scheduled_tasks[task_id]
                    logger.debug(f"Cancelled task {task_id}")
                else:
                    logger.warning(f"Task {task_id} not found for cancellation")

        except Exception as e:
            raise SchedulerError(f"Failed to cancel task: {e}")

    def start(self) -> None:
        """Start the scheduler."""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run)
            self._thread.daemon = True
            self._thread.start()
            logger.debug("Scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if self._running:
            self._running = False
            if self._thread:
                self._thread.join()
            logger.debug("Scheduler stopped")

    def _run(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                # Get next task
                if self.tasks.empty():
                    time.sleep(1)
                    continue

                # Peek at next task
                timestamp, task = self.tasks.queue[0]
                now = datetime.now().timestamp()

                if timestamp <= now:
                    # Remove task from queue
                    self.tasks.get()

                    # Execute task
                    try:
                        task['callback'](*task['args'], **task['kwargs'])
                    except Exception as e:
                        logger.error(f"Error executing task {task['id']}: {e}")
                else:
                    # Wait until next task or 1 second
                    time.sleep(min(timestamp - now, 1))

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(1)

    def get_scheduled_tasks(self) -> Dict[str, dict]:
        """Get all scheduled tasks.

        Returns:
            dict: Dictionary of scheduled tasks.
        """
        return self.scheduled_tasks.copy()

    def get_task(self, task_id: str) -> Optional[dict]:
        """Get a specific scheduled task.

        Args:
            task_id: Task identifier.

        Returns:
            dict: Task information or None if not found.
        """
        return self.scheduled_tasks.get(task_id)

    def clear(self) -> None:
        """Clear all scheduled tasks."""
        with self._lock:
            while not self.tasks.empty():
                self.tasks.get()
            self.scheduled_tasks.clear()
        logger.debug("Cleared all scheduled tasks")