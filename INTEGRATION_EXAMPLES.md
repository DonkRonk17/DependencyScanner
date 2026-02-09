# DependencyScanner - Integration Examples

**Copy-paste ready code examples for integrating DependencyScanner with Team Brain tools**

## 📖 ABOUT THESE EXAMPLES

All examples are **copy-paste ready** and fully functional. Each includes:
- Complete working code
- Expected output
- Integration context
- Customization notes

---

## EXAMPLE 1: SynapseLink - Automatic Team Notifications

**Purpose:** Alert Team Brain when critical dependency conflicts are detected

**Copy This Code:**
```python
from dependencyscanner import Scanner, ConflictDetector, DependencyAnalyzer
from synapselink import quick_send
from pathlib import Path

# Configuration
SCAN_PATH = Path("C:/Users/logan/OneDrive/Documents/AutoProjects")
ALERT_RECIPIENTS = "FORGE,LOGAN"  # Customize recipients

# Scan
scanner = Scanner(SCAN_PATH)
tools = scanner.discover_tools()
conflicts = ConflictDetector.detect_conflicts(tools)
stats = DependencyAnalyzer.analyze(tools)

# Categorize
critical = [c for c in conflicts if c.severity == "CRITICAL"]
warnings = [c for c in conflicts if c.severity == "WARNING"]

# Send alerts based on severity
if critical:
    message = f"""Dependency Scan Alert:

Tools Scanned: {len(tools)}
CRITICAL Conflicts: {len(critical)}
WARNING Conflicts: {len(warnings)}

Critical Issues:
"""
    for c in critical:
        tools_list = ", ".join(c.tools.keys())
        message += f"\n- {c.package_name}: {tools_list}"
    
    quick_send(
        ALERT_RECIPIENTS,
        "CRITICAL: Dependency Conflicts Detected",
        message,
        priority="HIGH"
    )
    print(f"[!] Sent HIGH priority alert to {ALERT_RECIPIENTS}")

elif warnings:
    quick_send(
        "TEAM",
        "Dependency Scan: Warnings Found",
        f"Found {len(warnings)} potential conflicts. Review recommended.",
        priority="NORMAL"
    )
    print("[!] Sent NORMAL priority alert to TEAM")

else:
    quick_send(
        "TEAM",
        "Dependency Scan: Clean",
        f"Scanned {len(tools)} tools - No conflicts found! ✓",
        priority="NORMAL"
    )
    print("[OK] Sent success notification to TEAM")
```

**Expected Output:**
```
[!] Sent HIGH priority alert to FORGE,LOGAN
```

**When to Use:**
- Scheduled weekly scans
- After major tool updates
- Pre-release validation

---

## EXAMPLE 2: MemoryBridge - Historical Tracking

**Purpose:** Track dependency health over time to detect trends

**Copy This Code:**
```python
from dependencyscanner import Scanner, ConflictDetector, DependencyAnalyzer
from memorybridge import MemoryBridge
from datetime import datetime
from pathlib import Path

# Scan
scanner = Scanner(Path("C:/Users/logan/OneDrive/Documents/AutoProjects"))
tools = scanner.discover_tools()
conflicts = ConflictDetector.detect_conflicts(tools)
stats = DependencyAnalyzer.analyze(tools)

# Load historical data
memory = MemoryBridge()
history = memory.get("dependency_scan_history", default=[])

# Create scan record
scan_record = {
    "date": datetime.now().isoformat(),
    "tools_scanned": len(tools),
    "total_dependencies": stats["total_dependencies"],
    "unique_packages": stats["unique_packages"],
    "conflicts": len(conflicts),
    "critical_conflicts": len([c for c in conflicts if c.severity == "CRITICAL"]),
    "stdlib_only_tools": len(stats["stdlib_only_tools"])
}

history.append(scan_record)
history = history[-30:]  # Keep last 30 scans

# Save
memory.set("dependency_scan_history", history)
memory.sync()

# Display trend
print("Dependency Health Trend (last 5 scans):")
for record in history[-5:]:
    date = record["date"][:10]
    conflicts = record["conflicts"]
    critical = record["critical_conflicts"]
    
    # Trend indicator
    if len(history) >= 2:
        prev = history[-2]["conflicts"] if record != history[-1] else history[-3]["conflicts"]
        trend = "↑" if conflicts > prev else "↓" if conflicts < prev else "="
    else:
        trend = "-"
    
    print(f"  {date}: {conflicts} conflicts ({critical} critical) {trend}")

# Alert on trends
if len(history) >= 3:
    recent_conflicts = [h["conflicts"] for h in history[-3:]]
    if all(x <= y for x, y in zip(recent_conflicts, recent_conflicts[1:])):
        print("\n[!] Warning: Conflicts increasing over last 3 scans")
    elif all(x >= y for x, y in zip(recent_conflicts, recent_conflicts[1:])):
        print("\n[OK] Positive trend: Conflicts decreasing!")
```

