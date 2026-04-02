"""
Simple test suite for VECTOR module endpoints
Run with: python test_modules.py
"""
import requests
import json

BASE = "http://localhost:5000"

def test_tasks():
    print("\n=== Testing TASKS Module ===")
    
    # Create task
    r = requests.post(f"{BASE}/api/tasks", json={
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high"
    })
    print(f"Create task: {r.status_code} - {r.json()}")
    assert r.status_code == 201
    
    # List tasks
    r = requests.get(f"{BASE}/api/tasks")
    print(f"List tasks: {r.status_code} - Found {len(r.json())} tasks")
    assert r.status_code == 200
    assert len(r.json()) > 0
    
    # Update task
    task_id = r.json()[0]['id']
    r = requests.patch(f"{BASE}/api/tasks/{task_id}", json={"status": "completed"})
    print(f"Update task: {r.status_code}")
    assert r.status_code == 200
    
    print("✓ Tasks module working!")

def test_memory():
    print("\n=== Testing MEMORY Module ===")
    
    # Create memory
    r = requests.post(f"{BASE}/api/memory", json={
        "title": "Test Memory",
        "content": "This is a test memory item",
        "tags": "test,automated"
    })
    print(f"Create memory: {r.status_code} - {r.json()}")
    assert r.status_code == 201
    
    # List memories
    r = requests.get(f"{BASE}/api/memory")
    print(f"List memories: {r.status_code} - Found {len(r.json())} memories")
    assert r.status_code == 200
    
    # Search memories
    r = requests.get(f"{BASE}/api/memory?query=test")
    print(f"Search memories: {r.status_code} - Found {len(r.json())} results")
    assert r.status_code == 200
    
    print("✓ Memory module working!")

def test_retrieval():
    print("\n=== Testing RETRIEVAL Module ===")
    
    # Get settings
    r = requests.get(f"{BASE}/api/retrieval/settings")
    print(f"Get settings: {r.status_code} - {r.json()}")
    assert r.status_code == 200
    assert 'web_enabled' in r.json()
    
    # Update settings
    r = requests.post(f"{BASE}/api/retrieval/settings", json={
        "web_enabled": 1,
        "images_enabled": 1,
        "safe_search": "moderate"
    })
    print(f"Update settings: {r.status_code}")
    assert r.status_code == 200
    
    # Get logs
    r = requests.get(f"{BASE}/api/retrieval/logs")
    print(f"Get logs: {r.status_code} - Found {len(r.json())} logs")
    assert r.status_code == 200
    
    print("✓ Retrieval module working!")

def test_systems():
    print("\n=== Testing SYSTEMS Module ===")
    
    # Get status
    r = requests.get(f"{BASE}/api/systems/status")
    print(f"Get status: {r.status_code}")
    assert r.status_code == 200
    
    status = r.json()
    print(f"  LLM: {status['llm']['status']} ({status['llm']['model']})")
    print(f"  Web: {status['web']['status']}")
    print(f"  Images: {status['images']['status']}")
    
    assert 'llm' in status
    assert 'web' in status
    assert 'images' in status
    
    print("✓ Systems module working!")

def test_robots():
    print("\n=== Testing ROBOTS Module ===")
    
    # List robots
    r = requests.get(f"{BASE}/api/robots")
    print(f"List robots: {r.status_code} - Found {len(r.json())} robots")
    assert r.status_code == 200
    assert len(r.json()) > 0
    
    # Get SimBot-01
    robots = r.json()
    simbot = next((r for r in robots if r['name'] == 'SimBot-01'), None)
    assert simbot is not None
    print(f"  SimBot-01: {simbot['status']} - Capabilities: {simbot['capabilities']}")
    
    # Send command
    r = requests.post(f"{BASE}/api/robots/{simbot['id']}/command", json={
        "command": "move",
        "args": [10]
    })
    print(f"Send command: {r.status_code} - {r.json()}")
    assert r.status_code == 200
    
    # Test E-STOP
    r = requests.post(f"{BASE}/api/robots/estop", json={"active": True})
    print(f"Activate E-STOP: {r.status_code}")
    assert r.status_code == 200
    
    # Try command with E-STOP active (should fail)
    r = requests.post(f"{BASE}/api/robots/{simbot['id']}/command", json={
        "command": "move",
        "args": [10]
    })
    print(f"Command with E-STOP: {r.status_code} (should be 403)")
    assert r.status_code == 403
    
    # Deactivate E-STOP
    r = requests.post(f"{BASE}/api/robots/estop", json={"active": False})
    print(f"Deactivate E-STOP: {r.status_code}")
    assert r.status_code == 200
    
    print("✓ Robots module working!")

if __name__ == "__main__":
    print("="*60)
    print("VECTOR MODULE ENDPOINT TESTS")
    print("="*60)
    print("\nMake sure the server is running at http://localhost:5000")
    print("Press Enter to start tests...")
    input()
    
    try:
        test_tasks()
        test_memory()
        test_retrieval()
        test_systems()
        test_robots()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server at http://localhost:5000")
        print("Make sure the server is running with: python web_server.py")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
