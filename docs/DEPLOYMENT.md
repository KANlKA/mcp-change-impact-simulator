# Change Impact Simulator - Deployment Guide

## 🎯 Deployment Overview

This guide covers three deployment scenarios:

1. **Local Development** (HAWCC + Claude Desktop)
2. **Docker Containerized** (Portability demonstration)
3. **Production Considerations** (Future scalability)

## 1️⃣ Local Development Deployment

### Prerequisites
- Python 3.11+
- Claude Desktop application
- Git

### Step-by-Step Setup

#### A. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd change-impact-simulator

# Run setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate   # Windows
```

#### B. Verify Installation

```bash
# Run test suite
python clients/test_change_impact.py

# Expected: All 5 tests pass
```

#### C. Configure Claude Desktop

**macOS:**
```bash
# Edit config file
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```cmd
# Edit config file
notepad %APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
# Edit config file
nano ~/.config/Claude/claude_desktop_config.json
```

**Configuration:**
```json
{
  "mcpServers": {
    "change-impact-simulator": {
      "command": "python",
      "args": [
        "/absolute/path/to/change-impact-simulator/src/change_impact_simulator_server.py"
      ],
      "env": {
        "CONFIG_DIR": "/absolute/path/to/change-impact-simulator/src/config"
      }
    }
  }
}
```

**Important:** Use absolute paths!

#### D. Start and Verify

```bash
# 1. Restart Claude Desktop completely
# 2. Open Claude Desktop
# 3. Look for 🔌 icon showing "change-impact-simulator" connected
# 4. Try a test query: "What happens if I reduce replicas from 3 to 1?"
```

### Troubleshooting Local Deployment

**Server not appearing in Claude Desktop:**
```bash
# Check logs (macOS)
tail -f ~/Library/Logs/Claude/mcp*.log

# Verify paths are absolute
python -c "import os; print(os.path.abspath('src/change_impact_simulator_server.py'))"

# Test server manually
python src/change_impact_simulator_server.py
# Should start without errors
```

**Config files not loading:**
```bash
# Verify config directory
ls -la src/config/

# Should show:
# - knowledge_base.yaml
# - change_patterns.yaml
# - risk_definitions.yaml
# - intents.yaml
# - actions.yaml
# - persona.yaml
```

## 2️⃣ Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Quick Start

```bash
# Navigate to docker directory
cd docker

# Copy environment template
cp .env.template .env

# Edit configuration
nano .env

# Build and run
docker-compose up --build
```

### Configuration Options

Edit `docker/.env`:

```bash
# Basic Configuration
CONFIG_DIR=/configs
INDUSTRY_MODE=general           # general|fintech|healthcare|saas
RISK_THRESHOLD=MEDIUM          # LOW|MEDIUM|HIGH|CRITICAL
LOG_LEVEL=INFO                 # DEBUG|INFO|WARN|ERROR

# Advanced Configuration
ENABLE_ESCALATION=true         # Auto-escalate high-risk changes
ENABLE_METRICS=false           # Enable metrics collection
ENABLE_AUDIT_LOG=true          # Enable audit logging
```

### Custom Configurations

```bash
# Create custom config directory
mkdir -p docker/custom-configs

# Copy and customize configs
cp src/config/*.yaml docker/custom-configs/

# Edit configs as needed
nano docker/custom-configs/change_patterns.yaml

# Update docker-compose.yml to mount custom configs
# Already configured in docker-compose.yml
```

### Docker Commands

```bash
# Build image
docker-compose build

# Run in foreground
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

### Docker Architecture

```
┌─────────────────────────────────────────┐
│  Docker Container                       │
│  ┌───────────────────────────────────┐ │
│  │  MCP Server Process               │ │
│  │  - Python runtime                 │ │
│  │  - YAML config loading            │ │
│  │  - MCP protocol handling          │ │
│  └───────────────────────────────────┘ │
│                                         │
│  Volume Mounts:                         │
│  /configs ← custom-configs/             │
│  /app/logs ← ./logs/                   │
└─────────────────────────────────────────┘
```

### Health Checks

```bash
# Check container health
docker-compose ps

# Should show:
# change-impact-simulator-mcp   healthy

# Manual health check
docker exec change-impact-simulator-mcp python -c "import sys; sys.exit(0)"
```

### Resource Limits

Configured in `docker-compose.yml`:

```yaml
resources:
  limits:
    cpus: '0.5'      # Max 0.5 CPU cores
    memory: 512M     # Max 512MB RAM
  reservations:
    cpus: '0.25'     # Min 0.25 CPU cores
    memory: 256M     # Min 256MB RAM
