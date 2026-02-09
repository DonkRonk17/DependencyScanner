#!/usr/bin/env python3
"""
DependencyScanner - Team Brain Tool Dependency Analyzer

Scans all Team Brain tools for Python dependencies, identifies conflicts,
generates comprehensive reports, and provides insights for dependency management.

Author: ATLAS (Team Brain)
For: Logan Smith / Metaphy LLC
Version: 1.0.0
Date: 2026-02-09
License: MIT
Protocol: BUILD_PROTOCOL_V1.md
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from packaging import version
from packaging.specifiers import SpecifierSet, InvalidSpecifier

# ASCII-safe status indicators (no Unicode emojis for Windows compatibility)
STATUS_OK = "[OK]"
STATUS_WARNING = "[!]"
STATUS_ERROR = "[X]"
STATUS_INFO = "[i]"

__version__ = "1.0.0"


@dataclass
class Dependency:
    """Represents a single Python package dependency."""
    package_name: str
    version_spec: str
    extras: List[str] = field(default_factory=list)
    source_file: str = ""
    is_git_url: bool = False
    is_editable: bool = False

    def __post_init__(self):
        """Normalize package name for consistent comparison."""
        self.package_name = self.package_name.lower().replace("_", "-")


@dataclass
class Tool:
    """Represents a Team Brain tool with its dependencies."""
    name: str
    path: Path
    dependencies: List[Dependency] = field(default_factory=list)
    has_requirements_txt: bool = False
    has_setup_py: bool = False
    parse_errors: List[str] = field(default_factory=list)


@dataclass
class Conflict:
    """Represents a dependency version conflict between tools."""
    package_name: str
    severity: str  # CRITICAL, WARNING
    tools: Dict[str, str]  # {tool_name: version_spec}
    description: str = ""


@dataclass
class ScanResult:
    """Complete scan results with all analysis."""
    scan_date: str
    tools_scanned: int
    total_dependencies: int
    unique_packages: int
    conflicts: List[Conflict]
    tools: List[Tool]
    statistics: Dict = field(default_factory=dict)


class DependencyParser:
    """Parse dependency files (requirements.txt, setup.py)."""

    # Regex patterns for requirements.txt parsing
    REQUIREMENT_PATTERN = re.compile(
        r'^([a-zA-Z0-9_-]+)'  # Package name
        r'(?:\[([a-zA-Z0-9_,-]+)\])?'  # Optional extras
        r'([><=!~]+[0-9a-zA-Z.,<>= *]+)?'  # Optional version spec (fixed: allow full range)
    )

    GIT_URL_PATTERN = re.compile(r'^git\+https?://')
    EDITABLE_PATTERN = re.compile(r'^-e\s+')

    @staticmethod
    def parse_requirements_txt(filepath: Path) -> List[Dependency]:
        """
        Parse a requirements.txt file.

        Args:
            filepath: Path to requirements.txt file

        Returns:
            List of Dependency objects

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        dependencies = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    # Skip comments and empty lines
                    line = line.split('#')[0].strip()
                    if not line:
                        continue

                    # Handle editable installs
                    is_editable = bool(DependencyParser.EDITABLE_PATTERN.match(line))
                    if is_editable:
                        line = DependencyParser.EDITABLE_PATTERN.sub('', line).strip()

                    # Handle git URLs
                    is_git = bool(DependencyParser.GIT_URL_PATTERN.match(line))
                    if is_git:
                        # Extract package name from git URL (simplified)
                        package_name = line.split('/')[-1].replace('.git', '')
                        dep = Dependency(
                            package_name=package_name,
                            version_spec="git",
                            source_file=str(filepath),
                            is_git_url=True,
                            is_editable=is_editable
                        )
                        dependencies.append(dep)
                        continue

                    # Handle editable "." (current directory)
                    if is_editable and line == ".":
                        dep = Dependency(
                            package_name="local-editable",
                            version_spec="",
                            source_file=str(filepath),
                            is_editable=True
                        )
                        dependencies.append(dep)
                        continue

                    # Parse standard requirement
                    match = DependencyParser.REQUIREMENT_PATTERN.match(line)
                    if match:
                        package_name = match.group(1)
                        extras_str = match.group(2)
                        version_spec = match.group(3) or ""

                        extras = []
                        if extras_str:
                            extras = [e.strip() for e in extras_str.split(',')]

                        dep = Dependency(
                            package_name=package_name,
                            version_spec=version_spec,
                            extras=extras,
                            source_file=str(filepath),
                            is_editable=is_editable
                        )
                        dependencies.append(dep)

        except FileNotFoundError:
            raise
        except Exception as e:
            print(f"{STATUS_ERROR} Error parsing {filepath}: {e}")
            raise

        return dependencies

    @staticmethod
    def parse_setup_py(filepath: Path) -> List[Dependency]:
        """
        Parse setup.py for install_requires (basic extraction).

        Args:
            filepath: Path to setup.py file

        Returns:
            List of Dependency objects

        Note:
            This is a simplified parser. Complex setup.py files may not be fully parsed.
        """
        dependencies = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple regex to extract install_requires list
            # This is NOT a full Python parser, just basic pattern matching
            pattern = r'install_requires\s*=\s*\[(.*?)\]'
            match = re.search(pattern, content, re.DOTALL)

            if match:
                requires_str = match.group(1)
                # Extract quoted strings
                package_pattern = r'["\']([^"\']+)["\']'
                packages = re.findall(package_pattern, requires_str)

                for pkg_spec in packages:
                    # Parse each package specification
                    match = DependencyParser.REQUIREMENT_PATTERN.match(pkg_spec)
                    if match:
                        package_name = match.group(1)
                        version_spec = match.group(3) or ""

                        dep = Dependency(
                            package_name=package_name,
                            version_spec=version_spec,
                            source_file=str(filepath)
                        )
                        dependencies.append(dep)

        except Exception as e:
            print(f"{STATUS_WARNING} Could not parse {filepath}: {e}")

        return dependencies