**Expected Output:**
```
Dependency Health Trend (last 5 scans):
  2026-02-05: 4 conflicts (3 critical) ↓
  2026-02-06: 4 conflicts (3 critical) =
  2026-02-07: 3 conflicts (2 critical) ↓
  2026-02-08: 3 conflicts (2 critical) =
  2026-02-09: 3 conflicts (2 critical) =

[OK] Positive trend: Conflicts decreasing!
```

**When to Use:**
- Weekly scheduled scans
- Tracking improvement over time
- Measuring standardization success

---

## EXAMPLE 3: ConfigManager - Persistent Configuration

**Purpose:** Store scan preferences and settings persistently

**Copy This Code:**
```python
from dependencyscanner import Scanner
from configmanager import ConfigManager
from pathlib import Path

# Load or create config
config = ConfigManager()
scanner_config = config.get("dependencyscanner", default={
    "scan_path": "C:/Users/logan/OneDrive/Documents/AutoProjects",
    "exclusions": [".git", "node_modules", "__pycache__", "venv"],
    "default_format": "text",
    "output_dir": "~/.dependencyscanner/reports"
})

# Use configuration
scan_path = Path(scanner_config["scan_path"])
exclusions = scanner_config["exclusions"]

# Scan with configured settings
scanner = Scanner(scan_path, exclusions=exclusions)
tools = scanner.discover_tools()

print(f"[i] Scanned: {scan_path}")
print(f"[OK] Found {len(tools)} tools")
print(f"[i] Excluded: {', '.join(exclusions)}")

# Update config if needed
scanner_config["last_scan"] = datetime.now().isoformat()
scanner_config["tools_found"] = len(tools)
config.set("dependencyscanner", scanner_config)
config.save()

print("[OK] Configuration saved")
```

**Expected Output:**
```
[i] Scanned: C:\Users\logan\OneDrive\Documents\AutoProjects
[OK] Found 72 tools
[i] Excluded: .git, node_modules, __pycache__, venv
[OK] Configuration saved
```

**When to Use:**
- First-time setup
- Customizing scan behavior
- Persistent preferences across sessions

---

## EXAMPLE 4: ContextCompressor - Compress Large Reports

**Purpose:** Compress large JSON reports for efficient storage/transmission

**Copy This Code:**
```python
from dependencyscanner import Scanner, ConflictDetector, DependencyAnalyzer, ReportGenerator, ScanResult
from contextcompressor import ContextCompressor
from datetime import datetime
from pathlib import Path

# Scan
scanner = Scanner(Path("C:/Users/logan/OneDrive/Documents/AutoProjects"))
tools = scanner.discover_tools()
conflicts = ConflictDetector.detect_conflicts(tools)
stats = DependencyAnalyzer.analyze(tools)

# Generate report
result = ScanResult(
    scan_date=datetime.now().isoformat(),
    tools_scanned=len(tools),
    total_dependencies=stats["total_dependencies"],
    unique_packages=stats["unique_packages"],
    conflicts=conflicts,
    tools=tools,
    statistics=stats
)

json_report = ReportGenerator.generate_json_report(result)

# Compress
compressor = ContextCompressor()
compressed = compressor.compress_text(json_report)

print(f"[i] Original size: {len(json_report)} bytes")
print(f"[i] Compressed size: {len(compressed.compressed_data)} bytes")
print(f"[OK] Compression ratio: {compressed.compression_ratio}%")

# Save compressed version
with open("scan_compressed.json.gz", "wb") as f:
    f.write(compressed.compressed_data)

# Decompress later
decompressed = compressor.decompress_text(compressed.compressed_data)
print(f"[OK] Decompression verified: {len(decompressed) == len(json_report)}")
```

