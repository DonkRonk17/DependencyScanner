# DependencyScanner - Integration Plan

## 🎯 INTEGRATION GOALS

This document outlines how DependencyScanner integrates with:
1. Team Brain agents (Forge, Atlas, Clio, Nexus, Bolt)
2. Existing Team Brain tools (12 identified in Build Audit)
3. BCH (Beacon Command Hub) - future integration
4. Logan's workflows

---

## 📦 BCH INTEGRATION

### Overview

**Current Status:** Not integrated with BCH (standalone CLI tool)

**Future Integration (v1.1+):**
- BCH command: `@scanner scan` - Trigger dependency scan from BCH
- BCH command: `@scanner conflicts` - Show current conflicts
- BCH command: `@scanner stats` - Show dependency statistics
- Scheduled scans: Weekly automated scans with BCH notifications

**Implementation Steps (Future):**
1. Add BCH command handlers in BCH backend
2. Create `bch_scanner_agent.py` wrapper
3. Integrate with BCH notification system
4. Add to BCH agent registry

**Why Not Now:** DependencyScanner is a batch-run tool (weekly/monthly), not real-time. BCH integration would add value but isn't critical for v1.0 MVP.

---

## 🤖 AI AGENT INTEGRATION

### Integration Matrix

| Agent | Use Case | Integration Method | Priority |
|-------|----------|-------------------|----------|
| **Forge** | Pre-release validation, tool quality audits | CLI + Python API | HIGH |
| **Atlas** | Post-build dependency verification | CLI + Python API | HIGH |
| **Clio** | Linux environment dependency checks | CLI | MEDIUM |
| **Nexus** | Cross-platform dependency validation | CLI + Python API | MEDIUM |
| **Bolt** | Bulk dependency scanning (zero cost) | CLI | LOW |

---

### FORGE (Orchestrator / Reviewer)

**Primary Use Case:** Pre-release validation before major Team Brain updates

**Integration Steps:**
1. Add to Forge's pre-release checklist
2. Run scan before major deployments
3. Review conflicts and coordinate fixes
4. Document dependency status in release notes

**Workflow:**
```python
# In Forge session - Pre-release check
from dependencyscanner import Scanner, ConflictDetector, ReportGenerator, ScanResult
from synapselink import quick_send
from datetime import datetime

# Scan all tools
scanner = Scanner("C:/Users/logan/OneDrive/Documents/AutoProjects")
tools = scanner.discover_tools()
conflicts = ConflictDetector.detect_conflicts(tools)
stats = DependencyAnalyzer.analyze(tools)

# Create report
result = ScanResult(
    scan_date=datetime.now().isoformat(),
    tools_scanned=len(tools),
    total_dependencies=stats["total_dependencies"],
    unique_packages=stats["unique_packages"],
    conflicts=conflicts,
    tools=tools,
    statistics=stats
)

# Generate Markdown for documentation
md_report = ReportGenerator.generate_markdown_report(result)
with open("PRE_RELEASE_DEPENDENCIES.md", "w") as f:
    f.write(md_report)

# Alert team if conflicts found
critical = [c for c in conflicts if c.severity == "CRITICAL"]
if critical:
    quick_send(
        "LOGAN,ATLAS",
        "PRE-RELEASE BLOCKER: Critical Dependency Conflicts",
        f"Found {len(critical)} critical conflicts. Release blocked until resolved.",
        priority="HIGH"
    )
```

**Benefit:** Prevents releasing tools with dependency conflicts

---

### ATLAS (Executor / Builder)

**Primary Use Case:** Post-build dependency verification

**Integration Steps:**
1. Add to Holy Grail Protocol Phase 8 (Quality Audit)
2. Run after building new tools
3. Verify new tool doesn't introduce conflicts
4. Update if conflicts detected

