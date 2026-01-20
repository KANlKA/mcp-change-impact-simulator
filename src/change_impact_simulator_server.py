#!/usr/bin/env python3
"""
Change Impact Simulator MCP Server - Enhanced Version
A read-only, advisory MCP server for analyzing infrastructure change risks

NEW FEATURES:
- CI/CD Pipeline Integration
- Policy-Based Approval Workflows
- Metrics Collection
- Extended Change Patterns
- Industry-Specific Patterns
"""

import asyncio
import json
import yaml
import os
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, UTC
from collections import defaultdict

from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
import mcp.server.stdio


class MetricsCollector:
    """Collects and provides analytics on change analyses"""
    
    def __init__(self):
        self.analyses = []
        self.risk_distribution = defaultdict(int)
        self.pattern_usage = defaultdict(int)
        self.start_time = datetime.now(UTC)
    
    def record_analysis(self, analysis: Dict[str, Any]):
        """Record a change analysis"""
        self.analyses.append({
            "timestamp": analysis.get("timestamp"),
            "risk_level": analysis.get("risk_level"),
            "pattern": analysis.get("matched_pattern"),
            "requires_review": analysis.get("requires_manual_review")
        })
        
        risk = analysis.get("risk_level", "UNKNOWN")
        self.risk_distribution[risk] += 1
        
        pattern = analysis.get("matched_pattern")
        if pattern:
            self.pattern_usage[pattern] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        total = len(self.analyses)
        high_risk_count = self.risk_distribution["HIGH"] + self.risk_distribution["CRITICAL"]
        
        return {
            "summary": {
                "total_analyses": total,
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "high_risk_percentage": round(high_risk_count / max(total, 1) * 100, 2)
            },
            "risk_distribution": dict(self.risk_distribution),
            "top_patterns": sorted(
                self.pattern_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "recent_analyses": self.analyses[-10:]  # Last 10
        }


class ApprovalWorkflowEngine:
    """Manages policy-based approval workflows"""
    
    def __init__(self, workflow_config: Dict[str, Any]):
        self.workflows = workflow_config
    
    def get_required_approvals(self, risk_level: str) -> List[Dict[str, Any]]:
        """Determine required approvals based on risk level"""
        workflow = self.workflows.get("approval_workflow", {})
        stages = workflow.get("stages", [])
        
        required = []
        for stage in stages:
            required_for = stage.get("required_for", [])
            if risk_level in required_for:
                required.append({
                    "stage": stage.get("name"),
                    "description": stage.get("description", ""),
                    "auto_approve": stage.get("auto_approve", False),
                    "approvers": stage.get("approvers", [])
                })
        
        return required
    
    def create_approval_chain(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create approval workflow for a change"""
        risk_level = analysis.get("risk_level", "UNKNOWN")
        required_approvals = self.get_required_approvals(risk_level)
        
        if not required_approvals:
            return {
                "requires_approval": False,
                "reason": "Risk level does not require approval workflow"
            }
        
        return {
            "requires_approval": True,
            "risk_level": risk_level,
            "change_description": analysis.get("change_description"),
            "approval_stages": required_approvals,
            "estimated_approval_time": self._estimate_approval_time(required_approvals),
            "workflow_id": f"WF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "status": "PENDING_APPROVAL",
            "note": "This is an advisory workflow. No automatic execution will occur."
        }
    
    def _estimate_approval_time(self, stages: List[Dict]) -> str:
        """Estimate time to complete approvals"""
        hours = len(stages) * 2  # Assume 2 hours per stage
        if hours <= 4:
            return "Same day"
        elif hours <= 24:
            return "Within 24 hours"
        else:
            return f"{hours // 24} business days"


class CICDValidator:
    """Validates deployment configurations for CI/CD pipelines"""
    
    def __init__(self, change_patterns: Dict[str, Any]):
        self.change_patterns = change_patterns
    
    def validate_deployment_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a deployment configuration"""
        issues = []
        warnings = []
        
        # Check replica count
        replicas = config.get("replicas", 0)
        if replicas < 2:
            issues.append({
                "severity": "HIGH",
                "field": "replicas",
                "message": f"Replica count ({replicas}) is below recommended minimum of 2",
                "recommendation": "Increase replicas to at least 2 for high availability"
            })
        elif replicas < 3:
            warnings.append({
                "severity": "MEDIUM",
                "field": "replicas",
                "message": f"Replica count ({replicas}) is below optimal count of 3",
                "recommendation": "Consider increasing to 3 replicas for better fault tolerance"
            })
        
        # Check resource limits
        resources = config.get("resources", {})
        limits = resources.get("limits", {})
        
        if not limits:
            warnings.append({
                "severity": "MEDIUM",
                "field": "resources.limits",
                "message": "No resource limits defined",
                "recommendation": "Define CPU and memory limits to prevent resource exhaustion"
            })
        
        # Check health checks
        health_check = config.get("healthCheck", {})
        if not health_check:
            issues.append({
                "severity": "MEDIUM",
                "field": "healthCheck",
                "message": "No health check configured",
                "recommendation": "Add liveness and readiness probes"
            })
        
        # Check environment
        environment = config.get("environment", "unknown")
        if environment == "production" and len(issues) > 0:
            issues.append({
                "severity": "CRITICAL",
                "field": "environment",
                "message": "Production deployment has blocking issues",
                "recommendation": "Resolve all HIGH severity issues before production deployment"
            })
        
        return {
            "valid": len(issues) == 0,
            "environment": environment,
            "issues": issues,
            "warnings": warnings,
            "summary": {
                "total_issues": len(issues),
                "total_warnings": len(warnings),
                "blocking_issues": len([i for i in issues if i["severity"] in ["HIGH", "CRITICAL"]])
            },
            "recommendation": "BLOCK DEPLOYMENT" if len(issues) > 0 else "PROCEED WITH CAUTION" if len(warnings) > 0 else "APPROVED"
        }
    
    def validate_pipeline_stage(self, stage: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration for a specific pipeline stage"""
        stage_configs = {
            "dev": {"min_replicas": 1, "require_health_check": False},
            "staging": {"min_replicas": 2, "require_health_check": True},
            "production": {"min_replicas": 3, "require_health_check": True}
        }
        
        stage_requirements = stage_configs.get(stage.lower(), stage_configs["production"])
        issues = []
        
        replicas = config.get("replicas", 0)
        if replicas < stage_requirements["min_replicas"]:
            issues.append({
                "severity": "HIGH",
                "message": f"{stage} requires at least {stage_requirements['min_replicas']} replicas"
            })
        
        if stage_requirements["require_health_check"] and not config.get("healthCheck"):
            issues.append({
                "severity": "HIGH",
                "message": f"{stage} requires health check configuration"
            })
        
        return {
            "stage": stage,
            "valid": len(issues) == 0,
            "issues": issues
        }


class ChangeImpactSimulatorServer:
    """MCP Server for analyzing change impacts and risks - Enhanced Version"""

    def __init__(self):
        # Load industry mode from environment
        self.industry_mode = os.getenv("INDUSTRY_MODE", "general")
        
        # Config directory handling
        config_dir = os.getenv("CONFIG_DIR", "src/config")
        self.config_dir = Path(config_dir)

        self.knowledge_base = {}
        self.change_patterns = {}
        self.risk_definitions = {}
        self.intents = {}
        self.actions = {}
        self.persona = {}
        self.workflows = {}

        self.load_all_configs()
        
        # Initialize new components
        self.metrics = MetricsCollector()
        self.workflow_engine = ApprovalWorkflowEngine(self.workflows)
        self.cicd_validator = CICDValidator(self.change_patterns)

    def load_all_configs(self):
        """Load all configuration files, including industry-specific ones"""
        
        base_configs = {
            "knowledge_base": "knowledge_base.yaml",
            "change_patterns": "change_patterns.yaml",
            "risk_definitions": "risk_definitions.yaml",
            "intents": "intents.yaml",
            "actions": "actions.yaml",
            "persona": "persona.yaml",
            "workflows": "workflows.yaml",
        }
        
        for attr, filename in base_configs.items():
            # Try industry-specific config first
            industry_file = filename.replace(".yaml", f"_{self.industry_mode}.yaml")
            industry_path = self.config_dir / industry_file
            
            if industry_path.exists():
                print(f"Loading industry-specific config: {industry_file}")
                with open(industry_path, "r") as f:
                    setattr(self, attr, yaml.safe_load(f))
            else:
                # Fall back to base config
                base_path = self.config_dir / filename
                if base_path.exists():
                    with open(base_path, "r") as f:
                        setattr(self, attr, yaml.safe_load(f))
                else:
                    print(f"Warning: {filename} not found")

    # -----------------------------
    # Core Logic (Original)
    # -----------------------------

    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        query = query.lower()
        results = []

        for category, items in self.knowledge_base.items():
            for item in items:
                title = item.get("title", "").lower()
                content = item.get("content", "").lower()

                if query in title or query in content:
                    results.append({
                        "category": category,
                        "title": item.get("title"),
                        "content": item.get("content"),
                    })

        return results

    def analyze_change(self, change_description: str) -> Dict[str, Any]:
        text = change_description.lower()
        matched_pattern = None

        for name, pattern in self.change_patterns.items():
            keywords = pattern.get("keywords", [])
            if any(k.lower() in text for k in keywords):
                matched_pattern = pattern.copy()
                matched_pattern["name"] = name
                break

        if not matched_pattern:
            return {
                "risk_level": "UNKNOWN",
                "message": "Unrecognized change pattern",
                "recommendation": "Manual review required",
            }

        risk_level = matched_pattern.get("risk_level", "MEDIUM")
        risk_def = self.risk_definitions.get(risk_level, {})

        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "change_description": change_description,
            "matched_pattern": matched_pattern["name"],
            "risk_level": risk_level,
            "impact": matched_pattern.get("impacts", []),
            "safe_conditions": matched_pattern.get("safe_conditions", []),
            "safeguards": matched_pattern.get("safeguards", []),
            "risk_definition": risk_def,
            "requires_manual_review": risk_level in ["HIGH", "CRITICAL"],
        }
        
        # Record metrics
        self.metrics.record_analysis(analysis)
        
        return analysis

    def create_review_task(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        risk = analysis.get("risk_level", "UNKNOWN")

        if risk not in ["HIGH", "CRITICAL"]:
            return {
                "task_created": False,
                "reason": "Risk level does not require manual review",
            }

        return {
            "task_created": True,
            "task_type": "MANUAL_REVIEW_REQUIRED",
            "priority": "HIGH" if risk == "CRITICAL" else "MEDIUM",
            "timestamp": datetime.utcnow().isoformat(),
            "change_description": analysis.get("change_description"),
            "risk_level": risk,
            "note": "Advisory only — no execution, no automation",
        }

    def list_supported_changes(self) -> List[Dict[str, str]]:
        return [
            {
                "name": name,
                "description": p.get("description", ""),
                "risk_level": p.get("risk_level", "MEDIUM"),
                "example": p.get("example", ""),
            }
            for name, p in self.change_patterns.items()
        ]


# -----------------------------
# MCP Server Wiring - Enhanced
# -----------------------------

async def main():
    simulator = ChangeImpactSimulatorServer()
    server = Server("change-impact-simulator")

    # -------- Resources --------

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        return [
            Resource("config://knowledge_base", "Knowledge Base", "application/json"),
            Resource("config://change_patterns", "Change Patterns", "application/json"),
            Resource("config://risk_definitions", "Risk Definitions", "application/json"),
            Resource("config://intents", "Intents", "application/json"),
            Resource("config://actions", "Actions", "application/json"),
            Resource("config://persona", "Persona", "application/json"),
            Resource("config://workflows", "Approval Workflows", "application/json"),
            Resource("metrics://statistics", "Analysis Statistics", "application/json"),
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        mapping = {
            "config://knowledge_base": simulator.knowledge_base,
            "config://change_patterns": simulator.change_patterns,
            "config://risk_definitions": simulator.risk_definitions,
            "config://intents": simulator.intents,
            "config://actions": simulator.actions,
            "config://persona": simulator.persona,
            "config://workflows": simulator.workflows,
            "metrics://statistics": simulator.metrics.get_statistics(),
        }
        return json.dumps(mapping.get(uri, {}), indent=2)

    # -------- Tools --------

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            # Original tools
            Tool(
                name="search_knowledge",
                description="Search engineering knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            ),
            Tool(
                name="analyze_change",
                description="Analyze a proposed change and assess risk",
                inputSchema={
                    "type": "object",
                    "properties": {"change_description": {"type": "string"}},
                    "required": ["change_description"],
                },
            ),
            Tool(
                name="create_review_task",
                description="Create advisory review task for high-risk changes",
                inputSchema={
                    "type": "object",
                    "properties": {"analysis": {"type": "object"}},
                    "required": ["analysis"],
                },
            ),
            Tool(
                name="list_supported_changes",
                description="List all supported change patterns",
                inputSchema={"type": "object", "properties": {}},
            ),
            
            # NEW: Metrics tool
            Tool(
                name="get_analysis_statistics",
                description="Get statistics about change analyses (total, risk distribution, trends)",
                inputSchema={"type": "object", "properties": {}},
            ),
            
            # NEW: Approval workflow tool
            Tool(
                name="create_approval_workflow",
                description="Create policy-based approval workflow for a change",
                inputSchema={
                    "type": "object",
                    "properties": {"analysis": {"type": "object"}},
                    "required": ["analysis"],
                },
            ),
            
            # NEW: CI/CD validation tools
            Tool(
                name="validate_deployment_config",
                description="Validate a deployment configuration for CI/CD pipeline",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "config": {
                            "type": "object",
                            "description": "Deployment configuration (replicas, resources, healthCheck, etc.)"
                        }
                    },
                    "required": ["config"],
                },
            ),
            Tool(
                name="validate_pipeline_stage",
                description="Validate configuration for a specific pipeline stage (dev/staging/production)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "stage": {"type": "string", "description": "Pipeline stage (dev, staging, production)"},
                        "config": {"type": "object", "description": "Stage configuration"}
                    },
                    "required": ["stage", "config"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        # Original tools
        if name == "search_knowledge":
            return [TextContent(type="text", text=json.dumps(
                simulator.search_knowledge(arguments["query"]), indent=2
            ))]

        if name == "analyze_change":
            return [TextContent(type="text", text=json.dumps(
                simulator.analyze_change(arguments["change_description"]), indent=2
            ))]

        if name == "create_review_task":
            return [TextContent(type="text", text=json.dumps(
                simulator.create_review_task(arguments["analysis"]), indent=2
            ))]

        if name == "list_supported_changes":
            return [TextContent(type="text", text=json.dumps(
                simulator.list_supported_changes(), indent=2
            ))]
        
        # NEW: Metrics
        if name == "get_analysis_statistics":
            return [TextContent(type="text", text=json.dumps(
                simulator.metrics.get_statistics(), indent=2
            ))]
        
        # NEW: Approval workflow
        if name == "create_approval_workflow":
            return [TextContent(type="text", text=json.dumps(
                simulator.workflow_engine.create_approval_chain(arguments["analysis"]), indent=2
            ))]
        
        # NEW: CI/CD validation
        if name == "validate_deployment_config":
            return [TextContent(type="text", text=json.dumps(
                simulator.cicd_validator.validate_deployment_config(arguments["config"]), indent=2
            ))]
        
        if name == "validate_pipeline_stage":
            return [TextContent(type="text", text=json.dumps(
                simulator.cicd_validator.validate_pipeline_stage(
                    arguments["stage"],
                    arguments["config"]
                ), indent=2
            ))]

        raise ValueError(f"Unknown tool: {name}")

    # -------- Run --------

    async with mcp.server.stdio.stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())