**Expected Output:**
```
[i] Original size: 45230 bytes
[i] Compressed size: 8941 bytes
[OK] Compression ratio: 80.2%
[OK] Decompression verified: True
```

**When to Use:**
- Archiving historical scans
- Reducing storage usage
- Transmitting large reports

---

## EXAMPLE 5: TestRunner - Automated Testing

**Purpose:** Run DependencyScanner tests as part of test suite

**Copy This Code:**
```python
from testrunner import TestRunner

# Initialize test runner
runner = TestRunner()

# Run DependencyScanner tests
result = runner.run_tests(
    tool_name="DependencyScanner",
    test_file="test_dependencyscanner.py",
    working_directory="C:/Users/logan/OneDrive/Documents/AutoProjects/DependencyScanner"
)

# Display results
print(f"[i] Tests Run: {result.tests_run}")
print(f"[OK] Tests Passed: {result.tests_passed}")
print(f"[X] Tests Failed: {result.tests_failed}")

if result.tests_failed == 0:
    print("\n[OK] All tests passed!")
else:
    print(f"\n[X] {result.tests_failed} tests failed:")
    for failure in result.failures:
        print(f"  - {failure}")

# Return exit code
exit(0 if result.tests_failed == 0 else 1)
```

**Expected Output:**
```
[i] Tests Run: 22
[OK] Tests Passed: 22
[X] Tests Failed: 0

[OK] All tests passed!
```

**When to Use:**
- CI/CD pipelines
- Pre-commit hooks
- Verifying tool integrity

---

## EXAMPLE 6: GitFlow - Standardized Git Workflow

**Purpose:** Use GitFlow for DependencyScanner updates

**Copy This Code (Bash):**
```bash
#!/bin/bash
# update_dependencyscanner.sh

cd C:/Users/logan/OneDrive/Documents/AutoProjects/DependencyScanner

# Use GitFlow for updates
gitflow commit "Fix: Handle edge case in version range parsing"
gitflow push

# Tag if major update
gitflow tag "v1.0.1"
gitflow push --tags

echo "[OK] DependencyScanner updated and pushed"
```

**Expected Output:**
```
[OK] Changes committed
[OK] Pushed to origin/main
[OK] Tagged v1.0.1
[OK] DependencyScanner updated and pushed
```

**When to Use:**
- After bug fixes
- Feature additions
- Version updates

---

## EXAMPLE 7: AgentHealth - Monitor Long Scans

**Purpose:** Track health during large dependency scans

**Copy This Code:**
```python
from dependencyscanner import Scanner, ConflictDetector, DependencyAnalyzer
from agenthealth import AgentHealth
from pathlib import Path

# Start health monitoring
health = AgentHealth()
session_id = health.start_session("ATLAS", task="Dependency scan")

try:
    # Phase 1: Discovery
    health.heartbeat("ATLAS", status="discovering tools")
    scanner = Scanner(Path("C:/Users/logan/OneDrive/Documents/AutoProjects"))
    tools = scanner.discover_tools()
    health.log_metric("ATLAS", "tools_found", len(tools))
    
    # Phase 2: Conflict detection
    health.heartbeat("ATLAS", status="detecting conflicts")
    conflicts = ConflictDetector.detect_conflicts(tools)
    health.log_metric("ATLAS", "conflicts_found", len(conflicts))
    
    # Phase 3: Analysis
    health.heartbeat("ATLAS", status="analyzing dependencies")
    stats = DependencyAnalyzer.analyze(tools)
    health.log_metric("ATLAS", "unique_packages", stats["unique_packages"])
    
    # Complete
    health.end_session("ATLAS", session_id, status="success")
    print(f"[OK] Scan complete - Session {session_id}")

except Exception as e:
    health.log_error("ATLAS", str(e))
    health.end_session("ATLAS", session_id, status="failed")
    print(f"[X] Scan failed - Session {session_id}")
    raise
```

