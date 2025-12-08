#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spring AI Scraping Script

Executes all Spring AI scraping configurations:
- Phase 1: spring_ai_starter (Quick Start - 5-10 min)
- Phase 2: spring_ai_official (Complete Framework - 15-20 min)
- Phase 3: spring_ai_alibaba (Full Ecosystem - 30-60 min)
- Phase 4: spring_ai_examples (Examples Repository - 3-5 min)

Usage:
    python run_springai.py
    python run_springai.py --phase 1      # Run only phase 1
    python run_springai.py --skip-existing # Skip if output exists
    python run_springai.py --force-retry   # Auto-retry failed phases
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

import argparse
import subprocess
import time
from pathlib import Path


PHASES = [
    {
        "name": "spring-ai-starter",
        "config": "configs/spring_ai_starter.json",
        "description": "Quick Start (5-10 min)",
        "estimated_time": 600  # 10 minutes
    },
    {
        "name": "spring-ai-official",
        "config": "configs/spring_ai_official.json",
        "description": "Complete Framework (15-20 min)",
        "estimated_time": 1200  # 20 minutes
    },
    {
        "name": "spring-ai-alibaba",
        "config": "configs/spring_ai_alibaba.json",
        "description": "Full Ecosystem (30-60 min)",
        "estimated_time": 3600  # 60 minutes
    },
    {
        "name": "spring-ai-examples",
        "config": "configs/spring_ai_examples.json",
        "description": "Examples Repository (3-5 min)",
        "estimated_time": 300  # 5 minutes
    }
]


def check_output_exists(task_name):
    """Check if output already exists."""
    import json

    skill_file = f"output/{task_name}/SKILL.md"
    progress_file = f"output/{task_name}_progress.json"

    # Check progress file first (most reliable)
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)

            status = progress.get('status', 'unknown')

            if status == 'completed':
                return "completed"
            elif status == 'running':
                # Check if it's stale (last update > 10 minutes ago)
                from datetime import datetime
                last_update = progress.get('last_update', '')
                if last_update:
                    try:
                        last_time = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
                        elapsed = (datetime.now() - last_time).total_seconds()
                        if elapsed > 600:  # 10 minutes
                            return "stale"
                    except:
                        pass
                return "running"
            elif status == 'failed' or status == 'timeout':
                return status
            else:
                return "in_progress"
        except:
            pass

    # Fallback to checking skill file
    if os.path.exists(skill_file):
        return "completed"

    return "not_started"