class Scanner:
    """Discover and scan tools in a directory."""

    def __init__(self, base_path: Path, exclusions: Optional[List[str]] = None):
        """
        Initialize scanner.

        Args:
            base_path: Base directory to scan for tools
            exclusions: List of directory names to exclude
        """
        self.base_path = Path(base_path)
        self.exclusions = exclusions or ['.git', 'node_modules', '__pycache__', 'venv', '.venv']

    def discover_tools(self) -> List[Tool]:
        """
        Discover all tools in the base directory.

        Returns:
            List of Tool objects

        Raises:
            FileNotFoundError: If base_path doesn't exist
        """
        if not self.base_path.exists():
            raise FileNotFoundError(f"Base path not found: {self.base_path}")

        tools = []

        # Walk directory tree
        for item in self.base_path.iterdir():
            if not item.is_dir():
                continue

            # Skip excluded directories
            if item.name in self.exclusions:
                continue

            # Check for dependency files
            req_file = item / "requirements.txt"
            setup_file = item / "setup.py"

            if req_file.exists() or setup_file.exists():
                tool = Tool(
                    name=item.name,
                    path=item,
                    has_requirements_txt=req_file.exists(),
                    has_setup_py=setup_file.exists()
                )

                # Parse requirements.txt
                if req_file.exists():
                    try:
                        deps = DependencyParser.parse_requirements_txt(req_file)
                        tool.dependencies.extend(deps)
                    except Exception as e:
                        tool.parse_errors.append(f"requirements.txt: {e}")

                # Parse setup.py
                if setup_file.exists():
                    try:
                        deps = DependencyParser.parse_setup_py(setup_file)
                        tool.dependencies.extend(deps)
                    except Exception as e:
                        tool.parse_errors.append(f"setup.py: {e}")

                tools.append(tool)

        return tools


class ConflictDetector:
    """Detect version conflicts between tool dependencies."""

    @staticmethod
    def detect_conflicts(tools: List[Tool]) -> List[Conflict]:
        """
        Detect dependency conflicts across tools.

        Args:
            tools: List of Tool objects to analyze

        Returns:
            List of Conflict objects
        """
        # Group dependencies by package name
        package_map: Dict[str, Dict[str, str]] = defaultdict(dict)

        for tool in tools:
            for dep in tool.dependencies:
                if dep.is_git_url or dep.is_editable:
                    continue  # Skip git URLs and editable installs

                package_name = dep.package_name
                package_map[package_name][tool.name] = dep.version_spec

        conflicts = []

        # Check each package for conflicts
        for package_name, tool_versions in package_map.items():
            if len(tool_versions) < 2:
                continue  # Need at least 2 tools to have a conflict

            # Check if versions are compatible
            conflict = ConflictDetector._check_compatibility(package_name, tool_versions)
            if conflict:
                conflicts.append(conflict)

        return conflicts

    @staticmethod
    def _check_compatibility(package_name: str, tool_versions: Dict[str, str]) -> Optional[Conflict]:
        """
        Check if version specifications are compatible.

        Args:
            package_name: Package name
            tool_versions: Dict of {tool_name: version_spec}

        Returns:
            Conflict object if incompatible, None otherwise
        """
        version_specs = list(tool_versions.values())

        # Remove empty version specs
        version_specs = [v for v in version_specs if v]

        if not version_specs:
            return None  # No version specs to compare

        # Try to parse version specs
        spec_sets = []
        for spec in version_specs:
            try:
                spec_set = SpecifierSet(spec)
                spec_sets.append(spec_set)
            except InvalidSpecifier:
                # Invalid version spec, treat as potential conflict
                pass

        # If we have multiple different specs, check for conflicts
        unique_specs = set(version_specs)
        if len(unique_specs) > 1:
            # Simple heuristic: if there are exact versions that differ, it's a conflict
            exact_versions = [v for v in version_specs if v.startswith('==')]
            if len(set(exact_versions)) > 1:
                return Conflict(
                    package_name=package_name,
                    severity="CRITICAL",
                    tools=tool_versions,
                    description=f"Multiple tools require different exact versions of {package_name}"
                )

            # Otherwise, it's a warning (potentially compatible)
            return Conflict(
                package_name=package_name,
                severity="WARNING",
                tools=tool_versions,
                description=f"Multiple tools have different version requirements for {package_name}"
            )

        return None


