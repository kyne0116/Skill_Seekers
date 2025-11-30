#!/usr/bin/env python3
"""
Real-time Progress Tracker for Skill Scraping

Writes progress updates to a JSON file that can be monitored in real-time.
Provides detailed status for each phase and source.
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ProgressTracker:
    """
    Real-time progress tracker for multi-source scraping.

    Progress file format:
    {
        "task_name": "spring-ai-starter",
        "status": "running",  // running, completed, failed, timeout
        "start_time": "2025-01-15 10:30:00",
        "last_update": "2025-01-15 10:32:15",
        "elapsed_seconds": 135,
        "phases": {
            "phase1_scraping": {
                "status": "running",
                "sources": {
                    "documentation": {
                        "status": "running",
                        "progress": "45/100 pages",
                        "current_url": "https://docs.spring.io/...",
                        "elapsed_seconds": 90
                    },
                    "github": {
                        "status": "pending",
                        "progress": "0/0",
                        "elapsed_seconds": 0
                    }
                }
            },
            "phase2_conflict_detection": {"status": "pending"},
            "phase3_merging": {"status": "pending"},
            "phase4_building": {"status": "pending"}
        },
        "errors": [],
        "warnings": []
    }
    """

    def __init__(self, task_name: str, progress_file: Optional[str] = None):
        """
        Initialize progress tracker.

        Args:
            task_name: Name of the scraping task
            progress_file: Path to progress file (default: output/{task_name}_progress.json)
        """
        self.task_name = task_name

        if progress_file is None:
            progress_file = f"output/{task_name}_progress.json"

        self.progress_file = progress_file

        # Ensure output directory exists
        os.makedirs(os.path.dirname(progress_file) or ".", exist_ok=True)

        # Initialize progress data
        self.data = {
            "task_name": task_name,
            "status": "initialized",
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_seconds": 0,
            "phases": {
                "phase1_scraping": {
                    "status": "pending",
                    "sources": {}
                },
                "phase2_conflict_detection": {"status": "pending"},
                "phase3_merging": {"status": "pending"},
                "phase4_building": {"status": "pending"}
            },
            "errors": [],
            "warnings": []
        }

        self.start_time = time.time()
        self._write()

    def _write(self):
        """Write progress data to file."""
        # Update elapsed time
        self.data["elapsed_seconds"] = int(time.time() - self.start_time)
        self.data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Write to file (atomic write)
        temp_file = self.progress_file + ".tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        # Atomic rename
        os.replace(temp_file, self.progress_file)

    def start_task(self):
        """Mark task as started."""
        self.data["status"] = "running"
        self._write()

    def complete_task(self):
        """Mark task as completed."""
        self.data["status"] = "completed"
        self._write()

    def fail_task(self, error: str):
        """Mark task as failed."""
        self.data["status"] = "failed"
        self.data["errors"].append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": error
        })
        self._write()

    def timeout_task(self):
        """Mark task as timeout."""
        self.data["status"] = "timeout"
        self._write()

    def start_phase(self, phase: str):
        """Start a phase."""
        if phase in self.data["phases"]:
            self.data["phases"][phase]["status"] = "running"
            self._write()

    def complete_phase(self, phase: str):
        """Complete a phase."""
        if phase in self.data["phases"]:
            self.data["phases"][phase]["status"] = "completed"
            self._write()

    def fail_phase(self, phase: str, error: str):
        """Mark phase as failed."""
        if phase in self.data["phases"]:
            self.data["phases"][phase]["status"] = "failed"
            self.data["phases"][phase]["error"] = error
            self.add_error(f"{phase}: {error}")
            self._write()

    def update_source(self, source_type: str, status: str,
                     progress: Optional[str] = None,
                     current_url: Optional[str] = None,
                     details: Optional[Dict] = None):
        """
        Update source progress.

        Args:
            source_type: Type of source (documentation, github, pdf)
            status: Status (pending, running, completed, failed)
            progress: Progress string (e.g., "45/100 pages")
            current_url: Current URL being processed
            details: Additional details
        """
        if "sources" not in self.data["phases"]["phase1_scraping"]:
            self.data["phases"]["phase1_scraping"]["sources"] = {}

        sources = self.data["phases"]["phase1_scraping"]["sources"]

        if source_type not in sources:
            sources[source_type] = {
                "status": "pending",
                "progress": "0/0",
                "elapsed_seconds": 0,
                "start_time": None
            }

        source = sources[source_type]

        # Update status
        if status != source["status"]:
            source["status"] = status
            if status == "running" and source["start_time"] is None:
                source["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                source["source_start"] = time.time()

        # Update progress
        if progress:
            source["progress"] = progress

        if current_url:
            source["current_url"] = current_url

        if details:
            source.update(details)

        # Update elapsed time for this source
        if "source_start" in source and status == "running":
            source["elapsed_seconds"] = int(time.time() - source["source_start"])

        self._write()

    def add_error(self, error: str):
        """Add an error message."""
        self.data["errors"].append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": error
        })
        self._write()

    def add_warning(self, warning: str):
        """Add a warning message."""
        self.data["warnings"].append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": warning
        })
        self._write()

    def get_summary(self) -> str:
        """Get a human-readable summary."""
        lines = []
        lines.append(f"Task: {self.data['task_name']}")
        lines.append(f"Status: {self.data['status']}")
        lines.append(f"Elapsed: {self.data['elapsed_seconds']}s ({self.data['elapsed_seconds']/60:.1f} min)")

        lines.append("\nPhases:")
        for phase, data in self.data["phases"].items():
            status = data.get("status", "pending")
            lines.append(f"  {phase}: {status}")

            if phase == "phase1_scraping" and "sources" in data:
                for source, sdata in data["sources"].items():
                    progress = sdata.get("progress", "")
                    sstatus = sdata.get("status", "pending")
                    elapsed = sdata.get("elapsed_seconds", 0)
                    lines.append(f"    {source}: {sstatus} - {progress} ({elapsed}s)")

        if self.data["errors"]:
            lines.append(f"\nErrors: {len(self.data['errors'])}")
            for err in self.data["errors"][-3:]:  # Last 3 errors
                lines.append(f"  [{err['time']}] {err['message']}")

        if self.data["warnings"]:
            lines.append(f"\nWarnings: {len(self.data['warnings'])}")

        return "\n".join(lines)


def load_progress(progress_file: str) -> Optional[Dict]:
    """Load progress from file."""
    if not os.path.exists(progress_file):
        return None

    try:
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None
