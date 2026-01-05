#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launch script for Todo App
"""
import os
import sys
import subprocess

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Application file name
app_file = "工作待办清单桌面应用_精美版.py"
app_path = os.path.join(script_dir, app_file)

print("=" * 50)
print("Todo App Launcher")
print("=" * 50)
print()
print(f"Current directory: {os.getcwd()}")
print(f"Application file: {app_path}")
print()

# Check if file exists
if not os.path.exists(app_path):
    print(f"ERROR: Application file not found!")
    print(f"File path: {app_path}")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Check Python
print("[1/3] Checking Python...")
try:
    result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
    print(result.stdout.strip())
except Exception as e:
    print(f"ERROR: {e}")
    input("\nPress Enter to exit...")
    sys.exit(1)
print()

# Check Flask
print("[2/3] Checking Flask...")
try:
    import flask
    print(f"Flask version: {flask.__version__}")
except ImportError:
    print("Flask not found, installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "flask"], check=True)
    print("Flask installed successfully!")
print()

# Start application
print("[3/3] Starting application...")
print()
print("Browser will open automatically in a few seconds")
print("Keep this window open")
print("Press Ctrl+C to stop the server")
print()
print()

# Run application
try:
    subprocess.run([sys.executable, app_path], cwd=script_dir)
except KeyboardInterrupt:
    print("\n\nApplication stopped by user")
except Exception as e:
    print(f"\n\nERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 50)
print("Application stopped")
print("=" * 50)
input("\nPress Enter to exit...")