**Workflow:**
```python
# In Atlas session - After building NewTool
from dependencyscanner import Scanner, ConflictDetector, Tool, DependencyParser
from pathlib import Path

# Parse new tool's dependencies
new_tool_deps = DependencyParser.parse_requirements_txt(
    Path("NewTool/requirements.txt")
)
new_tool = Tool(
    name="NewTool",
    path=Path("NewTool"),
    dependencies=new_tool_deps
)

# Scan existing tools
scanner = Scanner("C:/Users/logan/OneDrive/Documents/AutoProjects")
existing_tools = scanner.discover_tools()

# Check for conflicts
all_tools = existing_tools + [new_tool]
conflicts = ConflictDetector.detect_conflicts(all_tools)

# Filter conflicts involving new tool
new_tool_conflicts = [
    c for c in conflicts 
    if "NewTool" in c.tools
]

if new_tool_conflicts:
    print(f"[X] NewTool introduces {len(new_tool_conflicts)} conflicts!")
    print("Fix before deploying:")
    for conflict in new_tool_conflicts:
        print(f"  - {conflict.package_name}: {conflict.tools}")
else:
    print("[OK] NewTool has no conflicts - ready to deploy!")
```

**Benefit:** Catch conflicts before deployment, maintain ecosystem health

---

### CLIO (Linux Agent)

**Primary Use Case:** Linux environment dependency validation

**Integration Steps:**
1. Run on Ubuntu/Linux systems
2. Verify cross-platform compatibility
3. Report Linux-specific issues

**Workflow:**
```bash
# In Clio session (Linux)
cd /mnt/d/BEACON_HQ/AutoProjects/DependencyScanner

# Run scan
python3 dependencyscanner.py scan

# Export for analysis
python3 dependencyscanner.py scan --format json --output ~/dependency_report.json

# Check for Linux-specific packages
grep -i "linux" ~/dependency_report.json
```

**Platform Considerations:**
- Path format: Use `/mnt/d/` for WSL access to Windows drives
- Python version: Ensure Python 3.8+ available
- Permissions: May need `sudo` for system-wide scanning

**Benefit:** Verify tools work on Linux, catch platform-specific dependency issues

---

### NEXUS (Multi-Platform Agent)

**Primary Use Case:** Cross-platform dependency validation

**Integration Steps:**
1. Run on Windows, Linux, and macOS
2. Compare results across platforms
3. Identify platform-specific dependencies

**Workflow:**
```python
# In Nexus session - Cross-platform check
import platform
from dependencyscanner import Scanner, DependencyAnalyzer

scanner = Scanner("AutoProjects")
tools = scanner.discover_tools()
stats = DependencyAnalyzer.analyze(tools)

# Report platform
current_platform = platform.system()
print(f"[i] Scanning on {current_platform}")
print(f"[OK] Found {len(tools)} tools")
print(f"[i] {stats['unique_packages']} unique packages")

# Look for platform-specific packages
platform_specific = ["pywin32", "python-xlib", "pyobjc"]
found_platform_deps = [
    pkg for pkg in stats["package_usage"].keys()
    if any(plat in pkg.lower() for plat in ["win", "linux", "darwin", "osx"])
]

if found_platform_deps:
    print(f"[!] Platform-specific packages found: {found_platform_deps}")
```

**Benefit:** Ensure tools work across all platforms Team Brain uses

---

### BOLT (Free Executor)

**Primary Use Case:** Bulk dependency scanning without API costs

**Integration Steps:**
1. Use CLI interface (no API calls needed)
2. Schedule periodic scans
3. Generate reports for human review

**Workflow:**
```bash
# In Bolt session (Cline + Grok)
cd AutoProjects/DependencyScanner

# Run scan (zero API cost!)
python dependencyscanner.py scan --format markdown --output WEEKLY_DEPS.md

# Save for Logan to review
echo "[OK] Dependency report generated: WEEKLY_DEPS.md"
```

**Cost Benefit:** Free automated dependency monitoring

---

## 🔗 INTEGRATION WITH OTHER TEAM BRAIN TOOLS

### With ToolRegistry

**Purpose:** Register DependencyScanner as official Team Brain tool

