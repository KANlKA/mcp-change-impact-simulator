# Change Impact Simulator MCP Server

> **A read-only, advisory MCP server that helps users understand risk and impact of system changes before execution.**


## 🎯 Overview

The Change Impact Simulator is a **knowledge-powered Q&A and action bot** that:

✅ **Does NOT execute changes**  
✅ **Does NOT automate infrastructure**  
✅ **EXISTS purely to reason + guide**

It provides intelligent, risk-aware analysis of proposed infrastructure changes using:
- Engineering knowledge base (SRE best practices, failure modes)
- Pattern-based change recognition
- Risk assessment framework
- Advisory recommendations

### Key Features

- 🔍 **Knowledge Search** - Query engineering best practices
- 📊 **Change Analysis** - Assess risk and impact of proposed changes
- ⚠️ **Risk Detection** - Identify high-risk changes requiring review
- 📋 **Advisory Tasks** - Recommend manual review when needed
- 🎨 **Config-Driven** - Fully customizable via YAML/JSON configs
- 🐳 **Docker Ready** - Enterprise deployability demonstrated

## 🏗️ Architecture

### MCP Resources (Config-Driven)

All knowledge is loaded from YAML configuration files:

| Resource | Description |
|----------|-------------|
| `/knowledge_base` | Engineering principles, SRE practices, failure modes |
| `/change_patterns` | Known change types with risk hints and impacts |
| `/risk_definitions` | Risk levels (LOW/MEDIUM/HIGH/CRITICAL) |
| `/intents` | Intent taxonomy for query understanding |
| `/actions` | Advisory actions (non-executable) |
| `/persona` | Response style and safety language |

### MCP Tools

Four core tools implement all functionality:

```python
search_knowledge(query)          # Search knowledge base
analyze_change(change_desc)      # Assess risk and impact
create_review_task(analysis)     # Advisory task creation
list_supported_changes()         # List capabilities
```

### Data Flow

```
User Query
    ↓
Claude (via HAWCC) detects intent
    ↓
Queries MCP resources
    ↓
Calls appropriate MCP tools
    ↓
If HIGH risk → create_review_task
    ↓
Structured advisory response
```

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

```bash
# 1. Setup
./setup.sh
source venv/bin/activate

# 2. Test
python clients/test_change_impact.py

# 3. Connect to Claude Desktop
# Edit claude_desktop_config.json with server path

# 4. Try it!
# Ask: "What happens if I reduce replicas from 3 to 1?"
```

## 📁 Project Structure

```
change-impact-simulator/
├── src/
│   ├── change_impact_simulator_server.py    # Main MCP server
│   └── config/
│       ├── knowledge_base.yaml              # Engineering knowledge
│       ├── change_patterns.yaml             # Change type definitions
│       ├── risk_definitions.yaml            # Risk level specs
│       ├── intents.yaml                     # Intent taxonomy
│       ├── actions.yaml                     # Advisory actions
│       └── persona.yaml                     # Response configuration
├── docker/
│   ├── Dockerfile                           # Multi-stage build
│   ├── docker-compose.yml                   # Container orchestration
│   └── .env.template                        # Environment config
├── clients/
│   └── test_change_impact.py               # Test suite
├── docs/
│   ├── README.md                            # This file
│   ├── QUICKSTART.md                        # Quick start guide
│   └── DEPLOYMENT.md                        # Deployment guide
├── requirements.txt                         # Python dependencies
└── setup.sh                                 # Setup script
```

## 🎬 Demo Scenario

### Query
```
What happens if I reduce replicas from 3 to 1?
```

### Claude's Process (via HAWCC)
1. Detects `impact_analysis` intent
2. Calls `search_knowledge("replica")`
3. Calls `analyze_change("reduce replicas from 3 to 1")`
4. Triggers `create_review_task` (HIGH risk detected)

### Response
```
Risk Level: HIGH

Impact:
  - Reduced fault tolerance
  - Single point of failure
  - Potential performance degradation under load

Safe Conditions:
  - Low traffic window (off-peak hours)
  - Non-critical service
  - Adequate monitoring in place

Recommended Safeguards:
  - Execute during off-peak hours
  - Enable enhanced health checks
  - Have rollback plan ready
  - Monitor error rates closely

Advisory Action:
  ⚠️ Manual review recommended

─────────────────────────────────────────────
⚠️ Nothing is executed. This is purely advisory.
─────────────────────────────────────────────
```

## 🔧 Configuration

### Environment Variables