```

## 3️⃣ Production Considerations

### Architecture for Scale

**Note:** For the hackathon, we demonstrate local execution via HAWCC. The following represents production-ready patterns.

#### Multi-Instance Deployment

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  change-impact-simulator:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

#### Load Balancing

```yaml
# nginx.conf snippet
upstream mcp_servers {
    least_conn;
    server simulator1:3000;
    server simulator2:3000;
    server simulator3:3000;
}
```

#### Monitoring Integration

```python
# Add to change_impact_simulator_server.py
from prometheus_client import Counter, Histogram

CHANGE_ANALYSIS_COUNTER = Counter(
    'change_analysis_total',
    'Total change analyses',
    ['risk_level']
)

ANALYSIS_DURATION = Histogram(
    'change_analysis_duration_seconds',
    'Change analysis duration'
)
```

### Security Hardening

#### 1. Container Security

```dockerfile
# Use non-root user
RUN useradd -m -u 1000 mcpuser
USER mcpuser

# Read-only root filesystem
docker run --read-only \
  --tmpfs /tmp \
  change-impact-simulator
```

#### 2. Config Validation

```python
# Add schema validation
import jsonschema

def validate_config(config_data, schema):
    jsonschema.validate(instance=config_data, schema=schema)
```

#### 3. Rate Limiting

```python
# Add rate limiting per client
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=100, period=60)
def analyze_change(change_description):
    # Implementation
```

### High Availability

#### 1. Health Checks

```python
# Enhanced health check endpoint
@server.health()
async def health_check():
    return {
        "status": "healthy",
        "configs_loaded": all([
            simulator.knowledge_base,
            simulator.change_patterns,
            simulator.risk_definitions
        ]),
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### 2. Graceful Shutdown

```python
import signal

def graceful_shutdown(signum, frame):
    logger.info("Received shutdown signal, cleaning up...")
    # Cleanup logic
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)
```

### Logging & Observability

#### Structured Logging

```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
```

#### Log Aggregation

```yaml
# docker-compose with log driver
services:
  change-impact-simulator:
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: mcp.change-impact
```

### Backup & Disaster Recovery

```bash
# Backup configurations
tar -czf configs-backup-$(date +%Y%m%d).tar.gz src/config/

# Upload to S3
aws s3 cp configs-backup-*.tar.gz s3://backup-bucket/configs/
```

### Deployment Checklist

#### Pre-Deployment
- [ ] All configs validated
- [ ] Tests passing (100%)
- [ ] Security scan completed
- [ ] Resource limits set
- [ ] Monitoring configured
- [ ] Backup procedures tested

#### Deployment
- [ ] Blue-green deployment strategy
- [ ] Health checks passing
- [ ] Logs accessible
- [ ] Rollback plan ready

#### Post-Deployment
- [ ] Verify MCP connection
- [ ] Run smoke tests
- [ ] Monitor error rates
- [ ] Check resource usage
- [ ] Document any issues

## 4️⃣ Environment-Specific Configurations

### Development
```bash
LOG_LEVEL=DEBUG
ENABLE_METRICS=false
RISK_THRESHOLD=LOW
```

### Staging
```bash
LOG_LEVEL=INFO
ENABLE_METRICS=true
RISK_THRESHOLD=MEDIUM
INDUSTRY_MODE=general
```

### Production
```bash
LOG_LEVEL=WARN
ENABLE_METRICS=true
ENABLE_AUDIT_LOG=true
RISK_THRESHOLD=HIGH
INDUSTRY_MODE=fintech  # or specific industry
```

## 5️⃣ Troubleshooting

### Common Issues

**Issue: Container fails to start**
```bash
# Check logs
docker-compose logs

# Common causes:
# - Missing config files
# - Invalid YAML syntax
# - Port conflicts
```

**Issue: Config files not loading**
```bash
# Verify mount
docker exec change-impact-simulator-mcp ls -la /configs

# Should show all YAML files
```

**Issue: High memory usage**
```bash
# Monitor resources
docker stats change-impact-simulator-mcp

# Adjust limits in docker-compose.yml if needed
```

## 6️⃣ Upgrade Procedures

```bash
# 1. Backup current configs
tar -czf configs-backup.tar.gz src/config/

# 2. Pull latest code
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt

# 4. Run tests
python clients/test_change_impact.py

# 5. Rebuild Docker image
docker-compose build

# 6. Deploy with zero downtime
docker-compose up -d --no-deps --build change-impact-simulator
```

---

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Run diagnostics: `python clients/test_change_impact.py`
3. Review [QUICKSTART.md](QUICKSTART.md) and [README.md](README.md)

---

**Remember:** For the hackathon, local deployment via HAWCC is recommended. Docker deployment demonstrates enterprise scalability and portability.