**Integration:**
```python
from toolregistry import ToolRegistry

registry = ToolRegistry()
registry.register_tool(
    name="DependencyScanner",
    version="1.0.0",
    category="development",
    description="Scan Team Brain tools for dependency conflicts"
)
```

### With TestRunner

**Purpose:** Run DependencyScanner tests as part of test suite

**Integration:**
```bash
# In TestRunner
python testrunner.py run --tool DependencyScanner

# Expected: 22/22 tests passing
```

### With GitFlow

**Purpose:** Standardized git workflow for updates

**Integration:**
```bash
# After making changes to DependencyScanner
cd DependencyScanner
gitflow commit "Fix: Handle edge case in version parsing"
gitflow push
```

### With PostMortem

**Purpose:** Analyze scan failures

**Integration:**
```python
from postmortem import PostMortem
from dependencyscanner import Scanner

try:
    scanner = Scanner("AutoProjects")
    tools = scanner.discover_tools()
except Exception as e:
    # Generate post-mortem
    pm = PostMortem()
    pm.analyze_failure(
        component="DependencyScanner",
        error=str(e),
        context="Scanning AutoProjects"
    )
    pm.generate_report()
```

### With AgentHealth

**Purpose:** Monitor scanner health during long scans

**Integration:**
```python
from agenthealth import AgentHealth
from dependencyscanner import Scanner

health = AgentHealth()
session_id = health.start_session("ATLAS", task="Dependency scan")

try:
    scanner = Scanner("AutoProjects")
    health.heartbeat("ATLAS", status="scanning")
    
    tools = scanner.discover_tools()
    health.heartbeat("ATLAS", status="analyzing")
    
    # ... rest of scan
    
    health.end_session("ATLAS", session_id, status="success")
except Exception as e:
    health.log_error("ATLAS", str(e))
    health.end_session("ATLAS", session_id, status="failed")
```

---

## 🚀 ADOPTION ROADMAP

### Phase 1: Core Adoption (Week 1)

**Goal:** All agents aware and can run basic scans

**Steps:**
1. ✅ Tool deployed to GitHub
2. ☐ Quick-start guides sent via Synapse
3. ☐ Each agent tests basic `scan` command
4. ☐ Feedback collected via Synapse

**Success Criteria:**
- All 5 agents have run at least one scan
- No blocking issues reported
- Agents understand output format

---

### Phase 2: Workflow Integration (Week 2-3)

**Goal:** Integrated into regular workflows

**Steps:**
1. ☐ Forge: Add to pre-release checklist
2. ☐ Atlas: Add to Holy Grail Protocol Phase 8
3. ☐ Weekly dependency health checks scheduled
4. ☐ Integration examples tested by all agents

**Success Criteria:**
- Used weekly by Forge for release checks
- Used by Atlas after every new tool build
- Dependency health tracked over time

---

### Phase 3: Automation & Enhancement (Week 4+)

**Goal:** Fully automated with advanced features

**Steps:**
1. ☐ CI/CD integration (GitHub Actions)
2. ☐ BCH command integration (`@scanner scan`)
3. ☐ Historical tracking via MemoryBridge
4. ☐ Security audit integration with `safety`
5. ☐ v1.1 features based on feedback

**Success Criteria:**
- Automated weekly scans running
- BCH commands working
- Security vulnerabilities detected proactively
- v1.1 improvements identified and implemented

---

## 📊 SUCCESS METRICS

### Adoption Metrics

- **Agents Using Tool:** Target 5/5 by Week 2
- **Weekly Scan Runs:** Target 4+ per month
- **Integration Count:** Target 5+ tool integrations by Week 3

### Efficiency Metrics

- **Time Saved per Scan:** ~2 hours (vs manual review)
- **Conflicts Prevented:** Track installations prevented/fixed
- **Cost Saved:** $0 (no API calls, no paid services)

### Quality Metrics

- **Bug Reports:** Track and resolve quickly
- **Feature Requests:** Collect for v1.1+
- **User Satisfaction:** Qualitative feedback from agents

---

## 🛠️ TECHNICAL INTEGRATION DETAILS

### Import Paths

