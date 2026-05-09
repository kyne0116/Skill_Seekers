#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tier 1 Skills Scraping Script

抓取 ai-personal-assistant 终态架构最相关的 6 个一级仓库为 Claude Skill。
推进顺序与产品方案优先级对齐。

Phase 1: mastra              (L1 编排 + L2.6 记忆双载体, ~30-40 min)
Phase 2: vercel-ai           (L3 流式合成 + 前端 useChat, ~30-40 min)
Phase 3: mcp-typescript-sdk  (L2 能力注册边界, ~10-15 min)
Phase 4: promptfoo           (L3 评估闭环, ~20-30 min)
Phase 5: llamaindex-ts       (L2.5 文件解析 + RAG, ~25-35 min)
Phase 6: stagehand           (探索式浏览器, ~10-15 min)

Usage:
    python run_tier1.py
    python run_tier1.py --phase 1          # 仅运行 phase 1
    python run_tier1.py --skip-existing    # 跳过已完成 phase
    python run_tier1.py --force-retry      # 自动重试失败 phase
    python run_tier1.py --phase 2 --phase 3  # 运行 phase 2 和 3
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
    # estimated_time 按"文档抓取 + GitHub clone + C3 surface + merge"实际经验值
    # timeout = estimated_time × 2，已校准避免 TIMEOUT 误杀
    {
        "name": "mastra",
        "config": "configs/mastra.json",
        "description": "Mastra Workflow + Memory + MCP integration (~25-30 min)",
        "estimated_time": 1800  # 30 minutes → timeout 60 min
    },
    {
        "name": "vercel-ai",
        "config": "configs/vercel-ai.json",
        "description": "Vercel AI SDK Core + UI hooks (@ai-sdk/react) (~30-40 min, 235 URLs)",
        "estimated_time": 2400  # 40 minutes → timeout 80 min
    },
    {
        "name": "mcp-typescript-sdk",
        "config": "configs/mcp-typescript-sdk.json",
        "description": "Model Context Protocol TypeScript SDK (~15-20 min, 127 URLs)",
        "estimated_time": 1200  # 20 minutes → timeout 40 min
    },
    {
        "name": "promptfoo",
        "config": "configs/promptfoo.json",
        "description": "Promptfoo LLM evaluation & red-teaming (~20-25 min)",
        "estimated_time": 1500  # 25 minutes → timeout 50 min
    },
    {
        "name": "llamaindex-ts",
        "config": "configs/llamaindex-ts.json",
        "description": "LlamaIndex TypeScript - file parsing + RAG (~25-30 min, monorepo)",
        "estimated_time": 1800  # 30 minutes → timeout 60 min
    },
    {
        "name": "stagehand",
        "config": "configs/stagehand.json",
        "description": "Stagehand exploratory browser automation (~10-15 min)",
        "estimated_time": 900  # 15 minutes → timeout 30 min
    }
]


def check_output_exists(task_name):
    """检查 output 是否已存在。"""
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
    """运行单个 phase。"""
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
    print(f"   python watch_tier1_progress.py {phase['name']}")
    print("   OR (复用 Spring AI 同款监控):")
    print(f"   python watch_springai_progress.py {phase['name']}")
    print()

    # Wait a moment for user to start monitoring
    for i in range(5, 0, -1):
        print(f"   Starting in {i}...")
        time.sleep(1)

    print()

    # Execute scraping (v3.6.0+: unified → create <config-path> as positional source)
    # Note: --async/--workers 对 config 源不生效（v3.6.0 unified scraper 内部自管并发）
    # --enhance-level 0: 跳过 LLM 增强（Anthropic 401 + enhance_skill.py GBK 故障，避免 zip 失败）
    cmd = ["skill-seekers", "create", phase['config'], "--enhance-level", "0"]

    # Windows GBK 编码 fix (PEP 540): 强制 Python subprocess 用 UTF-8 读写文件
    # v3.6.0 的 merge_sources.py 写文件含 emoji ⚠️, 默认 GBK 会 UnicodeEncodeError
    subprocess_env = os.environ.copy()
    subprocess_env['PYTHONUTF8'] = '1'
    subprocess_env['PYTHONIOENCODING'] = 'utf-8'

    try:
        result = subprocess.run(
            cmd,
            env=subprocess_env,
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
    """主入口。"""
    parser = argparse.ArgumentParser(
        description='Run Tier 1 skills scraping (6 phases for ai-personal-assistant terminal stack)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 运行全部六个 phase
  python run_tier1.py

  # 仅运行 phase 1（mastra）
  python run_tier1.py --phase 1

  # 跳过已完成 phase
  python run_tier1.py --skip-existing

  # 运行 phase 2 和 phase 3
  python run_tier1.py --phase 2 --phase 3

  # 仅运行 phase 4（promptfoo - §37 评估闭环优先）
  python run_tier1.py --phase 4

  # 自动重试失败 phase（无人值守）
  python run_tier1.py --skip-existing --force-retry --yes

Phase 顺序对齐 ai-personal-assistant 推进顺序：
  1. mastra              ← L1 §14 + L2.6 §18 双载体
  2. vercel-ai           ← L3 §17 + 前端 §13
  3. mcp-typescript-sdk  ← L2 §15 注册边界
  4. promptfoo           ← §37 评估闭环（先建后续才能量化回归）
  5. llamaindex-ts       ← L2.5 §16 文件解析 + RAG
  6. stagehand           ← §42 探索式浏览器
        """
    )

    parser.add_argument('--phase', type=int, action='append',
                       help='Run specific phase(s) only (1-6)')
    parser.add_argument('--skip-existing', action='store_true',
                       help='Skip phases with existing output')
    parser.add_argument('--force-retry', action='store_true',
                       help='Force retry failed/timeout phases without asking')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Auto-start without prompting (for automation)')

    args = parser.parse_args()

    # Determine which phases to run
    if args.phase:
        phases_to_run = [PHASES[p-1] for p in args.phase if 1 <= p <= 6]
    else:
        phases_to_run = PHASES

    if not phases_to_run:
        print("❌ No valid phases specified")
        return 1

    print("=" * 70)
    print("TIER 1 SKILLS SCRAPING (ai-personal-assistant 终态栈)")
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
