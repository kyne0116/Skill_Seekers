#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tier 2 Skills Scraping Script

抓取 ai-personal-assistant 桌面宿主 + 基础工具栈的 3 个二级仓库。
对应代码层 wrapper / 静态断言 / 录制 / schema 校验全覆盖。

Phase 1: electron     (Electron 35 主进程 / IPC / preload, ~25 min)
Phase 2: playwright   (正式录制业务域 skill 路径 / Stagehand 基底, ~25 min)
Phase 3: zod          (L1 plan / L2 contentProducer / MCP inputSchema 校验, ~10 min)

Usage:
    python run_tier2.py
    python run_tier2.py --phase 3          # 仅运行 zod (体量小)
    python run_tier2.py --skip-existing    # 跳过已完成
    python run_tier2.py --force-retry      # 自动重试失败
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

# 自动加载项目根目录 .env（GITHUB_TOKEN / ANTHROPIC_API_KEY 等）
# v3.6.0 skill-seekers 本身不读 .env，由本编排脚本在调用前注入到 subprocess 环境
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv 未装时跳过；用户需手动 export 环境变量
    pass


PHASES = [
    # estimated_time 翻倍校准（参考 Tier 1 经验：实际耗时是初始估计的 2-3 倍）
    # timeout = estimated_time × 2
    {
        "name": "electron",
        "config": "configs/electron.json",
        "description": "Electron 35+ 桌面端宿主 (~25-30 min, ~600 页 docs)",
        "estimated_time": 1800  # 30 minutes → timeout 60 min
    },
    {
        "name": "playwright",
        "config": "configs/playwright.json",
        "description": "Playwright Node.js 浏览器自动化 (~20-25 min)",
        "estimated_time": 1500  # 25 minutes → timeout 50 min
    },
    {
        "name": "zod",
        "config": "configs/zod.json",
        "description": "Zod v4 TypeScript schema 校验 (~10 min)",
        "estimated_time": 600  # 10 minutes → timeout 20 min
    }
]


def check_output_exists(task_name):
    """检查 output 是否已存在。"""
    import json

    skill_file = f"output/{task_name}/SKILL.md"
    progress_file = f"output/{task_name}_progress.json"

    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)

            status = progress.get('status', 'unknown')

            if status == 'completed':
                return "completed"
            elif status == 'running':
                from datetime import datetime
                last_update = progress.get('last_update', '')
                if last_update:
                    try:
                        last_time = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
                        elapsed = (datetime.now() - last_time).total_seconds()
                        if elapsed > 600:
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

    if os.path.exists(skill_file):
        return "completed"

    return "not_started"