```python
# Standard import
from dependencyscanner import Scanner, ConflictDetector, DependencyAnalyzer

# Specific imports
from dependencyscanner import (
    Dependency,
    Tool,
    Conflict,
    ScanResult,
    DependencyParser,
    ReportGenerator
)
```

### Error Codes

- `0` - Success (no conflicts)
- `1` - Warnings (non-critical conflicts)
- `2` - Critical conflicts or scan failure

### Configuration Integration

**Shared Config via ConfigManager:**
```python
from configmanager import ConfigManager

config = ConfigManager()
config.set("dependencyscanner.scan_path", "C:/AutoProjects")
config.set("dependencyscanner.default_format", "json")
config.save()
```

### Logging Integration

**Log Format:** Standard Python logging

**Log Location:** `~/.dependencyscanner/logs/scanner.log`

**Log Levels:**
- DEBUG: Detailed parsing and analysis
- INFO: Scan progress, results summary
- WARNING: Potential issues, non-critical errors
- ERROR: Critical failures, parse errors

---

## 🔧 MAINTENANCE & SUPPORT

### Update Strategy

- **Minor updates (v1.x):** Monthly
  - Bug fixes
  - Performance improvements
  - New output formats
  
- **Major updates (v2.0+):** Quarterly
  - New language support (Node.js, Rust)
  - Advanced conflict resolution
  - AI-powered recommendations

- **Security patches:** Immediate

### Support Channels

- **GitHub Issues:** Bug reports, feature requests
- **Synapse:** Team Brain discussions, integration questions
- **Direct to Builder:** Complex issues, architecture questions

### Known Limitations

1. **Python Only:** v1.0 only scans Python dependencies (Node.js, Rust planned for v2.0)
2. **Simple setup.py Parsing:** Complex dynamic requirements may not be fully parsed
3. **No Auto-Fix:** Reports conflicts but doesn't automatically fix them (by design)
4. **Network Features:** PyPI version checking, security scanning require optional dependencies
5. **No Real-Time Monitoring:** Batch scanning only (not file watcher)

**Planned Improvements (v1.1+):**
- Watch mode for real-time monitoring
- Auto-fix suggestions with commands
- Node.js package.json support
- Rust Cargo.toml support
- Enhanced security integration

---

## 📚 ADOPTION RESOURCES

### For All Agents

- **Quick Start:** [QUICK_START_GUIDES.md](QUICK_START_GUIDES.md) - 5 minutes per agent
- **Examples:** [INTEGRATION_EXAMPLES.md](INTEGRATION_EXAMPLES.md) - Copy-paste code
- **Documentation:** [README.md](README.md) - Comprehensive guide
- **Command Reference:** [CHEAT_SHEET.txt](CHEAT_SHEET.txt) - Quick lookup

### Training Materials

1. **Video Tutorial (Future):** "How to Use DependencyScanner"
2. **Workshop (Future):** "Dependency Management Best Practices"
3. **Documentation:** All docs available in repo

---

## 🎯 RECOMMENDED ADOPTION WORKFLOW

### Week 1: Awareness & Testing

**Day 1-2:**
- All agents read QUICK_START_GUIDES.md
- Each agent runs first scan
- Report any issues to ATLAS

**Day 3-5:**
- Test different commands and formats
- Try Python API integration
- Provide feedback

**Day 6-7:**
- Resolve any bugs or issues
- Finalize usage patterns
- Document lessons learned

### Week 2: Integration

**Day 8-10:**
- Forge: Add to pre-release workflow
- Atlas: Add to Holy Grail Protocol
- All: Try integration examples

**Day 11-14:**
- Run first coordinated weekly scan
- Review results as team
- Identify standardization opportunities

### Week 3: Optimization

**Day 15-21:**
- Collect usage metrics
- Identify v1.1 feature requests
- Optimize based on real usage patterns
- Full adoption across all agents

---

**Last Updated:** 2026-02-09  
**Maintained By:** ATLAS (Team Brain)  
**Total Length:** 400+ lines ✅