def run_phase(phase, skip_existing=False, force_retry=False):
    """Run a single phase."""
    print("\n" + "=" * 70)
    print(f"📦 PHASE: {phase['name']}")
    print(f"   {phase['description']}")
    print(f"   Estimated time: {phase['estimated_time']//60} minutes")
    print("=" * 70)

    # Check if already exists
    status = check_output_exists(phase['name'])

    # Handle different statuses
    if status == "completed":
        if skip_existing:
            print(f"✅ Already completed - skipping")
            return "skipped"
        else:
            print(f"⚠️  Already completed!")
            if not force_retry:
                response = input("   Re-run anyway? (y/n): ")
                if response.lower() != 'y':
                    return "skipped"
            print("   Re-running phase...")

    elif status == "running":
        print("⚠️  Previous scraping appears to be RUNNING")
        print("   This might be:")
        print("   1. Another process is currently running")
        print("   2. Previous process crashed without cleanup")
        if not force_retry:
            response = input("   Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return "cancelled"
        print("   Continuing anyway (--force-retry enabled)...")

    elif status == "stale":
        print("⚠️  Previous scraping is STALE (no update for 10+ minutes)")
        print("   Previous process likely crashed or timed out")
        if not force_retry:
            response = input("   Retry this phase? (y/n): ")
            if response.lower() != 'y':
                return "cancelled"
        print("   Retrying phase (--force-retry enabled)...")

    elif status == "failed":
        print("❌ Previous attempt FAILED")
        if not force_retry:
            response = input("   Retry this phase? (y/n): ")
            if response.lower() != 'y':
                return "cancelled"
        print("   Retrying phase...")

    elif status == "timeout":
        print("⏰ Previous attempt TIMEOUT")
        if not force_retry:
            response = input("   Retry with current timeout settings? (y/n): ")
            if response.lower() != 'y':
                return "cancelled"
        print("   Retrying phase...")

    # Run scraping
    print(f"\n🚀 Starting scraping...")
    print(f"   Config: {phase['config']}")
    print(f"   Progress tracking: output/{phase['name']}_progress.json")
    print()
    print("💡 TIP: Open another terminal and run:")
    print(f"   python watch_springai_progress.py {phase['name']}")
    print("   OR:")
    print(f"   python watch_springai_progress.py  (auto-detect mode)")
    print()

    # Wait a moment for user to start monitoring
    for i in range(5, 0, -1):
        print(f"   Starting in {i}...")
        time.sleep(1)

    print()

    # Execute scraping
    cmd = ["skill-seekers", "unified", "--config", phase['config']]

    try:
        result = subprocess.run(
            cmd,
            timeout=phase['estimated_time'] * 2  # Double the estimated time as max timeout
        )

        if result.returncode == 0:
            print(f"\n✅ Phase completed successfully: {phase['name']}")

            # Auto-package the skill
            skill_dir = f"output/{phase['name']}"
            if os.path.exists(skill_dir):
                print(f"\n📦 Packaging skill...")
                try:
                    package_result = subprocess.run(
                        ["skill-seekers", "package", skill_dir, "--no-open"],
                        timeout=60
                    )
                    if package_result.returncode == 0:
                        zip_file = f"output/{phase['name']}.zip"
                        if os.path.exists(zip_file):
                            print(f"✅ Package created: {zip_file}")
                        else:
                            print(f"⚠️  Package command succeeded but zip file not found")
                    else:
                        print(f"⚠️  Package failed with exit code {package_result.returncode}")
                except Exception as e:
                    print(f"⚠️  Package error: {e}")

            return "completed"
        else:
            print(f"\n❌ Phase failed with exit code {result.returncode}")
            return "failed"

    except subprocess.TimeoutExpired:
        print(f"\n⏰ Phase TIMEOUT after {phase['estimated_time']*2//60} minutes")
        print("   Consider:")
        print("   1. Reduce max_pages in config")
        print("   2. Improve network connectivity")
        print("   3. Use --skip-existing to continue from last successful phase")
        return "timeout"

    except KeyboardInterrupt:
        print("\n⚠️  Phase interrupted by user")
        return "interrupted"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run Spring AI scraping (4 phases)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all four phases
  python run_springai.py

  # Run only phase 1 (quick start)
  python run_springai.py --phase 1

  # Skip phases that already have output
  python run_springai.py --skip-existing

  # Run phases 2 and 3
  python run_springai.py --phase 2 --phase 3

  # Run only phase 4 (examples repository)
  python run_springai.py --phase 4

  # Auto-retry failed phases
  python run_springai.py --skip-existing --force-retry
        """
    )

    parser.add_argument('--phase', type=int, action='append',
                       help='Run specific phase(s) only (1-4)')
    parser.add_argument('--skip-existing', action='store_true',
                       help='Skip phases with existing output')
    parser.add_argument('--force-retry', action='store_true',
                       help='Force retry failed/timeout phases without asking')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Auto-start without prompting (for automation)')

    args = parser.parse_args()

    # Determine which phases to run
    if args.phase:
        phases_to_run = [PHASES[p-1] for p in args.phase if 1 <= p <= 4]
    else:
        phases_to_run = PHASES

    if not phases_to_run:
        print("❌ No valid phases specified")
        return 1

    print("=" * 70)
    print("SPRING AI SCRAPING")
    print("=" * 70)
    print(f"\nPhases to run: {len(phases_to_run)}")
    for i, phase in enumerate(phases_to_run, 1):
        print(f"  {i}. {phase['name']} - {phase['description']}")

    total_time = sum(p['estimated_time'] for p in phases_to_run)
    print(f"\nEstimated total time: {total_time//60} minutes")

    if args.skip_existing:
        print("\n⏭️  Skip existing: ENABLED")

    if args.force_retry:
        print("\n🔄 Force retry: ENABLED (will auto-retry failed phases)")

    print("\n" + "=" * 70)

    # Only prompt for input if not using --yes flag
    if not args.yes:
        input("Press Enter to start...")
    else:
        print("Auto-starting (--yes flag enabled)...")
        time.sleep(1)

    # Run phases
    results = {}
    start_time = time.time()

    for phase in phases_to_run:
        result = run_phase(phase, skip_existing=args.skip_existing, force_retry=args.force_retry)
        results[phase['name']] = result

        if result == "interrupted":
            print("\n⚠️  Scraping interrupted by user")
            break

        if result == "failed" or result == "timeout":
            print("\n⚠️  Phase failed - stopping")
            response = input("   Continue to next phase anyway? (y/n): ")
            if response.lower() != 'y':
                break

    # Summary
    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    for phase_name, result in results.items():
        icon = {
            "completed": "✅",
            "failed": "❌",
            "timeout": "⏰",
            "skipped": "⏭️",
            "cancelled": "🚫",
            "interrupted": "⚠️"
        }.get(result, "❓")
        print(f"{icon} {phase_name}: {result}")

    print(f"\nTotal elapsed time: {int(elapsed//60)} minutes {int(elapsed%60)} seconds")
    print("=" * 70)

    # Final recommendations
    completed = sum(1 for r in results.values() if r == "completed")
    total = len(results)

    if completed == total:
        print("\n🎉 All phases completed successfully!")
        print("\n📦 Generated skill packages:")
        for phase in phases_to_run:
            if results.get(phase['name']) == "completed":
                zip_file = f"output/{phase['name']}.zip"
                if os.path.exists(zip_file):
                    file_size = os.path.getsize(zip_file) / 1024  # KB
                    print(f"   ✅ {zip_file} ({file_size:.1f} KB)")
                else:
                    print(f"   ⚠️  {zip_file} (not found - may need manual packaging)")
        print("\n🚀 Next step: Upload to Claude")
        print("   Visit: https://claude.ai/skills")
    else:
        print(f"\n⚠️  {completed}/{total} phases completed")
        print("\n💡 Tips:")
        print("   - Check progress files in output/ directory")
        print("   - Review error messages above")
        print("   - Use --skip-existing to resume")

    return 0 if completed == total else 1


if __name__ == '__main__':
    sys.exit(main())