def run_phase(phase, skip_existing=False, force_retry=False):
    """运行单个 phase。"""
    print("\n" + "=" * 70)
    print(f"📦 PHASE: {phase['name']}")
    print(f"   {phase['description']}")
    print(f"   Estimated time: {phase['estimated_time']//60} minutes")
    print("=" * 70)

    status = check_output_exists(phase['name'])

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
        if not force_retry:
            response = input("   Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return "cancelled"

    elif status == "stale":
        print("⚠️  Previous scraping is STALE (no update for 10+ minutes)")
        if not force_retry:
            response = input("   Retry this phase? (y/n): ")
            if response.lower() != 'y':
                return "cancelled"

    elif status == "failed":
        print("❌ Previous attempt FAILED")
        if not force_retry:
            response = input("   Retry this phase? (y/n): ")
            if response.lower() != 'y':
                return "cancelled"

    elif status == "timeout":
        print("⏰ Previous attempt TIMEOUT")
        if not force_retry:
            response = input("   Retry with current timeout settings? (y/n): ")
            if response.lower() != 'y':
                return "cancelled"

    print(f"\n🚀 Starting scraping...")
    print(f"   Config: {phase['config']}")
    print(f"   Progress tracking: output/{phase['name']}_progress.json")
    print()
    print("💡 TIP: Open another terminal and run:")
    print(f"   python watch_springai_progress.py {phase['name']}")
    print()

    for i in range(5, 0, -1):
        print(f"   Starting in {i}...")
        time.sleep(1)

    print()

    # v3.6.0+: skill-seekers create <config-path>
    # Note: --async/--workers 对 config 源不生效（v3.6.0 unified scraper 内部自管并发）
    # --enhance-level 0: 跳过 LLM 增强（Anthropic 401 + enhance_skill.py GBK 故障，避免 zip 失败）
    cmd = ["skill-seekers", "create", phase['config'], "--enhance-level", "0"]

    # Windows GBK 编码 fix (PEP 540): 强制 Python subprocess 用 UTF-8 读写文件
    subprocess_env = os.environ.copy()
    subprocess_env['PYTHONUTF8'] = '1'
    subprocess_env['PYTHONIOENCODING'] = 'utf-8'

    try:
        result = subprocess.run(
            cmd,
            env=subprocess_env,
            timeout=phase['estimated_time'] * 2
        )

        if result.returncode == 0:
            print(f"\n✅ Phase completed successfully: {phase['name']}")

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
                except Exception as e:
                    print(f"⚠️  Package error: {e}")

            return "completed"
        else:
            print(f"\n❌ Phase failed with exit code {result.returncode}")
            return "failed"

    except subprocess.TimeoutExpired:
        print(f"\n⏰ Phase TIMEOUT after {phase['estimated_time']*2//60} minutes")
        return "timeout"

    except KeyboardInterrupt:
        print("\n⚠️  Phase interrupted by user")
        return "interrupted"


def main():
    """主入口。"""
    parser = argparse.ArgumentParser(
        description='Run Tier 2 skills scraping (3 phases for ai-personal-assistant host + base tools)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 运行全部三个 phase
  python run_tier2.py

  # 仅运行 phase 3（zod - 体量最小）
  python run_tier2.py --phase 3

  # 跳过已完成 phase
  python run_tier2.py --skip-existing

  # 自动重试失败 phase（无人值守）
  python run_tier2.py --skip-existing --force-retry --yes

Phase 顺序：
  1. electron        ← 桌面宿主 / IPC / preload / webContents
  2. playwright      ← 正式录制业务域 skill 路径 + Stagehand 基底
  3. zod             ← L1 / L2 / MCP 三层 schema 校验
        """
    )

    parser.add_argument('--phase', type=int, action='append',
                       help='Run specific phase(s) only (1-3)')
    parser.add_argument('--skip-existing', action='store_true',
                       help='Skip phases with existing output')
    parser.add_argument('--force-retry', action='store_true',
                       help='Force retry failed/timeout phases without asking')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Auto-start without prompting (for automation)')

    args = parser.parse_args()

    if args.phase:
        phases_to_run = [PHASES[p-1] for p in args.phase if 1 <= p <= 3]
    else:
        phases_to_run = PHASES

    if not phases_to_run:
        print("❌ No valid phases specified")
        return 1

    print("=" * 70)
    print("TIER 2 SKILLS SCRAPING (ai-personal-assistant 宿主 + 基础工具)")
    print("=" * 70)
    print(f"\nPhases to run: {len(phases_to_run)}")
    for i, phase in enumerate(phases_to_run, 1):
        print(f"  {i}. {phase['name']} - {phase['description']}")

    total_time = sum(p['estimated_time'] for p in phases_to_run)
    print(f"\nEstimated total time: {total_time//60} minutes")

    if args.skip_existing:
        print("\n⏭️  Skip existing: ENABLED")

    if args.force_retry:
        print("\n🔄 Force retry: ENABLED")

    print("\n" + "=" * 70)

    if not args.yes:
        input("Press Enter to start...")
    else:
        print("Auto-starting (--yes flag enabled)...")
        time.sleep(1)

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

    completed = sum(1 for r in results.values() if r == "completed")
    total = len(results)

    if completed == total:
        print("\n🎉 All phases completed successfully!")
        print("\n📦 Generated skill packages:")
        for phase in phases_to_run:
            if results.get(phase['name']) == "completed":
                zip_file = f"output/{phase['name']}.zip"
                if os.path.exists(zip_file):
                    file_size = os.path.getsize(zip_file) / 1024
                    print(f"   ✅ {zip_file} ({file_size:.1f} KB)")
        print("\n🚀 Next step: Upload to Claude")
    else:
        print(f"\n⚠️  {completed}/{total} phases completed")

    return 0 if completed == total else 1


if __name__ == '__main__':
    sys.exit(main())
