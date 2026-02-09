# DependencyScanner - Quick Start Guides

## 📖 ABOUT THESE GUIDES

Each Team Brain agent has a **5-minute quick-start guide** tailored to their role and workflows.

**Choose your guide:**
- [Forge (Orchestrator)](#-forge-quick-start)
- [Atlas (Executor)](#-atlas-quick-start)
- [Clio (Linux Agent)](#-clio-quick-start)
- [Nexus (Multi-Platform)](#-nexus-quick-start)
- [Bolt (Free Executor)](#-bolt-quick-start)

---

## 🔥 FORGE QUICK START

**Role:** Orchestrator / Reviewer  
**Time:** 5 minutes  
**Goal:** Learn to use DependencyScanner for pre-release validation

### Step 1: Installation Check

```bash
# Verify DependencyScanner is available
cd C:\Users\logan\OneDrive\Documents\AutoProjects\DependencyScanner
python dependencyscanner.py --version

# Expected: DependencyScanner 1.0.0
```

### Step 2: First Scan

```bash
# Run your first scan
python dependencyscanner.py scan
```

**What to look for:**
- [X] CRITICAL conflicts - Block release until fixed
- [!] WARNING conflicts - Review and document
- [OK] No conflicts - Green light for release

### Step 3: Pre-Release Workflow

```python
# Add to your pre-release checklist
from dependencyscanner import Scanner, ConflictDetector, ReportGenerator, ScanResult, DependencyAnalyzer
from synapselink import quick_send
from datetime import datetime

# Scan all tools
scanner = Scanner("C:/Users/logan/OneDrive/Documents/AutoProjects")
tools = scanner.discover_tools()
conflicts = ConflictDetector.detect_conflicts(tools)
stats = DependencyAnalyzer.analyze(tools)

# Generate release report
result = ScanResult(
    scan_date=datetime.now().isoformat(),
    tools_scanned=len(tools),
    total_dependencies=stats["total_dependencies"],
    unique_packages=stats["unique_packages"],
    conflicts=conflicts,
    tools=tools,
    statistics=stats
)

md_report = ReportGenerator.generate_markdown_report(result)

# Save to release documentation
with open("RELEASE_DEPENDENCIES.md", "w") as f:
    f.write(md_report)

# Alert if blockers found
critical = [c for c in conflicts if c.severity == "CRITICAL"]
if critical:
    quick_send(
        "LOGAN,ATLAS",
        "Release Blocker: Dependency Conflicts",
        f"Found {len(critical)} critical conflicts. Review RELEASE_DEPENDENCIES.md",
        priority="HIGH"
    )
```

### Step 4: Common Forge Commands

```bash
# Pre-release scan
python dependencyscanner.py scan --format markdown --output PRE_RELEASE_DEPS.md

# Quick conflict check
python dependencyscanner.py scan | grep -E "\[X\]|\[!\]"

# JSON for programmatic review
python dependencyscanner.py scan --format json --output review.json
```

### Next Steps for Forge

1. Add to pre-release checklist in your protocol
2. Run weekly dependency health checks
3. Coordinate conflict resolution with Atlas
4. Track dependency health trends over time

---

## ⚡ ATLAS QUICK START

**Role:** Executor / Builder  
**Time:** 5 minutes  
**Goal:** Verify new tools don't introduce conflicts

### Step 1: Installation

```bash
cd C:\Users\logan\OneDrive\Documents\AutoProjects\DependencyScanner
pip install -e .

# Verify
python -c "from dependencyscanner import Scanner; print('OK')"
```

### Step 2: Post-Build Verification

```python
# Add to your Holy Grail Protocol Phase 8 (Quality Audit)
from dependencyscanner import Scanner, ConflictDetector, Tool, DependencyParser
from pathlib import Path

# After building NewTool, verify no conflicts
new_tool_deps = DependencyParser.parse_requirements_txt(
    Path("NewTool/requirements.txt")
)
new_tool = Tool(name="NewTool", path=Path("NewTool"), dependencies=new_tool_deps)

# Scan existing tools
scanner = Scanner("C:/Users/logan/OneDrive/Documents/AutoProjects")
existing_tools = scanner.discover_tools()

# Check conflicts
all_tools = existing_tools + [new_tool]
conflicts = ConflictDetector.detect_conflicts(all_tools)

# Filter for new tool
new_tool_conflicts = [c for c in conflicts if "NewTool" in c.tools]

if new_tool_conflicts:
    print(f"[X] NewTool introduces {len(new_tool_conflicts)} conflicts!")
    print("Quality Gate FAILED - Fix before deploying")
    for c in new_tool_conflicts:
        print(f"  - {c.package_name}: {c.tools}")
else:
    print("[OK] NewTool passes dependency quality gate")
```

### Step 3: Integration with Holy Grail Protocol

**Add to Phase 8 (Quality Audit):**

```markdown
### Quality Gate: Dependency Conflicts

- [ ] Run DependencyScanner to verify no conflicts introduced
- [ ] If conflicts found, update requirements.txt to align versions
- [ ] Re-scan to confirm resolution
```

### Step 4: Common Atlas Commands

```bash
# Quick check after build
python dependencyscanner.py scan | grep "NewToolName"

# Verify zero-dependency build
python dependencyscanner.py scan --format json | jq '.tools[] | select(.name=="NewToolName") | .dependencies'

# Full validation
python dependencyscanner.py scan --format markdown --output BUILD_DEPS.md
```

### Next Steps for Atlas

1. Add to Holy Grail Protocol Phase 8 checklist
2. Use after every tool build
3. Keep ecosystem dependency-healthy
4. Report systematic conflicts to Forge

---

## 🐧 CLIO QUICK START

**Role:** Linux / Ubuntu Agent  
**Time:** 5 minutes  
**Goal:** Run dependency scans in Linux environment

### Step 1: Linux Installation

```bash
# Clone from GitHub
cd /mnt/d/BEACON_HQ
git clone https://github.com/DonkRonk17/DependencyScanner.git
cd DependencyScanner

# Install (if needed)
pip3 install -e .

# Verify
python3 dependencyscanner.py --version
```

### Step 2: First Scan (Linux)

```bash
# Scan from Linux (accessing Windows drive via WSL)
python3 dependencyscanner.py scan --path /mnt/c/Users/logan/OneDrive/Documents/AutoProjects
```

### Step 3: Platform-Specific Workflow

```bash
# Check for Linux-specific packages
python3 dependencyscanner.py scan --format json --output scan.json
cat scan.json | jq '.tools[].dependencies[] | select(.package_name | contains("linux"))'

# Generate report for Team Brain
python3 dependencyscanner.py scan --format markdown --output ~/LINUX_DEPS.md
```

### Step 4: Common Clio Commands

```bash
# Quick scan
python3 dependencyscanner.py scan

# Export for sharing
python3 dependencyscanner.py scan --format json | jq '.conflicts'

# Pipe to grep
python3 dependencyscanner.py scan | grep CRITICAL
```

### Next Steps for Clio

1. Test on Ubuntu (not just WSL)
2. Report any Linux-specific issues
3. Integrate into Linux-based workflows
4. Share Linux compatibility findings

---

## 🌐 NEXUS QUICK START

**Role:** Multi-Platform Agent  
**Time:** 5 minutes  
**Goal:** Validate dependencies across platforms

### Step 1: Cross-Platform Test

```python
import platform
from dependencyscanner import Scanner
from pathlib import Path

# Report platform
print(f"[i] Platform: {platform.system()}")

# Scan
scanner = Scanner(Path("C:/Users/logan/OneDrive/Documents/AutoProjects"))
tools = scanner.discover_tools()

print(f"[OK] Found {len(tools)} tools on {platform.system()}")
```

### Step 2: Platform-Specific Package Detection

```python
from dependencyscanner import Scanner, DependencyAnalyzer

scanner = Scanner("AutoProjects")
tools = scanner.discover_tools()
stats = DependencyAnalyzer.analyze(tools)

# Find platform-specific packages
platform_keywords = ["win32", "pywin", "linux", "darwin", "osx", "mac"]
platform_deps = []

for tool in tools:
    for dep in tool.dependencies:
        if any(kw in dep.package_name.lower() for kw in platform_keywords):
            platform_deps.append((tool.name, dep.package_name))

print(f"[i] Platform-specific dependencies: {len(platform_deps)}")
for tool, pkg in platform_deps:
    print(f"  - {tool}: {pkg}")
```

### Step 3: Multi-Platform Report

```bash
# Run on each platform, save with platform tag
python dependencyscanner.py scan --format json --output scan_windows.json  # Windows
python dependencyscanner.py scan --format json --output scan_linux.json    # Linux
python dependencyscanner.py scan --format json --output scan_macos.json    # macOS

# Compare results
diff scan_windows.json scan_linux.json
```

### Step 4: Common Nexus Commands

```bash
# Cross-platform scan
python dependencyscanner.py scan --format text

# Compare across platforms
python dependencyscanner.py scan --format json --output scan_$(uname).json
```

### Next Steps for Nexus

1. Run on Windows, Linux, macOS
2. Document platform-specific findings
3. Report cross-platform issues
4. Help maintain platform compatibility

---

## 🆓 BOLT QUICK START

**Role:** Free Executor (Cline + Grok)  
**Time:** 5 minutes  
**Goal:** Run dependency scans without API costs

### Step 1: Verify Zero-Cost Operation

```bash
# No API key required - it's pure Python!
cd AutoProjects/DependencyScanner
python dependencyscanner.py --version

# Expected: DependencyScanner 1.0.0
```

### Step 2: Weekly Automated Scan

```bash
# Schedule weekly (cron or Windows Task Scheduler)
python dependencyscanner.py scan --format markdown --output WEEKLY_DEPS.md

# No API costs, no external dependencies!
```

### Step 3: Batch Processing

```bash
# Scan multiple directories (zero cost!)
for dir in /path/to/projects/*; do
    python dependencyscanner.py scan --path "$dir" --format json --output "${dir}_deps.json"
done
```

### Step 4: Common Bolt Commands

```bash
# Simple scan (free!)
python dependencyscanner.py scan

# Generate report for Logan
python dependencyscanner.py scan --format markdown --output REPORT.md

# Bulk operations (no API calls)
python dependencyscanner.py scan --format json --output scan1.json
python dependencyscanner.py scan --format markdown --output scan1.md
python dependencyscanner.py scan --format text > scan1.txt
```

### Next Steps for Bolt

1. Schedule weekly automated scans
2. Generate reports for human review
3. Use for bulk dependency checks
4. Save API costs (this tool is 100% free!)

---

## 📚 ADDITIONAL RESOURCES

**For All Agents:**
- Full Documentation: [README.md](README.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Integration Plan: [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)
- Integration Examples: [INTEGRATION_EXAMPLES.md](INTEGRATION_EXAMPLES.md)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)

**Support:**
- GitHub Issues: https://github.com/DonkRonk17/DependencyScanner/issues
- Synapse: Post in THE_SYNAPSE/active/
- Direct: Message ATLAS (builder)

---

**Last Updated:** 2026-02-09  
**Maintained By:** ATLAS (Team Brain)  
**Total Length:** 300+ lines ✅
