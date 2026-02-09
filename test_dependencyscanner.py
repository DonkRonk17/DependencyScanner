#!/usr/bin/env python3
"""
Comprehensive test suite for DependencyScanner.

Tests cover:
- Core functionality
- Edge cases
- Error handling
- Integration scenarios

Run: python test_dependencyscanner.py
Protocol: Bug Hunt Protocol (BUILD_PROTOCOL_V1.md Phase 5)
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dependencyscanner import (
    Dependency,
    DependencyParser,
    Scanner,
    ConflictDetector,
    DependencyAnalyzer,
    ReportGenerator,
    Tool,
    Conflict,
    ScanResult
)


class TestDependencyParser(unittest.TestCase):
    """Test DependencyParser functionality."""

    def test_parse_simple_requirement(self):
        """Test: Parse simple package requirement."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("requests==2.28.0\n")
            f.flush()
            
            deps = DependencyParser.parse_requirements_txt(Path(f.name))
            
            self.assertEqual(len(deps), 1)
            self.assertEqual(deps[0].package_name, "requests")
            self.assertEqual(deps[0].version_spec, "==2.28.0")

    def test_parse_version_range(self):
        """Test: Parse package with version range."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("click>=7.0,<9.0\n")
            f.flush()
            
            deps = DependencyParser.parse_requirements_txt(Path(f.name))
            
            self.assertEqual(len(deps), 1)
            self.assertEqual(deps[0].package_name, "click")
            self.assertEqual(deps[0].version_spec, ">=7.0,<9.0")

    def test_parse_with_extras(self):
        """Test: Parse package with extras."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("requests[security]>=2.28.0\n")
            f.flush()
            
            deps = DependencyParser.parse_requirements_txt(Path(f.name))
            
            self.assertEqual(len(deps), 1)
            self.assertEqual(deps[0].package_name, "requests")
            self.assertEqual(deps[0].extras, ["security"])

    def test_parse_git_url(self):
        """Test: Parse git URL dependency."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("git+https://github.com/user/repo.git\n")
            f.flush()
            
            deps = DependencyParser.parse_requirements_txt(Path(f.name))
            
            self.assertEqual(len(deps), 1)
            self.assertTrue(deps[0].is_git_url)

    def test_parse_editable(self):
        """Test: Parse editable install."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("-e .\n")
            f.flush()
            
            deps = DependencyParser.parse_requirements_txt(Path(f.name))
            
            self.assertEqual(len(deps), 1)
            self.assertTrue(deps[0].is_editable)

    def test_parse_comments(self):
        """Test: Skip comments and empty lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# Comment\n")
            f.write("\n")
            f.write("requests==2.28.0  # inline comment\n")
            f.flush()
            
            deps = DependencyParser.parse_requirements_txt(Path(f.name))
            
            self.assertEqual(len(deps), 1)
            self.assertEqual(deps[0].package_name, "requests")

    def test_parse_empty_file(self):
        """Test: Parse empty requirements.txt."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            f.flush()
            
            deps = DependencyParser.parse_requirements_txt(Path(f.name))
            
            self.assertEqual(len(deps), 0)


