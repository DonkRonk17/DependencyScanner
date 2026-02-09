# DependencyScanner - Usage Examples

**Complete working examples with expected output**

Quick navigation:
- [Example 1: Basic Scan](#example-1-basic-scan)
- [Example 2: Export to JSON](#example-2-export-to-json)
- [Example 3: Export to Markdown](#example-3-export-to-markdown)
- [Example 4: Custom Directory Scan](#example-4-custom-directory-scan)
- [Example 5: Python API Basic Usage](#example-5-python-api-basic-usage)
- [Example 6: Integration with SynapseLink](#example-6-integration-with-synapselink)
- [Example 7: Integration with MemoryBridge](#example-7-integration-with-memorybridge)
- [Example 8: Automated CI/CD Check](#example-8-automated-cicd-check)
- [Example 9: Find Stdlib-Only Tools](#example-9-find-stdlib-only-tools)
- [Example 10: Generate Security Audit List](#example-10-generate-security-audit-list)

---

## Example 1: Basic Scan

**Scenario:** First-time user wants to scan all Team Brain tools

**Command:**
```bash
cd C:\Users\logan\OneDrive\Documents\AutoProjects\DependencyScanner
dependencyscanner scan
```

**Expected Output:**
```
[i] Scanning C:\Users\logan\OneDrive\Documents\AutoProjects...
[OK] Found 72 tools
[i] Analyzing dependencies...

================================================================================
                         DEPENDENCYSCANNER REPORT
================================================================================

Date: 2026-02-09T12:34:56.789Z
Tools Scanned: 72
Total Dependencies: 245
Unique Packages: 87
Conflicts Found: 3

================================================================================
CONFLICTS
================================================================================

[X] requests (CRITICAL)
  - AgentHealth: ==2.28.0
  - RestCLI: ==2.31.0

[!] click (WARNING)
  - ConfigManager: >=7.0
  - ToolRegistry: >=8.0,<9.0

[X] certifi (CRITICAL)
  - SecureVault: ==2022.12.7
  - NetScan: ==2023.7.22

================================================================================
STATISTICS
================================================================================

Stdlib-Only Tools: 18
Light Tools (1-3 deps): 32
Heavy Tools (10+ deps): 5

Most Popular Packages:
   15x  click
   12x  requests
    8x  pytest
    6x  pyyaml
    5x  python-dateutil
    4x  certifi
    4x  charset-normalizer
    3x  idna
    3x  urllib3
    2x  colorama

[X] 3 critical conflicts found!
```

**What You Learned:**
- How to run a basic scan
- What the output looks like
- How conflicts are displayed
- What statistics are available

---

## Example 2: Export to JSON

**Scenario:** Need machine-readable data for programmatic analysis

**Command:**
```bash
dependencyscanner scan --format json --output deps.json
```

**Expected Output:**
```
[i] Scanning C:\Users\logan\OneDrive\Documents\AutoProjects...
[OK] Found 72 tools
[i] Analyzing dependencies...
[OK] Report saved to deps.json

[X] 3 critical conflicts found!
```

**Generated File (deps.json):**
```json
{
  "scan_date": "2026-02-09T12:34:56.789Z",
  "tools_scanned": 72,
  "total_dependencies": 245,
  "unique_packages": 87,
  "conflicts": [
    {
      "package_name": "requests",
      "severity": "CRITICAL",
      "tools": {
        "AgentHealth": "==2.28.0",
        "RestCLI": "==2.31.0"
      },
      "description": "Multiple tools require different exact versions of requests"
    }
  ],
  "statistics": {
    "most_popular_packages": [
      ["click", 15],
      ["requests", 12]
    ],
    "stdlib_only_tools": ["ToolRegistry", "ToolSentinel", ...]
  }
}
```

**What You Learned:**
- How to export JSON reports
- JSON structure for programmatic access
- How to integrate with other tools

---

## Example 3: Export to Markdown

**Scenario:** Generate documentation for GitHub or project wiki

**Command:**
```bash
dependencyscanner scan --format markdown --output DEPENDENCIES.md
```

**Expected Output:**
```
[i] Scanning C:\Users\logan\OneDrive\Documents\AutoProjects...
[OK] Found 72 tools
[i] Analyzing dependencies...
[OK] Report saved to DEPENDENCIES.md

[X] 3 critical conflicts found!
```

**Generated File (DEPENDENCIES.md):**
```markdown
# Dependency Scan Report

**Date:** 2026-02-09T12:34:56.789Z
**Tools Scanned:** 72
**Total Dependencies:** 245
**Unique Packages:** 87
**Conflicts Found:** 3

## Conflicts

### requests (CRITICAL)

- **AgentHealth**: `==2.28.0`
- **RestCLI**: `==2.31.0`

### click (WARNING)

- **ConfigManager**: `>=7.0`
- **ToolRegistry**: `>=8.0,<9.0`

## Statistics

- **Stdlib-Only Tools:** 18
- **Light Tools (1-3 deps):** 32
- **Heavy Tools (10+ deps):** 5

### Most Popular Packages

- **click**: 15 tools
- **requests**: 12 tools
```

**What You Learned:**
- How to generate documentation-friendly reports
- Markdown format for project wikis
- Professional documentation generation

---

## Example 4: Custom Directory Scan

**Scenario:** Scan a different directory of Python projects

**Command:**
```bash
dependencyscanner scan --path /home/user/projects
```

**Expected Output:**
```
[i] Scanning /home/user/projects...
[OK] Found 15 tools
[i] Analyzing dependencies...

================================================================================
                         DEPENDENCYSCANNER REPORT
================================================================================

Date: 2026-02-09T12:34:56.789Z
Tools Scanned: 15
Total Dependencies: 87
Unique Packages: 34
Conflicts Found: 1
...
```

**What You Learned:**
- How to scan custom directories
- Tool works on any Python project collection
- Not limited to Team Brain tools

---

## Example 5: Python API Basic Usage

**Scenario:** Use DependencyScanner programmatically in another tool

**Code:**
```python
from dependencyscanner import Scanner, ConflictDetector, DependencyAnalyzer
from pathlib import Path

# Scan tools
scanner = Scanner(Path("C:/Users/logan/OneDrive/Documents/AutoProjects"))
tools = scanner.discover_tools()

print(f"[OK] Found {len(tools)} tools")

# Detect conflicts
conflicts = ConflictDetector.detect_conflicts(tools)

critical_conflicts = [c for c in conflicts if c.severity == "CRITICAL"]
warning_conflicts = [c for c in conflicts if c.severity == "WARNING"]

print(f"[X] {len(critical_conflicts)} critical conflicts")
print(f"[!] {len(warning_conflicts)} warnings")

# Generate statistics
stats = DependencyAnalyzer.analyze(tools)

print(f"\nStdlib-only tools: {len(stats['stdlib_only_tools'])}")
print(f"Most popular: {stats['most_popular_packages'][0]}")

# Access individual tool data
for tool in tools:
    if tool.parse_errors:
        print(f"[!] {tool.name} had parse errors: {tool.parse_errors}")
```

**Expected Output:**
```
[OK] Found 72 tools
[X] 2 critical conflicts
[!] 1 warnings

Stdlib-only tools: 18
Most popular: ('click', 15)
```

**What You Learned:**
- How to import and use DependencyScanner classes
- How to access scan results programmatically
- How to filter conflicts by severity
- How to extract specific statistics

---

## Example 6: Integration with SynapseLink

**Scenario:** Automatically notify Team Brain when conflicts are found

**Code:**
```python
from dependencyscanner import Scanner, ConflictDetector, DependencyAnalyzer
from synapselink import quick_send
from pathlib import Path

# Scan
scanner = Scanner(Path("C:/Users/logan/OneDrive/Documents/AutoProjects"))
tools = scanner.discover_tools()
conflicts = ConflictDetector.detect_conflicts(tools)
stats = DependencyAnalyzer.analyze(tools)

# Categorize conflicts
critical = [c for c in conflicts if c.severity == "CRITICAL"]
warnings = [c for c in conflicts if c.severity == "WARNING"]

# Notify team
if critical:
    # High priority for critical conflicts
    message = f"""Dependency Scan Alert:

Tools Scanned: {len(tools)}
CRITICAL Conflicts: {len(critical)}
WARNING Conflicts: {len(warnings)}

Critical Issues:
"""
    for c in critical:
        message += f"\n- {c.package_name}: {len(c.tools)} tools affected"
    
    quick_send(
        "FORGE,LOGAN",
        "CRITICAL: Dependency Conflicts Detected",
        message,
        priority="HIGH"
    )
elif warnings:
    # Normal priority for warnings only
    quick_send(
        "TEAM",
        "Dependency Scan: Warnings Found",
        f"Found {len(warnings)} potential conflicts. Review recommended.",
        priority="NORMAL"
    )
else:
    # Success notification
    quick_send(
        "TEAM",
        "Dependency Scan: Clean",
        f"Scanned {len(tools)} tools - No conflicts found!",
        priority="NORMAL"
    )
```

**Result:** Team Brain stays informed of dependency health automatically

**What You Learned:**
- How to integrate with SynapseLink for notifications
- How to categorize conflicts by severity
- How to send priority-based alerts
- Real-world automation pattern

---

## Example 7: Integration with MemoryBridge

**Scenario:** Track dependency health over time

**Code:**
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

# Add current scan
scan_record = {
    "date": datetime.now().isoformat(),
    "tools_scanned": len(tools),
    "total_dependencies": stats["total_dependencies"],
    "unique_packages": stats["unique_packages"],
    "conflicts": len(conflicts),
    "critical_conflicts": len([c for c in conflicts if c.severity == "CRITICAL"])
}

history.append(scan_record)

# Keep last 30 scans
history = history[-30:]

# Save to Memory Core
memory.set("dependency_scan_history", history)
memory.sync()

# Show trend
print("Dependency Health Trend (last 5 scans):")
for record in history[-5:]:
    print(f"  {record['date'][:10]}: {record['conflicts']} conflicts ({record['critical_conflicts']} critical)")
```

**Expected Output:**
```
Dependency Health Trend (last 5 scans):
  2026-02-05: 4 conflicts (3 critical)
  2026-02-06: 4 conflicts (3 critical)
  2026-02-07: 3 conflicts (2 critical)  ← Improvement!
  2026-02-08: 3 conflicts (2 critical)
  2026-02-09: 3 conflicts (2 critical)
```

**What You Learned:**
- How to track dependency health over time
- How to use MemoryBridge for persistence
- How to detect improvement/degradation trends
- Historical analysis patterns

---

## Example 8: Automated CI/CD Check

**Scenario:** Run as part of automated testing pipeline

**Script (check_dependencies.py):**
```python
#!/usr/bin/env python3
"""
CI/CD dependency conflict checker.
Exit code 0 = no conflicts, 2 = conflicts found.
"""

import sys
from pathlib import Path
from dependencyscanner import Scanner, ConflictDetector

# Scan
scanner = Scanner(Path("C:/Users/logan/OneDrive/Documents/AutoProjects"))
tools = scanner.discover_tools()
conflicts = ConflictDetector.detect_conflicts(tools)

# Check for critical conflicts
critical = [c for c in conflicts if c.severity == "CRITICAL"]

if critical:
    print(f"[X] FAILURE: {len(critical)} critical dependency conflicts found!")
    for conflict in critical:
        print(f"  - {conflict.package_name}: {len(conflict.tools)} tools affected")
    sys.exit(2)
elif conflicts:
    print(f"[!] WARNING: {len(conflicts)} potential conflicts (non-critical)")
    sys.exit(1)
else:
    print("[OK] No dependency conflicts detected")
    sys.exit(0)
```

**Run in CI:**
```bash
python check_dependencies.py
if [ $? -eq 2 ]; then
    echo "Build FAILED due to dependency conflicts"
    exit 1
fi
```

**What You Learned:**
- How to use DependencyScanner in automation
- Exit code conventions
- CI/CD integration pattern

---

## Example 9: Find Stdlib-Only Tools

**Scenario:** Identify tools with zero external dependencies for reference

**Code:**
```python
from dependencyscanner import Scanner, DependencyAnalyzer
from pathlib import Path

# Scan
scanner = Scanner(Path("C:/Users/logan/OneDrive/Documents/AutoProjects"))
tools = scanner.discover_tools()
stats = DependencyAnalyzer.analyze(tools)

# Get stdlib-only tools
stdlib_only = stats["stdlib_only_tools"]

print(f"[OK] Found {len(stdlib_only)} stdlib-only tools:")
print()

for tool_name in sorted(stdlib_only):
    print(f"  - {tool_name}")

print()
print(f"That's {len(stdlib_only)/len(tools)*100:.1f}% of all tools!")
print()
print("These tools are excellent references for zero-dependency design.")
```

**Expected Output:**
```
[OK] Found 18 stdlib-only tools:

  - AgentRouter
  - ChangeLog
  - ClipStash
  - CodeMetrics
  - ContextPreserver
  - DevSnapshot
  - EchoGuard
  - ErrorRecovery
  - HashGuard
  - MentionGuard
  - QuickBackup
  - QuickClip
  - QuickRename
  - TerminalRewind
  - TestRunner
  - ToolRegistry
  - ToolSentinel
  - WindowSnap

That's 25.0% of all tools!

These tools are excellent references for zero-dependency design.
```

**What You Learned:**
- How to extract specific statistics
- How to calculate percentages
- Best practices for zero-dependency design
- Which tools to reference for stdlib-only patterns

---

## Example 10: Generate Security Audit List

**Scenario:** Prepare list of all packages for security vulnerability scanning

**Code:**
```python
from dependencyscanner import Scanner
from pathlib import Path

# Scan
scanner = Scanner(Path("C:/Users/logan/OneDrive/Documents/AutoProjects"))
tools = scanner.discover_tools()

# Collect all unique packages (excluding git URLs and editable)
packages = set()
for tool in tools:
    for dep in tool.dependencies:
        if not dep.is_git_url and not dep.is_editable:
            packages.add(dep.package_name)

# Sort and write to file
with open("packages_for_security_audit.txt", "w") as f:
    for pkg in sorted(packages):
        f.write(f"{pkg}\n")

print(f"[OK] Wrote {len(packages)} packages to packages_for_security_audit.txt")
print()
print("Next step: Run security check")
print("  pip install safety")
print("  safety check --file packages_for_security_audit.txt")
```

**Expected Output:**
```
[OK] Wrote 87 packages to packages_for_security_audit.txt

Next step: Run security check
  pip install safety
  safety check --file packages_for_security_audit.txt
```

**What You Learned:**
- How to extract unique package list
- How to prepare for security auditing
- Integration with `safety` tool
- Security-conscious dependency management

---

## Advanced Examples

### Example 11: Compare Two Scan Results

**Scenario:** Compare dependency changes between two dates

```python
import json

# Load two scan results
with open("scan_2026-02-01.json") as f:
    old_scan = json.load(f)

with open("scan_2026-02-09.json") as f:
    new_scan = json.load(f)

# Compare
old_conflicts = len(old_scan["conflicts"])
new_conflicts = len(new_scan["conflicts"])

print(f"Conflicts: {old_conflicts} -> {new_conflicts} (delta: {new_conflicts - old_conflicts})")

# Find new packages
old_pkgs = {t["package_name"] for t in old_scan["tools"] for d in t["dependencies"]}
new_pkgs = {t["package_name"] for t in new_scan["tools"] for d in t["dependencies"]}

added = new_pkgs - old_pkgs
removed = old_pkgs - new_pkgs

print(f"New packages: {len(added)}")
print(f"Removed packages: {len(removed)}")
```

---

## More Examples in Documentation

For additional examples, see:
- **[INTEGRATION_EXAMPLES.md](INTEGRATION_EXAMPLES.md)** - 10 integration patterns with Team Brain tools
- **[CHEAT_SHEET.txt](CHEAT_SHEET.txt)** - Quick command reference
- **[README.md](README.md)** - Complete usage guide

---

**Built by ATLAS (Team Brain)**  
**For the Maximum Benefit of Life** 🔆⚒️🔗
