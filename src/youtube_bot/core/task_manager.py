"""
Task Manager module for YouTube Live Comment Bot.

This module handles task creation, execution, scheduling, and management.
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Callable, Any
from queue import PriorityQueue
from dataclasses import dataclass
from datetime import datetime

from . import (
    TaskID, TaskStatus, TaskPriority, TaskConfig, TaskResult,
    TaskCallback, TaskError, create_task_id
)
from .config import Config
from .scheduler import Scheduler
from ..youtube.bot import YouTubeBot

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a bot task."""
    id: TaskID
    config: TaskConfig
    bot: YouTubeBot
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[TaskResult] = None
    retry_count: int = 0

    def __lt__(self, other: 'Task') -> bool:
        """Compare tasks based on priority."""
        return self.config.priority.value < other.config.priority.value


class TaskManager:
    """Manages bot tasks and their execution."""

    def __init__(self, config: Config):
        """Initialize TaskManager.

        Args:
            config: Application configuration.
        """
        self.config = config
        self.tasks: Dict[TaskID, Task] = {}
        self.active_tasks: Dict[TaskID, threading.Thread] = {}
        self.task_queue = PriorityQueue()
        self.scheduler = Scheduler()
        self.callbacks = TaskCallback()
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Start task processor thread
        self._processor_thread = threading.Thread(
            target=self._process_task_queue,
            daemon=True
        )
        self._processor_thread.start()

    def create_task(
            self,
            priority: TaskPriority = TaskPriority.NORMAL,
            max_duration: Optional[int] = None,
            max_retries: int = 3,
            **kwargs
    ) -> TaskID:
        """Create a new task.

        Args:
            priority: Task priority level.
            max_duration: Maximum task duration in seconds.
            max_retries: Maximum number of retry attempts.
            **kwargs: Additional task configuration parameters.

        Returns:
            str: Task ID.

        Raises:
            TaskError: If task creation fails.
        """
        try:
            task_id = create_task_id()
            task_config = TaskConfig(
                task_id=task_id,
                priority=priority,
                max_duration=max_duration,
                max_retries=max_retries
            )

            bot = YouTubeBot(self.config)
            task = Task(id=task_id, config=task_config, bot=bot)

            with self._lock:
                self.tasks[task_id] = task
                self.task_queue.put((priority.value, task))

            logger.info(f"Created task {task_id} with priority {priority}")
            return task_id

        except Exception as e:
            raise TaskError(f"Failed to create task: {e}")

    def schedule_task(
            self,
            schedule_time: datetime,
            priority: TaskPriority = TaskPriority.NORMAL,
            **kwargs
    ) -> TaskID:
        """Schedule a task for future execution.

        Args:
            schedule_time: When to execute the task.
            priority: Task priority level.
            **kwargs: Additional task configuration.

        Returns:
            str: Task ID.
        """
        task_id = self.create_task(priority=priority, **kwargs)
        self.scheduler.schedule(
            schedule_time,
            self._execute_task,
            task_id
        )
        return task_id

    def cancel_task(self, task_id: TaskID) -> None:
        """Cancel a pending or running task.

        Args:
            task_id: ID of task to cancel.

        Raises:
            TaskError: If task cancellation fails.
        """
        try:
            with self._lock:
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    task.status = TaskStatus.CANCELLED

                    if task_id in self.active_tasks:
                        # Stop the task's bot
                        task.bot.stop()
                        # Wait for thread to finish
                        self.active_tasks[task_id].join(timeout=5)
                        del self.active_tasks[task_id]

                    logger.info(f"Cancelled task {task_id}")

        except Exception as e:
            raise TaskError(f"Failed to cancel task {task_id}: {e}")

    def pause_task(self, task_id: TaskID) -> None:
        """Pause a running task.

        Args:
            task_id: ID of task to pause.
        """
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.PAUSED
                task.bot.pause()
                self.callbacks.trigger('on_pause', task)

    def resume_task(self, task_id: TaskID) -> None:
        """Resume a paused task.

        Args:
            task_id: ID of task to resume.
        """
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status == TaskStatus.PAUSED:
                    task.status = TaskStatus.RUNNING
                    task.bot.resume()
                    self.callbacks.trigger('on_resume', task)

    def get_task_status(self, task_id: TaskID) -> Optional[TaskStatus]:
        """Get current status of a task.

        Args:
            task_id: ID of task to check.

        Returns:
            TaskStatus: Current task status or None if task not found.
        """
        return self.tasks.get(task_id).status if task_id in self.tasks else None

    def get_task_result(self, task_id: TaskID) -> Optional[TaskResult]:
        """Get result of a completed task.

        Args:
            task_id: ID of task to get result for.

        Returns:
            TaskResult: Task result or None if task not completed.
        """
        task = self.tasks.get(task_id)
        return task.result if task and task.status == TaskStatus.COMPLETED else None

    def _execute_task(self, task_id: TaskID) -> None:
        """Execute a task.

        Args:
            task_id: ID of task to execute.
        """
        task = self.tasks.get(task_id)
        if not task:
            return

        try:
            task.status = TaskStatus.RUNNING
            task.start_time = time.time()
            self.callbacks.trigger('on_start', task)

            # Start task in a new thread
            thread = threading.Thread(
                target=self._run_task,
                args=(task,)
            )

            with self._lock:
                self.active_tasks[task_id] = thread

            thread.start()

        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            self._handle_task_error(task, e)

    def _run_task(self, task: Task) -> None:
        """Run a task and handle its completion.

        Args:
            task: Task to run.
        """
        try:
            # Start the bot
            task.bot.start()

            # Monitor execution
            while not self._stop_event.is_set():
                if task.status == TaskStatus.CANCELLED:
                    break

                if task.config.max_duration:
                    elapsed = time.time() - task.start_time
                    if elapsed >= task.config.max_duration:
                        logger.info(f"Task {task.id} reached maximum duration")
                        break

                time.sleep(1)

            # Clean up
            task.bot.stop()
            task.end_time = time.time()
            task.status = TaskStatus.COMPLETED

            # Create result
            task.result = TaskResult(
                task_id=task.id,
                status=task.status,
                start_time=task.start_time,
                end_time=task.end_time,
                success=True
            )

            self.callbacks.trigger('on_complete', task)

        except Exception as e:
            self._handle_task_error(task, e)
        finally:
            with self._lock:
                if task.id in self.active_tasks:
                    del self.active_tasks[task.id]

    def _handle_task_error(self, task: Task, error: Exception) -> None:
        """Handle task execution error.

        Args:
            task: Task that encountered error.
            error: The error that occurred.
        """
        task.status = TaskStatus.FAILED
        task.end_time = time.time()
        task.result = TaskResult(
            task_id=task.id,
            status=task.status,
            start_time=task.start_time,
            end_time=task.end_time,
            success=False,
            error=error
        )

        logger.error(f"Task {task.id} failed: {error}")

        # Handle retries
        if task.retry_count < task.config.max_retries:
            task.retry_count += 1
            delay = task.config.retry_delay * task.retry_count
            logger.info(f"Retrying task {task.id} in {delay} seconds")
            self.scheduler.schedule_after(
                delay,
                self._execute_task,
                task.id
            )
        else:
            self.callbacks.trigger('on_error', task)

    def _process_task_queue(self) -> None:
        """Process tasks from the task queue."""
        while not self._stop_event.is_set():
            try:
                # Get next task from queue
                _, task = self.task_queue.get(timeout=1)
                if task.status == TaskStatus.PENDING:
                    self._execute_task(task.id)

            except Exception as e:
                if not isinstance(e, EOFError):
                    logger.error(f"Error processing task queue: {e}")

    def shutdown(self) -> None:
        """Shutdown the task manager."""
        self._stop_event.set()

        # Cancel all active tasks
        for task_id in list(self.active_tasks.keys()):
            self.cancel_task(task_id)

        # Wait for processor thread
        self._processor_thread.join(timeout=5)

        # Clear all tasks
        with self._lock:
            self.tasks.clear()
            self.active_tasks.clear()

        logger.info("Task manager shutdown complete")