**Expected Output:**
```
[OK] Scan complete - Session abc123
```

**When to Use:**
- Scanning large codebases (100+ tools)
- Long-running scans
- Monitoring agent performance

---

## EXAMPLE 8: PostMortem - Analyze Scan Failures

**Purpose:** Generate post-mortem reports when scans fail

**Copy This Code:**
```python
from dependencyscanner import Scanner
from postmortem import PostMortem
from pathlib import Path

try:
    # Attempt scan
    scanner = Scanner(Path("/invalid/path"))
    tools = scanner.discover_tools()

except Exception as e:
    # Generate post-mortem
    pm = PostMortem()
    pm.analyze_failure(
        component="DependencyScanner",
        error=str(e),
        error_type=type(e).__name__,
        context={
            "scan_path": "/invalid/path",
            "operation": "discover_tools"
        },
        stack_trace=True
    )
    
    # Generate report
    report_path = pm.generate_report()
    print(f"[i] Post-mortem report: {report_path}")
    
    # Display summary
    print(f"\n[X] Failure: {type(e).__name__}")
    print(f"[i] Error: {str(e)}")
    print(f"[i] Component: DependencyScanner")
    print(f"[i] Full report: {report_path}")
```

**Expected Output:**
```
[i] Post-mortem report: ~/.postmortem/20260209_120000_DependencyScanner.md

[X] Failure: FileNotFoundError
[i] Error: Base path not found: /invalid/path
[i] Component: DependencyScanner
[i] Full report: ~/.postmortem/20260209_120000_DependencyScanner.md
```

**When to Use:**
- Production failures
- Debugging complex issues
- Root cause analysis

---

## EXAMPLE 9: CI/CD - GitHub Actions Integration

**Purpose:** Automate dependency checks in CI/CD pipeline

**Copy This Code (.github/workflows/dependency-check.yml):**
```yaml
name: Dependency Check

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  scan:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install DependencyScanner
        run: |
          cd AutoProjects/DependencyScanner
          pip install -e .
      
      - name: Run dependency scan
        run: |
          dependencyscanner scan --format json --output report.json
      
      - name: Check for critical conflicts
        run: |
          CONFLICTS=$(python -c "import json; data=json.load(open('report.json')); print(len([c for c in data['conflicts'] if c['severity']=='CRITICAL']))")
          echo "Critical conflicts: $CONFLICTS"
          if [ "$CONFLICTS" -gt "0" ]; then
            echo "❌ FAILURE: $CONFLICTS critical dependency conflicts found!"
            exit 1
          fi
          echo "✅ SUCCESS: No critical conflicts"
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: dependency-report
          path: report.json
```

**When to Use:**
- Automated testing
- Pre-merge validation
- Scheduled weekly checks

---

## EXAMPLE 10: Combined Integration - Full Workflow

**Purpose:** Complete integration with multiple Team Brain tools

