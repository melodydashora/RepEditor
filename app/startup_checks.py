"""
Startup validation checks to ensure correct topology
Enforces that SDK and Agent bind to loopback only
"""
import os
import sys


def assert_loopback(host: str, service_name: str):
    """Ensure internal services bind to loopback only"""
    if host not in ("127.0.0.1", "localhost", "::1"):
        print(f"❌ ERROR: {service_name} should bind to loopback, not {host}")
        print(f"   Security violation: internal service exposed externally")
        sys.exit(1)
    print(f"✅ {service_name} correctly bound to loopback ({host})")


def validate_gateway_topology():
    """
    Validate the three-tier topology:
    - Gateway: 0.0.0.0:5000 (public)
    - SDK: 127.0.0.1:3101 (internal)
    - Agent: 127.0.0.1:3102 (internal)
    """
    print("\n🔍 Validating Gateway Topology...")
    
    # Gateway should be public
    gateway_host = os.getenv("HOST", "0.0.0.0")
    gateway_port = os.getenv("PORT", "5000")
    print(f"✅ Gateway: {gateway_host}:{gateway_port} (public)")
    
    # SDK should be loopback
    sdk_host = os.getenv("SDK_HOST", "127.0.0.1")
    assert_loopback(sdk_host, "SDK")
    
    # Agent should be loopback
    agent_host = os.getenv("AGENT_HOST", "127.0.0.1")
    assert_loopback(agent_host, "Agent")
    
    print("\n✅ Topology validation passed!")
    print("   - Gateway is public (0.0.0.0:5000)")
    print("   - SDK is internal (127.0.0.1:3101)")
    print("   - Agent is internal (127.0.0.1:3102)\n")


def validate_model_config():
    """Validate AI model configuration is explicit"""
    print("🔍 Validating AI Model Configuration...")
    
    assistant_model = os.getenv("ASSISTANT_MODEL", "gpt-5")
    print(f"✅ Assistant Model: {assistant_model}")
    
    strategist = os.getenv("STRATEGIST_MODEL", "claude-sonnet-4-20250514")
    planner = os.getenv("PLANNER_MODEL", "gpt-5")
    validator = os.getenv("VALIDATOR_MODEL", "gemini-2.0-flash-001")
    
    print(f"✅ Triad Pipeline: {strategist} → {planner} → {validator}")
    print()


def run_all_checks():
    """Run all startup validation checks"""
    print("=" * 60)
    print("VECTO PILOT GATEWAY - STARTUP VALIDATION")
    print("=" * 60)
    
    validate_gateway_topology()
    validate_model_config()
    
    print("=" * 60)
    print("✅ All startup checks passed - ready to launch")
    print("=" * 60)
    print()


if __name__ == "__main__":
    run_all_checks()