class TestScanner(unittest.TestCase):
    """Test Scanner functionality."""

    def test_discover_tools(self):
        """Test: Discover tools in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            
            # Create test tools
            tool1 = base_path / "Tool1"
            tool1.mkdir()
            (tool1 / "requirements.txt").write_text("requests==2.28.0\n")
            
            tool2 = base_path / "Tool2"
            tool2.mkdir()
            (tool2 / "setup.py").write_text("# setup\n")
            
            # Scan
            scanner = Scanner(base_path)
            tools = scanner.discover_tools()
            
            self.assertEqual(len(tools), 2)
            tool_names = [t.name for t in tools]
            self.assertIn("Tool1", tool_names)
            self.assertIn("Tool2", tool_names)

    def test_skip_excluded_dirs(self):
        """Test: Skip excluded directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            
            # Create excluded directory
            git_dir = base_path / ".git"
            git_dir.mkdir()
            (git_dir / "requirements.txt").write_text("something\n")
            
            # Scan
            scanner = Scanner(base_path)
            tools = scanner.discover_tools()
            
            self.assertEqual(len(tools), 0)

    def test_parse_dependencies_from_tool(self):
        """Test: Parse dependencies from discovered tool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            
            # Create tool with dependencies
            tool_dir = base_path / "TestTool"
            tool_dir.mkdir()
            (tool_dir / "requirements.txt").write_text("requests==2.28.0\nclick>=7.0\n")
            
            # Scan
            scanner = Scanner(base_path)
            tools = scanner.discover_tools()
            
            self.assertEqual(len(tools), 1)
            self.assertEqual(len(tools[0].dependencies), 2)


class TestConflictDetector(unittest.TestCase):
    """Test ConflictDetector functionality."""

    def test_detect_no_conflict(self):
        """Test: No conflict when versions compatible."""
        tool1 = Tool(name="Tool1", path=Path("."))
        tool1.dependencies = [
            Dependency(package_name="requests", version_spec=">=2.28.0")
        ]
        
        tool2 = Tool(name="Tool2", path=Path("."))
        tool2.dependencies = [
            Dependency(package_name="requests", version_spec=">=2.30.0")
        ]
        
        conflicts = ConflictDetector.detect_conflicts([tool1, tool2])
        
        # Should be a WARNING (different specs) but not CRITICAL
        self.assertTrue(len(conflicts) <= 1)
        if conflicts:
            self.assertEqual(conflicts[0].severity, "WARNING")

    def test_detect_hard_conflict(self):
        """Test: Detect hard conflict (different exact versions)."""
        tool1 = Tool(name="Tool1", path=Path("."))
        tool1.dependencies = [
            Dependency(package_name="requests", version_spec="==2.28.0")
        ]
        
        tool2 = Tool(name="Tool2", path=Path("."))
        tool2.dependencies = [
            Dependency(package_name="requests", version_spec="==2.31.0")
        ]
        
        conflicts = ConflictDetector.detect_conflicts([tool1, tool2])
        
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].severity, "CRITICAL")
        self.assertEqual(conflicts[0].package_name, "requests")

    def test_no_conflict_single_tool(self):
        """Test: No conflict with single tool."""
        tool1 = Tool(name="Tool1", path=Path("."))
        tool1.dependencies = [
            Dependency(package_name="requests", version_spec="==2.28.0")
        ]
        
        conflicts = ConflictDetector.detect_conflicts([tool1])
        
        self.assertEqual(len(conflicts), 0)

    def test_skip_git_urls(self):
        """Test: Skip git URL dependencies in conflict detection."""
        tool1 = Tool(name="Tool1", path=Path("."))
        tool1.dependencies = [
            Dependency(package_name="custom-pkg", version_spec="git", is_git_url=True)
        ]
        
        tool2 = Tool(name="Tool2", path=Path("."))
        tool2.dependencies = [
            Dependency(package_name="custom-pkg", version_spec="==1.0.0")
        ]
        
        conflicts = ConflictDetector.detect_conflicts([tool1, tool2])
        
        # Git URL should be skipped
        self.assertEqual(len(conflicts), 0)


class TestDependencyAnalyzer(unittest.TestCase):
    """Test DependencyAnalyzer functionality."""

    def test_analyze_empty(self):
        """Test: Analyze empty tool list."""
        stats = DependencyAnalyzer.analyze([])
        
        self.assertEqual(stats["total_dependencies"], 0)
        self.assertEqual(stats["unique_packages"], 0)

    def test_analyze_single_tool(self):
        """Test: Analyze single tool."""
        tool1 = Tool(name="Tool1", path=Path("."))
        tool1.dependencies = [
            Dependency(package_name="requests", version_spec="==2.28.0"),
            Dependency(package_name="click", version_spec=">=7.0")
        ]
        
        stats = DependencyAnalyzer.analyze([tool1])
        
        self.assertEqual(stats["total_dependencies"], 2)
        self.assertEqual(stats["unique_packages"], 2)

    def test_identify_stdlib_only_tools(self):
        """Test: Identify tools with zero dependencies."""
        tool1 = Tool(name="Tool1", path=Path("."))
        tool1.dependencies = []
        
        tool2 = Tool(name="Tool2", path=Path("."))
        tool2.dependencies = [
            Dependency(package_name="requests", version_spec="==2.28.0")
        ]
        
        stats = DependencyAnalyzer.analyze([tool1, tool2])
        
        self.assertIn("Tool1", stats["stdlib_only_tools"])
        self.assertNotIn("Tool2", stats["stdlib_only_tools"])

    def test_identify_heavy_tools(self):
        """Test: Identify tools with many dependencies."""
        tool1 = Tool(name="HeavyTool", path=Path("."))
        tool1.dependencies = [
            Dependency(package_name=f"pkg{i}", version_spec=">=1.0")
            for i in range(15)
        ]
        
        stats = DependencyAnalyzer.analyze([tool1])
        
        self.assertIn("HeavyTool", stats["heavy_tools"])

    def test_most_popular_packages(self):
        """Test: Identify most popular packages."""
        tool1 = Tool(name="Tool1", path=Path("."))
        tool1.dependencies = [
            Dependency(package_name="requests", version_spec=">=1.0")
        ]
        
        tool2 = Tool(name="Tool2", path=Path("."))
        tool2.dependencies = [
            Dependency(package_name="requests", version_spec=">=1.0")
        ]
        
        tool3 = Tool(name="Tool3", path=Path("."))
        tool3.dependencies = [
            Dependency(package_name="click", version_spec=">=1.0")
        ]
        
        stats = DependencyAnalyzer.analyze([tool1, tool2, tool3])
        
        most_popular = stats["most_popular_packages"]
        self.assertEqual(most_popular[0][0], "requests")
        self.assertEqual(most_popular[0][1], 2)


class TestReportGenerator(unittest.TestCase):
    """Test ReportGenerator functionality."""

    def setUp(self):
        """Set up test data."""
        from datetime import datetime
        
        tool1 = Tool(name="Tool1", path=Path("."))
        tool1.dependencies = [
            Dependency(package_name="requests", version_spec="==2.28.0")
        ]
        
        conflict = Conflict(
            package_name="requests",
            severity="CRITICAL",
            tools={"Tool1": "==2.28.0", "Tool2": "==2.31.0"}
        )
        
        self.scan_result = ScanResult(
            scan_date=datetime.now().isoformat(),
            tools_scanned=2,
            total_dependencies=2,
            unique_packages=1,
            conflicts=[conflict],
            tools=[tool1],
            statistics={
                "stdlib_only_tools": ["Tool3"],
                "light_tools": ["Tool1"],
                "heavy_tools": [],
                "most_popular_packages": [("requests", 2)]
            }
        )

    def test_generate_text_report(self):
        """Test: Generate text report."""
        report = ReportGenerator.generate_text_report(self.scan_result)
        
        self.assertIn("DEPENDENCYSCANNER REPORT", report)
        self.assertIn("Tools Scanned: 2", report)
        self.assertIn("CONFLICTS", report)

    def test_generate_json_report(self):
        """Test: Generate JSON report."""
        report = ReportGenerator.generate_json_report(self.scan_result)
        
        data = json.loads(report)
        self.assertEqual(data["tools_scanned"], 2)
        self.assertEqual(len(data["conflicts"]), 1)

    def test_generate_markdown_report(self):
        """Test: Generate Markdown report."""
        report = ReportGenerator.generate_markdown_report(self.scan_result)
        
        self.assertIn("# Dependency Scan Report", report)
        self.assertIn("## Conflicts", report)
        self.assertIn("### requests", report)


def run_tests():
    """Run all tests with nice output."""
    print("=" * 70)
    print("TESTING: DependencyScanner v1.0")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDependencyParser))
    suite.addTests(loader.loadTestsFromTestCase(TestScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestDependencyAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {result.testsRun} tests")
    print(f"[OK] Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    if result.failures:
        print(f"[X] Failed: {len(result.failures)}")
    if result.errors:
        print(f"[X] Errors: {len(result.errors)}")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
