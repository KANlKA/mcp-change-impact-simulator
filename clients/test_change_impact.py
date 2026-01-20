#!/usr/bin/env python3
"""
Test client for Change Impact Simulator MCP Server
Demonstrates all capabilities without requiring Claude API
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from change_impact_simulator_server import ChangeImpactSimulatorServer


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))


def test_knowledge_search():
    """Test knowledge base search"""
    print_section("TEST 1: Knowledge Base Search")
    
    server = ChangeImpactSimulatorServer()
    
    queries = ["replica", "backup", "scaling"]
    
    for query in queries:
        print(f"\n🔍 Searching for: '{query}'")
        results = server.search_knowledge(query)
        print(f"Found {len(results)} results:")
        for result in results[:2]:  # Show first 2 results
            print(f"  - {result['title']}")
            print(f"    Category: {result['category']}")
            print(f"    Relevance: {result['relevance']}")


def test_analyze_change():
    """Test change analysis"""
    print_section("TEST 2: Change Analysis")
    
    server = ChangeImpactSimulatorServer()
    
    test_changes = [
        "What happens if I reduce replicas from 3 to 1?",
        "I want to increase replicas from 2 to 5",
        "Changing backup frequency from daily to weekly",
        "Enable new authentication feature flag"
    ]
    
    for change_desc in test_changes:
        print(f"\n📊 Analyzing: '{change_desc}'")
        analysis = server.analyze_change(change_desc)
        
        print(f"\nRisk Level: {analysis['risk_level']}")
        print(f"Pattern: {analysis.get('matched_pattern', 'UNKNOWN')}")
        
        if analysis.get('impact'):
            print("\nImpacts:")
            for impact in analysis['impact'][:3]:
                print(f"  - {impact}")
        
        if analysis.get('safeguards'):
            print("\nSafeguards:")
            for safeguard in analysis['safeguards'][:2]:
                print(f"  - {safeguard}")
        
        print(f"\nManual Review Required: {analysis.get('requires_manual_review', False)}")


def test_review_task_creation():
    """Test review task creation"""
    print_section("TEST 3: Review Task Creation")
    
    server = ChangeImpactSimulatorServer()
    
    # Analyze a high-risk change
    change_desc = "Reduce replicas from 3 to 1"
    print(f"Analyzing: '{change_desc}'")
    analysis = server.analyze_change(change_desc)
    
    print(f"\nRisk Level: {analysis['risk_level']}")
    
    # Create review task
    print("\nCreating review task...")
    task = server.create_review_task(analysis)
    
    print_json(task)


def test_supported_changes():
    """Test listing supported changes"""
    print_section("TEST 4: Supported Changes")
    
    server = ChangeImpactSimulatorServer()
    
    changes = server.list_supported_changes()
    
    print(f"Total supported change types: {len(changes)}\n")
    
    for change in changes:
        print(f"📌 {change['name']}")
        print(f"   Risk: {change['risk_level']}")
        print(f"   Example: {change['example']}")
        print()


def test_complete_workflow():
    """Test complete workflow - the DEMO scenario"""
    print_section("TEST 5: Complete Workflow (DEMO SCENARIO)")
    
    server = ChangeImpactSimulatorServer()
    
    # User query
    user_query = "What happens if I reduce replicas from 3 to 1?"
    print(f"👤 USER QUERY:\n{user_query}\n")
    
    # Step 1: Search knowledge
    print("STEP 1: Search Knowledge Base")
    knowledge = server.search_knowledge("replica")
    print(f"Found {len(knowledge)} relevant knowledge entries\n")
    
    # Step 2: Analyze change
    print("STEP 2: Analyze Change")
    analysis = server.analyze_change(user_query)
    
    # Step 3: Create review task if needed
    print("STEP 3: Check if Review Task Needed")
    task = server.create_review_task(analysis)
    
    # Step 4: Format final response (as Claude would present it)
    print("\n" + "=" * 80)
    print("  🤖 CLAUDE RESPONSE (via HAWCC)")
    print("=" * 80 + "\n")
    
    print(f"Risk Level: {analysis['risk_level']}\n")
    
    print("Impact:")
    for impact in analysis.get('impact', []):
        print(f"  - {impact}")
    
    print("\nSafe Conditions:")
    for condition in analysis.get('safe_conditions', []):
        print(f"  - {condition}")
    
    print("\nRecommended Safeguards:")
    for safeguard in analysis.get('safeguards', []):
        print(f"  - {safeguard}")
    
    if task.get('task_created'):
        print("\nAdvisory Action:")
        print("  - Manual review recommended")
    
    print("\n" + "─" * 80)
    print("⚠️  Nothing is executed. This is purely advisory.")
    print("─" * 80 + "\n")


def main():
    """Run all tests"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║          CHANGE IMPACT SIMULATOR MCP SERVER - TEST SUITE            ║
    ║                                                                      ║
    ║  Testing all MCP tools and demonstrating complete workflow          ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        test_knowledge_search()
        test_analyze_change()
        test_review_task_creation()
        test_supported_changes()
        test_complete_workflow()
        
        print_section("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        
        print("""
Next Steps:
1. Run the MCP server: python src/change_impact_simulator_server.py
2. Connect via Claude Desktop (HAWCC) - see QUICKSTART.md
3. Try the demo query: "What happens if I reduce replicas from 3 to 1?"
        """)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()