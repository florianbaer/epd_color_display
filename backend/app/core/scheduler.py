"""Scheduler for automated image generation."""

import logging
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class GenerationScheduler:
    """Manages scheduled image generation tasks."""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._generation_callback = None
        self._enabled = False
        self._schedule_time = "19:00"
        self._timezone = "UTC"

    def configure(
        self,
        enabled: bool,
        schedule_time: str,
        timezone: str,
        generation_callback
    ):
        """
        Configure the scheduler.

        Args:
            enabled: Whether automatic generation is enabled
            schedule_time: Time in HH:MM format
            timezone: Timezone string
            generation_callback: Function to call for generation
        """
        self._enabled = enabled
        self._schedule_time = schedule_time
        self._timezone = timezone
        self._generation_callback = generation_callback

        if enabled:
            try:
                hour, minute = schedule_time.split(':')
                self.scheduler.add_job(
                    func=self._run_scheduled_generation,
                    trigger=CronTrigger(hour=int(hour), minute=int(minute)),
                    id='daily_generation',
                    name='Daily image generation',
                    replace_existing=True
                )
                logger.info(f"Scheduled daily generation at {schedule_time}")
            except Exception as e:
                logger.error(f"Failed to configure scheduler: {e}")
        else:
            logger.info("Automatic generation disabled")

    def start(self):
        """Start the scheduler."""
        if self._enabled and not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")

    def _run_scheduled_generation(self):
        """Run the scheduled generation task."""
        logger.info("Starting scheduled image generation...")
        if self._generation_callback:
            self._generation_callback()

    def get_status(self) -> dict:
        """Get current scheduler status."""
        jobs = self.scheduler.get_jobs()
        next_run = None
        if jobs:
            next_run_time = jobs[0].next_run_time
            if next_run_time:
                next_run = next_run_time.isoformat()

        return {
            "enabled": self._enabled,
            "schedule_time": self._schedule_time,
            "next_run": next_run,
            "timezone": self._timezone
        }


# Global scheduler instance
scheduler = GenerationScheduler()
