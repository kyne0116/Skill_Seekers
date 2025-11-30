#!/usr/bin/env python3
"""
Unified Multi-Source Scraper

Orchestrates scraping from multiple sources (documentation, GitHub, PDF),
detects conflicts, merges intelligently, and builds unified skills.

This is the main entry point for unified config workflow.

Usage:
    skill-seekers unified --config configs/godot_unified.json
    skill-seekers unified --config configs/react_unified.json --merge-mode claude-enhanced
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import validators and scrapers
try:
    from skill_seekers.cli.config_validator import ConfigValidator, validate_config
    from skill_seekers.cli.conflict_detector import ConflictDetector
    from skill_seekers.cli.merge_sources import RuleBasedMerger, ClaudeEnhancedMerger
    from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
    from skill_seekers.cli.progress_tracker import ProgressTracker
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedScraper:
    """
    Orchestrates multi-source scraping and merging.

    Main workflow:
    1. Load and validate unified config
    2. Scrape all sources (docs, GitHub, PDF)
    3. Detect conflicts between sources
    4. Merge intelligently (rule-based or Claude-enhanced)
    5. Build unified skill
    """

    def __init__(self, config_path: str, merge_mode: Optional[str] = None):
        """
        Initialize unified scraper.

        Args:
            config_path: Path to unified config JSON
            merge_mode: Override config merge_mode ('rule-based' or 'claude-enhanced')
        """
        self.config_path = config_path

        # Validate and load config
        logger.info(f"Loading config: {config_path}")
        self.validator = validate_config(config_path)
        self.config = self.validator.config

        # Determine merge mode
        self.merge_mode = merge_mode or self.config.get('merge_mode', 'rule-based')
        logger.info(f"Merge mode: {self.merge_mode}")

        # Storage for scraped data
        self.scraped_data = {}

        # Output paths
        self.name = self.config['name']
        self.output_dir = f"output/{self.name}"
        self.data_dir = f"output/{self.name}_unified_data"

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

        # Initialize progress tracker
        self.progress = ProgressTracker(
            task_name=self.name,
            progress_file=f"output/{self.name}_progress.json"
        )
        logger.info(f"📊 Progress tracking: output/{self.name}_progress.json")

    def scrape_all_sources(self):
        """
        Scrape all configured sources.

        Routes to appropriate scraper based on source type.
        """
        logger.info("=" * 60)
        logger.info("PHASE 1: Scraping all sources")
        logger.info("=" * 60)

        self.progress.start_phase("phase1_scraping")

        logger.info("DEBUG: Checking if config is unified...")
        if not self.validator.is_unified:
            logger.warning("Config is not unified format, converting...")
            self.config = self.validator.convert_legacy_to_unified()

        logger.info("DEBUG: Getting sources from config...")
        sources = self.config.get('sources', [])
        logger.info(f"DEBUG: Found {len(sources)} sources")

        for i, source in enumerate(sources):
            source_type = source['type']
            logger.info(f"\n[{i+1}/{len(sources)}] Scraping {source_type} source...")

            # Initialize progress for this source
            self.progress.update_source(source_type, "running", progress="0/0")

            try:
                if source_type == 'documentation':
                    self._scrape_documentation(source)
                elif source_type == 'github':
                    self._scrape_github(source)
                elif source_type == 'pdf':
                    self._scrape_pdf(source)
                else:
                    logger.warning(f"Unknown source type: {source_type}")
                    self.progress.update_source(source_type, "failed")
            except Exception as e:
                logger.error(f"Error scraping {source_type}: {e}")
                self.progress.add_error(f"{source_type}: {str(e)}")
                self.progress.update_source(source_type, "failed")
                logger.info("Continuing with other sources...")

        logger.info(f"\n✅ Scraped {len(self.scraped_data)} sources successfully")
        self.progress.complete_phase("phase1_scraping")

    def _scrape_documentation(self, source: Dict[str, Any]):
        """Scrape documentation website."""
        # Create temporary config for doc scraper
        doc_config = {
            'name': f"{self.name}_docs",
            'base_url': source['base_url'],
            'selectors': source.get('selectors', {}),
            'url_patterns': source.get('url_patterns', {}),
            'categories': source.get('categories', {}),
            'rate_limit': source.get('rate_limit', 0.5),
            'max_pages': source.get('max_pages', 100),
            # Pass progress file path for real-time updates
            'progress_file': self.progress.progress_file if hasattr(self, 'progress') else None,
            'source_name': 'documentation'
        }

        # Write temporary config
        temp_config_path = os.path.join(self.data_dir, 'temp_docs_config.json')
        with open(temp_config_path, 'w') as f:
            json.dump(doc_config, f, indent=2)

        # Run doc_scraper as subprocess
        logger.info(f"Scraping documentation from {source['base_url']}")
        logger.info(f"Max pages: {doc_config['max_pages']}, Rate limit: {doc_config['rate_limit']}s")

        doc_scraper_path = Path(__file__).parent / "doc_scraper.py"
        cmd = [sys.executable, str(doc_scraper_path), '--config', temp_config_path, '--resume']

        # Calculate timeout: max_pages * (rate_limit + 2s per page) + 60s buffer
        estimated_time = doc_config['max_pages'] * (doc_config['rate_limit'] + 2) + 60
        timeout_seconds = source.get('timeout', max(300, int(estimated_time)))  # Minimum 5 minutes

        logger.info(f"⏱️  Estimated time: {estimated_time/60:.1f} min, Timeout: {timeout_seconds/60:.1f} min")

        logger.info(f"DEBUG: About to run command: {' '.join(cmd)}")

        try:
            # FIXED: Use Popen for real-time output instead of capture_output
            logger.info("DEBUG: Creating subprocess...")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            logger.info("DEBUG: Subprocess created, starting to stream output...")
            # Stream output in real-time
            logger.info("📥 Streaming doc_scraper output:\n")
            for line in process.stdout:
                # Forward output to user (remove logger prefix to avoid duplication)
                print(line.rstrip())

            logger.info("DEBUG: Finished streaming, waiting for process to complete...")
            # Wait for completion with timeout
            process.wait(timeout=timeout_seconds)

            if process.returncode != 0:
                logger.error(f"❌ Documentation scraping failed with exit code {process.returncode}")
                self.progress.update_source('documentation', 'failed')
                return

        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Documentation scraping TIMEOUT after {timeout_seconds}s ({timeout_seconds/60:.1f} min)")
            logger.error(f"   Consider:")
            logger.error(f"   1. Reduce max_pages (currently {doc_config['max_pages']})")
            logger.error(f"   2. Check network connectivity to {source['base_url']}")
            logger.error(f"   3. Increase timeout in config: 'timeout': {timeout_seconds * 2}")
            process.kill()
            process.wait()
            self.progress.update_source('documentation', 'timeout')
            self.progress.timeout_task()
            return

        except Exception as e:
            logger.error(f"❌ Unexpected error during documentation scraping: {e}")
            import traceback
            traceback.print_exc()
            self.progress.update_source('documentation', 'failed')
            return

        # Load scraped data
        docs_data_file = f"output/{doc_config['name']}_data/summary.json"

        if os.path.exists(docs_data_file):
            with open(docs_data_file, 'r') as f:
                summary = json.load(f)

            self.scraped_data['documentation'] = {
                'pages': summary.get('pages', []),
                'data_file': docs_data_file
            }

            total_pages = summary.get('total_pages', 0)
            logger.info(f"✅ Documentation: {total_pages} pages scraped")
            self.progress.update_source('documentation', 'completed', progress=f"{total_pages}/{total_pages} pages")
        else:
            logger.warning("⚠️  Documentation data file not found - scraping may have failed")
            self.progress.update_source('documentation', 'failed')

        # Clean up temp config
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)

    def _scrape_github(self, source: Dict[str, Any]):
        """Scrape GitHub repository with progress tracking."""
        sys.path.insert(0, str(Path(__file__).parent))

        try:
            from github_scraper import GitHubScraper
        except ImportError:
            logger.error("github_scraper.py not found")
            self.progress.update_source('github', 'failed')
            return

        # Create config for GitHub scraper
        github_config = {
            'repo': source['repo'],
            'name': f"{self.name}_github",
            'github_token': source.get('github_token'),
            'include_issues': source.get('include_issues', True),
            'max_issues': source.get('max_issues', 100),
            'include_changelog': source.get('include_changelog', True),
            'include_releases': source.get('include_releases', True),
            'include_code': source.get('include_code', True),
            'code_analysis_depth': source.get('code_analysis_depth', 'surface'),
            'file_patterns': source.get('file_patterns', []),
            'max_tree_items': source.get('max_tree_items', 5000),
            'file_tree_timeout': source.get('file_tree_timeout', 300)
        }

        # Create progress callback
        def progress_callback(source_type, status, progress=None, details=None):
            """Forward progress updates to main progress tracker."""
            self.progress.update_source(source_type, status, progress=progress, details=details)

        # Scrape
        logger.info(f"Scraping GitHub repository: {source['repo']}")
        try:
            scraper = GitHubScraper(github_config, progress_callback=progress_callback)
            github_data = scraper.scrape()

            # Save data
            github_data_file = os.path.join(self.data_dir, 'github_data.json')
            with open(github_data_file, 'w', encoding='utf-8') as f:
                json.dump(github_data, f, indent=2, ensure_ascii=False)

            self.scraped_data['github'] = {
                'data': github_data,
                'data_file': github_data_file
            }

            logger.info(f"✅ GitHub: Repository scraped successfully")
            self.progress.update_source('github', 'completed', progress="Completed")

        except Exception as e:
            logger.error(f"❌ GitHub scraping failed: {e}")
            self.progress.update_source('github', 'failed')
            self.progress.add_error(f"GitHub scraping: {str(e)}")

    def _scrape_pdf(self, source: Dict[str, Any]):
        """Scrape PDF document."""
        sys.path.insert(0, str(Path(__file__).parent))

        try:
            from pdf_scraper import PDFToSkillConverter
        except ImportError:
            logger.error("pdf_scraper.py not found")
            return

        # Create config for PDF scraper
        pdf_config = {
            'name': f"{self.name}_pdf",
            'pdf': source['path'],
            'extract_tables': source.get('extract_tables', False),
            'ocr': source.get('ocr', False),
            'password': source.get('password')
        }

        # Scrape
        logger.info(f"Scraping PDF: {source['path']}")
        converter = PDFToSkillConverter(pdf_config)
        pdf_data = converter.extract_all()

        # Save data
        pdf_data_file = os.path.join(self.data_dir, 'pdf_data.json')
        with open(pdf_data_file, 'w', encoding='utf-8') as f:
            json.dump(pdf_data, f, indent=2, ensure_ascii=False)

        self.scraped_data['pdf'] = {
            'data': pdf_data,
            'data_file': pdf_data_file
        }

        logger.info(f"✅ PDF: {len(pdf_data.get('pages', []))} pages extracted")

    def detect_conflicts(self) -> List:
        """
        Detect conflicts between documentation and code.

        Only applicable if both documentation and GitHub sources exist.

        Returns:
            List of conflicts
        """
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 2: Detecting conflicts")
        logger.info("=" * 60)

        if not self.validator.needs_api_merge():
            logger.info("No API merge needed (only one API source)")
            return []

        # Get documentation and GitHub data
        docs_data = self.scraped_data.get('documentation', {})
        github_data = self.scraped_data.get('github', {})

        if not docs_data or not github_data:
            logger.warning("Missing documentation or GitHub data for conflict detection")
            return []

        # Load data files
        with open(docs_data['data_file'], 'r', encoding='utf-8') as f:
            docs_json = json.load(f)

        with open(github_data['data_file'], 'r', encoding='utf-8') as f:
            github_json = json.load(f)

        # Detect conflicts
        detector = ConflictDetector(docs_json, github_json)
        conflicts = detector.detect_all_conflicts()

        # Save conflicts
        conflicts_file = os.path.join(self.data_dir, 'conflicts.json')
        detector.save_conflicts(conflicts, conflicts_file)

        # Print summary
        summary = detector.generate_summary(conflicts)
        logger.info(f"\n📊 Conflict Summary:")
        logger.info(f"   Total: {summary['total']}")
        logger.info(f"   By Type:")
        for ctype, count in summary['by_type'].items():
            if count > 0:
                logger.info(f"     - {ctype}: {count}")
        logger.info(f"   By Severity:")
        for severity, count in summary['by_severity'].items():
            if count > 0:
                emoji = '🔴' if severity == 'high' else '🟡' if severity == 'medium' else '🟢'
                logger.info(f"     {emoji} {severity}: {count}")

        return conflicts

    def merge_sources(self, conflicts: List):
        """
        Merge data from multiple sources.

        Args:
            conflicts: List of detected conflicts
        """
        logger.info("\n" + "=" * 60)
        logger.info(f"PHASE 3: Merging sources ({self.merge_mode})")
        logger.info("=" * 60)

        if not conflicts:
            logger.info("No conflicts to merge")
            return None

        # Get data files
        docs_data = self.scraped_data.get('documentation', {})
        github_data = self.scraped_data.get('github', {})

        # Load data
        with open(docs_data['data_file'], 'r', encoding='utf-8') as f:
            docs_json = json.load(f)

        with open(github_data['data_file'], 'r', encoding='utf-8') as f:
            github_json = json.load(f)

        # Choose merger
        if self.merge_mode == 'claude-enhanced':
            merger = ClaudeEnhancedMerger(docs_json, github_json, conflicts)
        else:
            merger = RuleBasedMerger(docs_json, github_json, conflicts)

        # Merge
        merged_data = merger.merge_all()

        # Save merged data
        merged_file = os.path.join(self.data_dir, 'merged_data.json')
        with open(merged_file, 'w') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Merged data saved: {merged_file}")

        return merged_data

    def build_skill(self, merged_data: Optional[Dict] = None):
        """
        Build final unified skill.

        Args:
            merged_data: Merged API data (if conflicts were resolved)
        """
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 4: Building unified skill")
        logger.info("=" * 60)

        # Load conflicts if they exist
        conflicts = []
        conflicts_file = os.path.join(self.data_dir, 'conflicts.json')
        if os.path.exists(conflicts_file):
            with open(conflicts_file, 'r', encoding='utf-8') as f:
                conflicts_data = json.load(f)
                conflicts = conflicts_data.get('conflicts', [])

        # Build skill
        builder = UnifiedSkillBuilder(
            self.config,
            self.scraped_data,
            merged_data,
            conflicts
        )

        builder.build()

        logger.info(f"✅ Unified skill built: {self.output_dir}/")

    def run(self):
        """
        Execute complete unified scraping workflow.
        """
        logger.info("\n" + "🚀 " * 20)
        logger.info(f"Unified Scraper: {self.config['name']}")
        logger.info("🚀 " * 20 + "\n")

        self.progress.start_task()

        try:
            # Phase 1: Scrape all sources
            self.scrape_all_sources()

            # Phase 2: Detect conflicts (if applicable)
            self.progress.start_phase("phase2_conflict_detection")
            conflicts = self.detect_conflicts()
            self.progress.complete_phase("phase2_conflict_detection")

            # Phase 3: Merge sources (if conflicts exist)
            merged_data = None
            if conflicts:
                self.progress.start_phase("phase3_merging")
                merged_data = self.merge_sources(conflicts)
                self.progress.complete_phase("phase3_merging")
            else:
                # No conflicts - mark phase as completed (skipped)
                self.progress.complete_phase("phase3_merging")

            # Phase 4: Build skill
            self.progress.start_phase("phase4_building")
            self.build_skill(merged_data)
            self.progress.complete_phase("phase4_building")

            logger.info("\n" + "✅ " * 20)
            logger.info("Unified scraping complete!")
            logger.info("✅ " * 20 + "\n")

            logger.info(f"📁 Output: {self.output_dir}/")
            logger.info(f"📁 Data: {self.data_dir}/")

            self.progress.complete_task()

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  Scraping interrupted by user")
            self.progress.add_error("Interrupted by user")
            self.progress.fail_task("Interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"\n\n❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            self.progress.add_error(str(e))
            self.progress.fail_task(str(e))
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Unified multi-source scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with unified config
  skill-seekers unified --config configs/godot_unified.json

  # Override merge mode
  skill-seekers unified --config configs/react_unified.json --merge-mode claude-enhanced

  # Backward compatible with legacy configs
  skill-seekers unified --config configs/react.json
        """
    )

    parser.add_argument('--config', '-c', required=True,
                       help='Path to unified config JSON file')
    parser.add_argument('--merge-mode', '-m',
                       choices=['rule-based', 'claude-enhanced'],
                       help='Override config merge mode')

    args = parser.parse_args()

    # Create and run scraper
    scraper = UnifiedScraper(args.config, args.merge_mode)
    scraper.run()


if __name__ == '__main__':
    main()
