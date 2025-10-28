#!/usr/bin/env python3
"""Simple test script for Ollama integration - uses only built-in libraries."""

import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Ollama configuration
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:latest"

def make_request(url, data=None, method="GET"):
    """Make HTTP request using urllib."""
    try:
        req = Request(url, data=data, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
        
        with urlopen(req) as response:
            return response.read().decode('utf-8'), response.status
    except HTTPError as e:
        return e.read().decode('utf-8'), e.code
    except URLError as e:
        raise Exception(f"Connection error: {e}")

def test_ollama():
    """Test basic Ollama functionality."""
    
    print("Testing Ollama connection...")
    print(f"URL: {OLLAMA_URL}")
    print(f"Model: {MODEL}")
    print("=" * 50)
    
    # Test 1: Check if Ollama is running
    print("\nTest 1: Checking Ollama status...")
    try:
        response, status = make_request(f"{OLLAMA_URL}/api/tags")
        if status == 200:
            print("OK: Ollama is running!")
            data = json.loads(response)
            models = data.get("models", [])
            print(f"Available models: {', '.join([m['name'] for m in models])}")
        else:
            print(f"ERROR: Ollama returned status code: {status}")
            return
    except Exception as e:
        print(f"ERROR: Cannot connect to Ollama: {e}")
        print("  Make sure Ollama is running. Try: ollama serve")
        return
    
    # Test 2: Simple chat request
    print("\n" + "=" * 50)
    print("Test 2: Simple chat request...")
    test_questions = [
        "What is 2+2?",
        "Explain photosynthesis in one sentence.",
        "Who is Albert Einstein?"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        print("-" * 50)
        
        try:
            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": question}
                ],
                "stream": False
            }
            
            data = json.dumps(payload).encode('utf-8')
            response, status = make_request(
                f"{OLLAMA_URL}/api/chat",
                data=data,
                method="POST"
            )
            
            if status == 200:
                result = json.loads(response)
                answer = result.get("message", {}).get("content", "")
                print(f"Answer: {answer[:200]}...")
            else:
                print(f"Error: Status code {status}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Test 3: JSON format output
    print("\n" + "=" * 50)
    print("Test 3: JSON format output...")
    print("\nQuestion: What is quantum computing in JSON format?")
    print("-" * 50)
    
    try:
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that outputs valid JSON."},
                {"role": "user", "content": "What is quantum computing? Return your answer as a JSON object with a 'definition' field."}
            ],
            "format": "json",
            "stream": False
        }
        
        data = json.dumps(payload).encode('utf-8')
        response, status = make_request(
            f"{OLLAMA_URL}/api/chat",
            data=data,
            method="POST"
        )
        
        if status == 200:
            result = json.loads(response)
            content = result.get("message", {}).get("content", "")
            print(f"Raw response: {content}")
            
            # Try to parse as JSON
            try:
                parsed = json.loads(content)
                print(f"OK: Parsed JSON: {json.dumps(parsed, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse JSON: {e}")
        else:
            print(f"Error: Status code {status}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")

if __name__ == "__main__":
    test_ollama()
