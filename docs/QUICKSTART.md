# Change Impact Simulator - QUICKSTART

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.11+
- Claude Desktop (for HAWCC integration)

### Installation

```bash
# 1. Clone or download the project
cd change-impact-simulator

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Activate virtual environment
source venv/bin/activate
```

### Run the Test Suite

```bash
# Test all functionality without Claude
python clients/test_change_impact.py
```

Expected output: All 5 tests pass, showing complete workflow.

### Connect to Claude Desktop (HAWCC)

1. **Configure Claude Desktop**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "change-impact-simulator": {
      "command": "python",
      "args": ["/full/path/to/change-impact-simulator/src/change_impact_simulator_server.py"],
      "env": {
        "CONFIG_DIR": "/full/path/to/change-impact-simulator/src/config"
      }
    }
  }
}
```

For Windows: `%APPDATA%\Claude\claude_desktop_config.json`

For Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Restart Claude Desktop**

3. **Verify Connection**

Look for the 🔌 icon in Claude Desktop showing "change-impact-simulator" connected.

### Demo Queries to Try

Once connected to Claude Desktop, try these queries:

#### Query 1: High-Risk Change
```
What happens if I reduce replicas from 3 to 1?
```

**Expected Response:**
- Risk Level: HIGH
- Impacts listed (reduced fault tolerance, SPOF, etc.)
- Safe conditions
- Safeguards
- Manual review recommended

#### Query 2: Low-Risk Change
```
What if I increase replicas from 2 to 5?
```

**Expected Response:**
- Risk Level: LOW
- Positive impacts
- Simple safeguards
- Proceed with standard procedures

#### Query 3: Knowledge Query
```
What are best practices for backup policies?
```

**Expected Response:**
- Knowledge base results
- RPO/RTO information
- Best practices

#### Query 4: List Capabilities
```
What types of changes can you analyze?
```

**Expected Response:**
- List of supported change patterns
- Examples for each

### Verify MCP Tools Are Working

In Claude Desktop, you should see Claude using these tools:
- `search_knowledge` - When you ask about best practices
- `analyze_change` - When you describe a change
- `create_review_task` - For high-risk changes
- `list_supported_changes` - When asking about capabilities

### Troubleshooting

**Server not connecting?**
- Check the path in `claude_desktop_config.json` is absolute
- Ensure `change_impact_simulator_server.py` is executable
- Check Claude Desktop logs: `~/Library/Logs/Claude/` (macOS)

**Config files not loading?**
- Verify CONFIG_DIR path in environment
- Check all YAML files exist in `src/config/`
- Run test suite to verify configs load correctly

**Tools not appearing in Claude?**
- Restart Claude Desktop completely
- Verify MCP server is listed in Settings > Developer
- Check server logs for errors

### Next Steps

1. ✅ Run test suite
2. ✅ Connect to Claude Desktop
3. ✅ Try demo queries
4. 📖 Read [README.md](README.md) for architecture details
5. 🚀 Read [DEPLOYMENT.md](DEPLOYMENT.md) for Docker deployment

---

## Quick Reference

### File Structure
```
change-impact-simulator/
├── src/
│   ├── change_impact_simulator_server.py  # Main MCP server
│   └── config/                             # YAML configs
├── clients/
│   └── test_change_impact.py              # Test suite
├── docker/                                 # Docker files
└── docs/                                   # Documentation
```

### Key Commands

```bash
# Run tests
python clients/test_change_impact.py

# Run server directly (for debugging)
python src/change_impact_simulator_server.py

# Docker deployment
cd docker && docker-compose up --build
```

### Environment Variables

```bash
CONFIG_DIR=/path/to/config    # Config directory
INDUSTRY_MODE=general         # Industry customization
RISK_THRESHOLD=MEDIUM         # Escalation threshold
LOG_LEVEL=INFO               # Logging verbosity
```

---

**Need Help?** Check the full [README.md](README.md) or [DEPLOYMENT.md](DEPLOYMENT.md)