class DependencyAnalyzer:
    """Analyze dependencies and generate statistics."""

    @staticmethod
    def analyze(tools: List[Tool]) -> Dict:
        """
        Generate comprehensive dependency statistics.

        Args:
            tools: List of Tool objects

        Returns:
            Dictionary of statistics
        """
        stats = {
            "total_dependencies": 0,
            "unique_packages": set(),
            "package_usage": defaultdict(int),
            "version_distribution": defaultdict(lambda: defaultdict(int)),
            "stdlib_only_tools": [],
            "heavy_tools": [],  # 10+ dependencies
            "light_tools": [],  # 1-3 dependencies
            "zero_dependency_tools": [],
        }

        for tool in tools:
            num_deps = len([d for d in tool.dependencies if not d.is_git_url])
            stats["total_dependencies"] += num_deps

            if num_deps == 0:
                stats["zero_dependency_tools"].append(tool.name)
                stats["stdlib_only_tools"].append(tool.name)
            elif num_deps <= 3:
                stats["light_tools"].append(tool.name)
            elif num_deps >= 10:
                stats["heavy_tools"].append(tool.name)

            for dep in tool.dependencies:
                if dep.is_git_url:
                    continue

                package_name = dep.package_name
                stats["unique_packages"].add(package_name)
                stats["package_usage"][package_name] += 1
                stats["version_distribution"][package_name][dep.version_spec] += 1

        # Convert sets to lists for JSON serialization
        stats["unique_packages"] = len(stats["unique_packages"])

        # Sort package usage
        stats["most_popular_packages"] = sorted(
            stats["package_usage"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Identify fragmented packages (3+ different versions)
        stats["fragmented_packages"] = [
            (pkg, versions)
            for pkg, versions in stats["version_distribution"].items()
            if len(versions) >= 3
        ]

        return stats


class ReportGenerator:
    """Generate reports in various formats."""

    @staticmethod
    def generate_text_report(result: ScanResult) -> str:
        """Generate plain text report."""
        lines = []
        lines.append("=" * 80)
        lines.append("DEPENDENCYSCANNER REPORT".center(80))
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Date: {result.scan_date}")
        lines.append(f"Tools Scanned: {result.tools_scanned}")
        lines.append(f"Total Dependencies: {result.total_dependencies}")
        lines.append(f"Unique Packages: {result.unique_packages}")
        lines.append(f"Conflicts Found: {len(result.conflicts)}")
        lines.append("")

        # Conflicts
        if result.conflicts:
            lines.append("=" * 80)
            lines.append("CONFLICTS")
            lines.append("=" * 80)
            lines.append("")

            for conflict in result.conflicts:
                prefix = STATUS_ERROR if conflict.severity == "CRITICAL" else STATUS_WARNING
                lines.append(f"{prefix} {conflict.package_name} ({conflict.severity})")
                for tool_name, version_spec in conflict.tools.items():
                    lines.append(f"  - {tool_name}: {version_spec or '(any version)'}")
                lines.append("")

        # Statistics
        lines.append("=" * 80)
        lines.append("STATISTICS")
        lines.append("=" * 80)
        lines.append("")

        stats = result.statistics

        lines.append(f"Stdlib-Only Tools: {len(stats.get('stdlib_only_tools', []))}")
        lines.append(f"Light Tools (1-3 deps): {len(stats.get('light_tools', []))}")
        lines.append(f"Heavy Tools (10+ deps): {len(stats.get('heavy_tools', []))}")
        lines.append("")

        lines.append("Most Popular Packages:")
        for pkg, count in stats.get("most_popular_packages", [])[:10]:
            lines.append(f"  {count:3d}x  {pkg}")
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def generate_json_report(result: ScanResult) -> str:
        """Generate JSON report."""
        # Convert dataclasses to dicts
        data = asdict(result)
        
        # Convert Path objects to strings for JSON serialization
        for tool in data.get('tools', []):
            if 'path' in tool and isinstance(tool['path'], Path):
                tool['path'] = str(tool['path'])
        
        return json.dumps(data, indent=2)

    @staticmethod
    def generate_markdown_report(result: ScanResult) -> str:
        """Generate Markdown report."""
        lines = []
        lines.append("# Dependency Scan Report")
        lines.append("")
        lines.append(f"**Date:** {result.scan_date}")
        lines.append(f"**Tools Scanned:** {result.tools_scanned}")
        lines.append(f"**Total Dependencies:** {result.total_dependencies}")
        lines.append(f"**Unique Packages:** {result.unique_packages}")
        lines.append(f"**Conflicts Found:** {len(result.conflicts)}")
        lines.append("")

        # Conflicts
        if result.conflicts:
            lines.append("## Conflicts")
            lines.append("")

            for conflict in result.conflicts:
                lines.append(f"### {conflict.package_name} ({conflict.severity})")
                lines.append("")
                for tool_name, version_spec in conflict.tools.items():
                    lines.append(f"- **{tool_name}**: `{version_spec or 'any version'}`")
                lines.append("")

        # Statistics
        lines.append("## Statistics")
        lines.append("")

        stats = result.statistics

        lines.append(f"- **Stdlib-Only Tools:** {len(stats.get('stdlib_only_tools', []))}")
        lines.append(f"- **Light Tools (1-3 deps):** {len(stats.get('light_tools', []))}")
        lines.append(f"- **Heavy Tools (10+ deps):** {len(stats.get('heavy_tools', []))}")
        lines.append("")

        lines.append("### Most Popular Packages")
        lines.append("")
        for pkg, count in stats.get("most_popular_packages", [])[:10]:
            lines.append(f"- **{pkg}**: {count} tools")
        lines.append("")

        return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DependencyScanner - Analyze Python dependencies across Team Brain tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan                           # Scan default AutoProjects directory
  %(prog)s scan --path /custom/path       # Scan custom directory
  %(prog)s scan --format json             # Output as JSON
  %(prog)s scan --output report.json      # Save to file
  
For more information: https://github.com/DonkRonk17/DependencyScanner
        """
    )

    parser.add_argument(
        'command',
        choices=['scan', 'conflicts', 'stats', 'config'],
        help='Command to execute'
    )

    parser.add_argument(
        '--path',
        type=str,
        help='Path to tools directory (default: AutoProjects)'
    )

    parser.add_argument(
        '--format',
        choices=['text', 'json', 'markdown'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: stdout)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    args = parser.parse_args()

    # Determine scan path
    if args.path:
        scan_path = Path(args.path)
    else:
        # Default to AutoProjects
        scan_path = Path(__file__).parent.parent

    # Execute command
    if args.command == 'scan':
        try:
            # Scan tools
            print(f"{STATUS_INFO} Scanning {scan_path}...")
            scanner = Scanner(scan_path)
            tools = scanner.discover_tools()

            print(f"{STATUS_OK} Found {len(tools)} tools")

            # Detect conflicts
            print(f"{STATUS_INFO} Analyzing dependencies...")
            conflicts = ConflictDetector.detect_conflicts(tools)

            # Generate statistics
            stats = DependencyAnalyzer.analyze(tools)

            # Create scan result
            from datetime import datetime
            result = ScanResult(
                scan_date=datetime.now().isoformat(),
                tools_scanned=len(tools),
                total_dependencies=stats["total_dependencies"],
                unique_packages=stats["unique_packages"],
                conflicts=conflicts,
                tools=tools,
                statistics=stats
            )

            # Generate report
            if args.format == 'text':
                report = ReportGenerator.generate_text_report(result)
            elif args.format == 'json':
                report = ReportGenerator.generate_json_report(result)
            elif args.format == 'markdown':
                report = ReportGenerator.generate_markdown_report(result)

            # Output report
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"{STATUS_OK} Report saved to {args.output}")
            else:
                print()
                print(report)

            # Exit with appropriate code
            if conflicts:
                critical_conflicts = [c for c in conflicts if c.severity == "CRITICAL"]
                if critical_conflicts:
                    print(f"\n{STATUS_ERROR} {len(critical_conflicts)} critical conflicts found!")
                    return 2
                else:
                    print(f"\n{STATUS_WARNING} {len(conflicts)} warnings found")
                    return 1
            else:
                print(f"\n{STATUS_OK} No conflicts found!")
                return 0

        except Exception as e:
            print(f"{STATUS_ERROR} Scan failed: {e}", file=sys.stderr)
            return 2

    elif args.command == 'config':
        print("Config command not yet implemented")
        return 1

    elif args.command == 'conflicts':
        print("Conflicts command not yet implemented")
        return 1

    elif args.command == 'stats':
        print("Stats command not yet implemented")
        return 1


if __name__ == "__main__":
    sys.exit(main())
