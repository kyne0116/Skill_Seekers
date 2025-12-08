#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Progress Monitor for Skill Scraping

Watches the progress file and displays updates in real-time.
Run this in a separate terminal while scraping is running.

Usage:
    # Show summary of all tasks (default)
    python watch_springai_progress.py
    python watch_springai_progress.py --summary

    # Monitor specific task in real-time
    python watch_springai_progress.py spring-ai-starter
    python watch_springai_progress.py spring-ai-official
    python watch_springai_progress.py spring-ai-alibaba
    python watch_springai_progress.py spring-ai-examples
"""

import sys
import os
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import time
from pathlib import Path
from datetime import datetime


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_time(seconds):
    """Format seconds into human-readable time."""
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m"


def get_status_icon(status):
    """Get icon for status."""
    icons = {
        'pending': '⏳',
        'running': '🔄',
        'completed': '✅',
        'failed': '❌',
        'timeout': '⏰'
    }
    return icons.get(status, '❓')


def display_progress(progress_file):
    """Display progress in a nice format."""
    if not os.path.exists(progress_file):
        print(f"❌ Progress file not found: {progress_file}")
        print(f"   Make sure scraping has started")
        return False

    try:
        with open(progress_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading progress file: {e}")
        return False

    clear_screen()

    # Header
    print("=" * 70)
    print(f"📊 Progress Monitor - {data['task_name']}")
    print("=" * 70)
    print()

    # Overall status
    status_icon = get_status_icon(data['status'])
    print(f"Status: {status_icon} {data['status'].upper()}")
    print(f"Started: {data['start_time']}")
    print(f"Last Update: {data['last_update']}")
    print(f"Elapsed: {format_time(data['elapsed_seconds'])}")
    print()

    # Phases
    print("📦 PHASES")
    print("-" * 70)

    phases = data['phases']

    # Phase 1: Scraping
    phase1 = phases['phase1_scraping']
    phase1_icon = get_status_icon(phase1['status'])
    print(f"{phase1_icon} Phase 1: Scraping Sources ({phase1['status']})")

    if 'sources' in phase1 and phase1['sources']:
        for source_type, source_data in phase1['sources'].items():
            status = source_data.get('status', 'pending')
            icon = get_status_icon(status)
            progress = source_data.get('progress', 'N/A')
            elapsed = source_data.get('elapsed_seconds', 0)

            print(f"  {icon} {source_type}: {status}")
            print(f"     Progress: {progress}")
            if elapsed > 0:
                print(f"     Time: {format_time(elapsed)}")

            if 'current_url' in source_data:
                url = source_data['current_url']
                if len(url) > 60:
                    url = url[:57] + "..."
                print(f"     URL: {url}")
    print()

    # Phase 2: Conflict Detection
    phase2 = phases['phase2_conflict_detection']
    phase2_icon = get_status_icon(phase2['status'])
    print(f"{phase2_icon} Phase 2: Conflict Detection ({phase2['status']})")
    print()

    # Phase 3: Merging
    phase3 = phases['phase3_merging']
    phase3_icon = get_status_icon(phase3['status'])
    phase3_status = phase3['status']

    # Check if Phase 2 completed with no conflicts
    phase2_status = phases.get('phase2_conflict_detection', {}).get('status', '')
    if phase3_status == 'completed' and phase2_status == 'completed':
        # Phase 3 completed might mean it was skipped (no conflicts)
        print(f"{phase3_icon} Phase 3: Merging ({phase3_status} - no conflicts detected)")
    elif phase3_status == 'pending' and phase2_status == 'completed':
        # Phase 3 pending after Phase 2 completed means it was skipped
        print(f"⏭️  Phase 3: Merging (skipped - no conflicts detected)")
    else:
        print(f"{phase3_icon} Phase 3: Merging ({phase3_status})")
    print()

    # Phase 4: Building
    phase4 = phases['phase4_building']
    phase4_icon = get_status_icon(phase4['status'])
    print(f"{phase4_icon} Phase 4: Building Skill ({phase4['status']})")
    print()

    # Errors
    if data['errors']:
        print("❌ ERRORS")
        print("-" * 70)
        for err in data['errors'][-5:]:  # Last 5 errors
            print(f"[{err['time']}] {err['message']}")
        print()

    # Warnings
    if data['warnings']:
        print("⚠️  WARNINGS")
        print("-" * 70)
        for warn in data['warnings'][-5:]:  # Last 5 warnings
            print(f"[{warn['time']}] {warn['message']}")
        print()

    # Footer
    print("=" * 70)
    if data['status'] == 'running':
        print("⏳ Scraping in progress... (Refresh every 3 seconds)")
        print("   Press Ctrl+C to stop monitoring")
    elif data['status'] == 'completed':
        print("✅ Scraping completed successfully!")
        return True  # Stop monitoring
    elif data['status'] == 'failed':
        print("❌ Scraping failed - check errors above")
        return True  # Stop monitoring
    elif data['status'] == 'timeout':
        print("⏰ Scraping timeout - consider increasing timeout in config")
        return True  # Stop monitoring

    print("=" * 70)
    return False


def find_active_tasks():
    """Find all active scraping tasks."""
    active_tasks = []

    if not os.path.exists("output"):
        return active_tasks

    # Look for all progress files
    import glob
    progress_files = glob.glob("output/*_progress.json")

    for progress_file in progress_files:
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            task_name = data['task_name']
            status = data['status']
            last_update = data.get('last_update', '')

            # Check if task is active (running or recently updated)
            is_active = False

            if status == 'running':
                is_active = True
            elif status in ['initialized', 'pending']:
                is_active = True
            elif last_update:
                # Check if updated within last 10 minutes
                try:
                    last_time = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
                    elapsed = (datetime.now() - last_time).total_seconds()
                    if elapsed < 600:  # 10 minutes
                        is_active = True
                except:
                    pass

            if is_active:
                active_tasks.append({
                    'name': task_name,
                    'file': progress_file,
                    'status': status,
                    'last_update': last_update
                })

        except Exception as e:
            continue

    return active_tasks


def select_task_interactive():
    """Interactively select a task to monitor."""
    active_tasks = find_active_tasks()

    if not active_tasks:
        print("❌ No active scraping tasks found")
        print()
        print("Available tasks to start:")
        print("  - spring-ai-starter")
        print("  - spring-ai-official")
        print("  - spring-ai-alibaba")
        print()
        print("To start a task, run:")
        print("  skill-seekers unified --config configs/spring_ai_starter.json")
        return None

    if len(active_tasks) == 1:
        task = active_tasks[0]
        print(f"✅ Found active task: {task['name']}")
        print(f"   Status: {task['status']}")
        print(f"   Last update: {task['last_update']}")
        print()
        return task['name']

    # Multiple active tasks - let user choose
    print("🔍 Found multiple active tasks:\n")

    for i, task in enumerate(active_tasks, 1):
        status_icon = get_status_icon(task['status'])
        print(f"  {i}. {status_icon} {task['name']}")
        print(f"     Status: {task['status']}")
        print(f"     Last update: {task['last_update']}")
        print()

    print("  0. Monitor all tasks (cycle through)")
    print()

    while True:
        try:
            choice = input("Select task to monitor (0-{max_num}): ".replace("{max_num}", str(len(active_tasks))))

            if not choice:
                # Default to first task
                return active_tasks[0]['name']

            choice = int(choice)

            if choice == 0:
                return "all"
            elif 1 <= choice <= len(active_tasks):
                return active_tasks[choice-1]['name']
            else:
                print(f"❌ Invalid choice. Please enter 0-{len(active_tasks)}")
        except ValueError:
            print("❌ Please enter a number")
        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled")
            return None


def monitor_all_tasks(active_tasks, refresh_interval=3):
    """Monitor all active tasks by cycling through them."""
    if not active_tasks:
        return 1

    print(f"👀 Monitoring {len(active_tasks)} tasks (cycling every {refresh_interval}s)")
    print()

    task_index = 0

    try:
        while True:
            task_name = active_tasks[task_index % len(active_tasks)]
            progress_file = f"output/{task_name}_progress.json"

            if os.path.exists(progress_file):
                should_stop = display_progress(progress_file)
                if should_stop:
                    # Task completed, remove from list
                    active_tasks.pop(task_index % len(active_tasks))
                    if not active_tasks:
                        print("\n✅ All tasks completed!")
                        return 0
                    continue

            task_index += 1
            time.sleep(refresh_interval)

    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped by user")
        return 0


def monitor(task_name, refresh_interval=3):
    """Monitor progress file continuously."""
    # Auto-detect mode
    if task_name == "auto":
        task_name = select_task_interactive()
        if not task_name:
            return 1

        if task_name == "all":
            active_tasks = [t['name'] for t in find_active_tasks()]
            return monitor_all_tasks(active_tasks, refresh_interval)

    progress_file = f"output/{task_name}_progress.json"

    print(f"👀 Monitoring progress for: {task_name}")
    print(f"📁 Progress file: {progress_file}")
    print()

    # Wait for file to be created
    wait_count = 0
    while not os.path.exists(progress_file) and wait_count < 20:
        print(f"⏳ Waiting for scraping to start... ({wait_count+1}/20)")
        time.sleep(1)
        wait_count += 1

    if not os.path.exists(progress_file):
        print("❌ Progress file not found after 20 seconds")
        print("   Make sure you started the scraping task:")
        print(f"   skill-seekers unified --config configs/{task_name}.json")
        return 1

    try:
        while True:
            should_stop = display_progress(progress_file)
            if should_stop:
                break

            time.sleep(refresh_interval)

    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped by user")
        return 0

    return 0


def show_summary():
    """Show summary of all Spring AI tasks."""
    tasks = [
        'spring-ai-starter',
        'spring-ai-official',
        'spring-ai-alibaba',
        'spring-ai-examples'
    ]

    print("=" * 70)
    print("📊 SPRING AI SCRAPING SUMMARY")
    print("=" * 70)
    print()

    all_completed = True

    for task in tasks:
        progress_file = f"output/{task}_progress.json"
        skill_dir = f"output/{task}"
        zip_file = f"output/{task}.zip"

        print(f"📦 {task}")
        print("-" * 70)

        # Check progress
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                status = data.get('status', 'unknown')
                status_icon = get_status_icon(status)
                elapsed = data.get('elapsed_seconds', 0)

                print(f"  Status: {status_icon} {status.upper()}")
                print(f"  Elapsed: {format_time(elapsed)}")

                if status != 'completed':
                    all_completed = False
            except:
                print(f"  Status: ❓ UNKNOWN (error reading progress file)")
                all_completed = False
        else:
            print(f"  Status: ⏭️  NOT STARTED")
            all_completed = False

        # Check skill directory
        if os.path.exists(skill_dir):
            skill_file = f"{skill_dir}/SKILL.md"
            if os.path.exists(skill_file):
                size = os.path.getsize(skill_file) / 1024  # KB
                print(f"  Skill: ✅ SKILL.md ({size:.1f} KB)")
            else:
                print(f"  Skill: ❌ Missing SKILL.md")
        else:
            print(f"  Skill: ❌ Directory not found")

        # Check zip package
        if os.path.exists(zip_file):
            size = os.path.getsize(zip_file) / 1024  # KB
            print(f"  Package: ✅ {task}.zip ({size:.1f} KB)")
        else:
            print(f"  Package: ❌ {task}.zip not found")
            all_completed = False

        print()

    print("=" * 70)
    if all_completed:
        print("✅ All four skills completed and packaged!")
        print()
        print("🚀 Next step: Upload to Claude")
        print("   Visit: https://claude.ai/skills")
        return 0
    else:
        print("⚠️  Some tasks incomplete or packages missing")
        print()
        print("💡 To fix:")
        print("   python run_springai.py --skip-existing --force-retry")
        return 1


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        # No argument - show summary by default
        print("🔍 Showing summary of all tasks...")
        print()
        return show_summary()

    task_name = sys.argv[1]

    # Check for --summary or --all flag
    if task_name in ['--summary', '--all', '-s']:
        return show_summary()

    # Support shorthand
    if not task_name.startswith('spring-ai'):
        # Try to match against known tasks
        possible_tasks = [
            'spring-ai-starter',
            'spring-ai-official',
            'spring-ai-alibaba',
            'spring-ai-examples'
        ]
        matches = [t for t in possible_tasks if task_name in t]
        if len(matches) == 1:
            task_name = matches[0]
            print(f"ℹ️  Resolved task name to: {task_name}")
        elif len(matches) > 1:
            print(f"❌ Ambiguous task name '{task_name}', matches:")
            for match in matches:
                print(f"   - {match}")
            return 1

    return monitor(task_name)


if __name__ == '__main__':
    sys.exit(main())
