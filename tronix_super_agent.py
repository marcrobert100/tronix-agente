#!/usr/bin/env python3
"""
TRONIX Super Agent v1.0 - Coding Agent via 9Router
Simple, direct coding agent using OpenAI API + 9Router.
No Docker, no complex dependencies.
"""
import os
import sys
import json
import subprocess
import openai

API_BASE = "http://localhost:20128/v1"
API_KEY = "sk-023b1b6cd521b683-n4hcv0-3f5ece0f"
MODEL = "openrouter/minimax/minimax-m3"

SYSTEM_PROMPT = """You are TRONIX Super Agent, an expert coding assistant.
You can read, write, and edit files. You can run shell commands.
Always provide the EXACT file changes needed.
When creating files, output the COMPLETE file content.
When editing, show the exact old->new replacement."""

def chat(messages, model=MODEL):
    client = openai.OpenAI(base_url=API_BASE, api_key=API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        max_tokens=4096
    )
    return response.choices[0].message.content

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out after 30s"
    except Exception as e:
        return f"Error: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python tronix_super_agent.py 'task description'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    
    print("=" * 50)
    print("  TRONIX SUPER AGENT v1.0")
    print("  Powered by 9Router + " + MODEL)
    print("=" * 50)
    print(f"  Task: {task}")
    print("=" * 50)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task}
    ]
    
    response = chat(messages)
    print("\nAI Response:")
    print("-" * 50)
    print(response)
    print("-" * 50)
    
    # Check if response contains file operations
    if "```" in response:
        print("\n[DETECTED] Code block found.")
    
    print("\nDone. Response saved to last_response.txt")
    with open("last_response.txt", "w", encoding="utf-8") as f:
        f.write(response)

if __name__ == "__main__":
    main()