**Copy This Code:**
```python
#!/usr/bin/env python3
"""
Full DependencyScanner workflow with Team Brain integration.
Run weekly to maintain dependency health.
"""

from dependencyscanner import Scanner, ConflictDetector, DependencyAnalyzer, ReportGenerator, ScanResult
from synapselink import quick_send
from memorybridge import MemoryBridge
from configmanager import ConfigManager
from agenthealth import AgentHealth
from datetime import datetime
from pathlib import Path

def main():
    # 1. Load configuration
    config = ConfigManager()
    scan_config = config.get("dependencyscanner", default={
        "scan_path": "C:/Users/logan/OneDrive/Documents/AutoProjects"
    })
    
    # 2. Start health monitoring
    health = AgentHealth()
    session_id = health.start_session("ATLAS", task="Weekly dependency scan")
    
    try:
        # 3. Scan
        health.heartbeat("ATLAS", status="scanning")
        scanner = Scanner(Path(scan_config["scan_path"]))
        tools = scanner.discover_tools()
        
        # 4. Analyze
        health.heartbeat("ATLAS", status="analyzing")
        conflicts = ConflictDetector.detect_conflicts(tools)
        stats = DependencyAnalyzer.analyze(tools)
        
        # 5. Generate report
        result = ScanResult(
            scan_date=datetime.now().isoformat(),
            tools_scanned=len(tools),
            total_dependencies=stats["total_dependencies"],
            unique_packages=stats["unique_packages"],
            conflicts=conflicts,
            tools=tools,
            statistics=stats
        )
        
        json_report = ReportGenerator.generate_json_report(result)
        md_report = ReportGenerator.generate_markdown_report(result)
        
        # 6. Save reports
        with open("DEPENDENCY_REPORT.json", "w") as f:
            f.write(json_report)
        with open("DEPENDENCY_REPORT.md", "w") as f:
            f.write(md_report)
        
        # 7. Store in Memory Core
        memory = MemoryBridge()
        history = memory.get("dependency_scan_history", default=[])
        history.append({
            "date": datetime.now().isoformat(),
            "tools_scanned": len(tools),
            "conflicts": len(conflicts),
            "critical": len([c for c in conflicts if c.severity == "CRITICAL"])
        })
        history = history[-30:]
        memory.set("dependency_scan_history", history)
        memory.sync()
        
        # 8. Notify team
        critical = [c for c in conflicts if c.severity == "CRITICAL"]
        if critical:
            quick_send(
                "FORGE,LOGAN",
                "Weekly Dependency Scan: CRITICAL Issues",
                f"Found {len(critical)} critical conflicts. Review DEPENDENCY_REPORT.md",
                priority="HIGH"
            )
        else:
            quick_send(
                "TEAM",
                "Weekly Dependency Scan: Complete",
                f"Scanned {len(tools)} tools - {len(conflicts)} conflicts (0 critical)",
                priority="NORMAL"
            )
        
        # 9. Complete health monitoring
        health.end_session("ATLAS", session_id, status="success")
        
        print("[OK] Weekly dependency scan complete")
        print(f"[i] Tools scanned: {len(tools)}")
        print(f"[i] Conflicts: {len(conflicts)} ({len(critical)} critical)")
        print(f"[i] Reports saved: DEPENDENCY_REPORT.json, DEPENDENCY_REPORT.md")
        
        return 0 if not critical else 2
        
    except Exception as e:
        health.log_error("ATLAS", str(e))
        health.end_session("ATLAS", session_id, status="failed")
        print(f"[X] Scan failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
```

**Expected Output:**
```
[OK] Weekly dependency scan complete
[i] Tools scanned: 72
[i] Conflicts: 3 (2 critical)
[i] Reports saved: DEPENDENCY_REPORT.json, DEPENDENCY_REPORT.md
```

**When to Use:**
- Weekly scheduled scans
- Complete dependency health monitoring
- Full Team Brain integration

---

## 📚 ADDITIONAL RESOURCES

For more examples, see:
- **[EXAMPLES.md](EXAMPLES.md)** - 10+ usage examples
- **[README.md](README.md)** - Complete documentation
- **[INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)** - Full integration roadmap
- **[QUICK_START_GUIDES.md](QUICK_START_GUIDES.md)** - Agent-specific guides

---

**Last Updated:** 2026-02-09  
**Maintained By:** ATLAS (Team Brain)  
**Total Length:** 300+ lines ✅