```bash
CONFIG_DIR=/path/to/config    # Configuration directory
INDUSTRY_MODE=general         # Industry: general|fintech|healthcare|saas
RISK_THRESHOLD=MEDIUM         # Escalation threshold
ENABLE_ESCALATION=true        # Auto-escalation for high-risk
LOG_LEVEL=INFO               # Logging: DEBUG|INFO|WARN|ERROR
```

### Industry Customization

Create industry-specific configs by copying and modifying base configs:

```bash
cp src/config/change_patterns.yaml src/config/change_patterns_fintech.yaml
# Edit with fintech-specific patterns
```

Set `INDUSTRY_MODE=fintech` to load industry configs.

## 🐳 Docker Deployment

```bash
# Build and run
cd docker
cp .env.template .env
# Edit .env with your configuration
docker-compose up --build

# Custom configs
mkdir custom-configs
# Copy and edit configs
docker-compose up
```

**Note:** For the hackathon, we demonstrate local execution via HAWCC. Docker deployment shows enterprise scalability and portability.

## 🧪 Testing

### Run Test Suite

```bash
python clients/test_change_impact.py
```

Tests cover:
1. ✅ Knowledge base search
2. ✅ Change analysis (various risk levels)
3. ✅ Review task creation
4. ✅ Supported changes listing
5. ✅ Complete workflow (demo scenario)

### Manual Testing with Claude

After connecting to Claude Desktop:

```
# Test 1: High-risk change
What happens if I reduce replicas from 3 to 1?

# Test 2: Low-risk change
What if I increase replicas from 2 to 5?

# Test 3: Knowledge query
What are best practices for backup policies?

# Test 4: List capabilities
What types of changes can you analyze?
```

## 🎓 How It Works

### 1. Intent Detection
Claude analyzes user queries and matches against intent patterns in `intents.yaml`:
- Impact analysis
- Risk review
- Change validation
- Knowledge queries

### 2. Knowledge Retrieval
Uses `search_knowledge` tool to find relevant engineering principles from `knowledge_base.yaml`.

### 3. Change Analysis
Matches query against patterns in `change_patterns.yaml` using keyword matching:
- Replica changes
- Backup modifications
- Feature flags
- Database configs
- Network rules

### 4. Risk Assessment
Evaluates against `risk_definitions.yaml`:
- **CRITICAL** → Block, executive approval
- **HIGH** → Manual review required
- **MEDIUM** → Caution recommended
- **LOW** → Standard procedures

### 5. Advisory Response
Generates structured response using `persona.yaml` guidelines:
- Clear risk communication
- Actionable safeguards
- Safe execution conditions
- "Advisory only" disclaimers

## 🔐 Safety & Compliance

### Safety Features
- ✅ Read-only operations
- ✅ No execution capability
- ✅ Clear advisory disclaimers
- ✅ Human-in-the-loop for high-risk
- ✅ Audit trail via logging

### Compliance
- Config-driven rules ensure consistency
- All decisions are explainable
- Manual review gates for critical changes
- Stateless design (no sensitive data storage)

## 🎯 Use Cases

### 1. Pre-Change Review
Engineer wants to understand impact before making a change.

### 2. Learning Tool
New team members learn about infrastructure risks.

### 3. Change Documentation
Automatically document risks and safeguards for changes.

### 4. Incident Prevention
Catch high-risk changes before they cause incidents.

## 📊 Metrics & Observability

The server is designed to integrate with monitoring:
- Change analysis requests
- Risk level distribution
- High-risk change frequency
- Tool usage patterns

(Metrics collection can be enabled via `ENABLE_METRICS=true`)

## 🚧 Limitations

**By Design:**
- Does not execute any changes
- Does not integrate with ticketing systems
- Does not require authentication (stateless)
- Pattern matching (not ML-based)

**Current Limitations:**
- English language only
- Text-based analysis (no code parsing)
- No persistent storage
- Single-server deployment

## 🛣️ Roadmap

- [ ] Multi-language support
- [ ] Custom pattern training
- [ ] Integration templates (Jira, ServiceNow)
- [ ] Advanced risk scoring
- [ ] Historical change analysis
- [ ] Team collaboration features

## 📚 Additional Resources

- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [MCP Documentation](https://modelcontextprotocol.io) - Learn about MCP

## 🤝 Contributing

This is a hackathon project. Contributions, suggestions, and feedback are welcome!

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built for the Anthropic MCP Hackathon  
Powered by the Model Context Protocol  
Integrated with Claude via HAWCC

---

**Remember:** This is an advisory system. Nothing is executed. Manual review is required for high-risk changes.
