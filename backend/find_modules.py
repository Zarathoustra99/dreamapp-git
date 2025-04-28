#!/usr/bin/env python3
"""
Diagnostic script to find Python modules and paths in Azure.
"""
import os
import sys
import importlib.util

def check_module(module_name):
    """Check if a module can be imported and report details."""
    print(f"Checking module: {module_name}")
    try:
        spec = importlib.util.find_spec(module_name)
        if spec:
            print(f"  ✓ Module {module_name} found at: {spec.origin}")
            return True
        else:
            print(f"  ✗ Module {module_name} not found in sys.path")
            return False
    except ImportError as e:
        print(f"  ✗ Error checking {module_name}: {e}")
        return False

def find_module_files(root_dir, module_name):
    """Find all files that might be part of the module."""
    print(f"Searching for {module_name} in {root_dir}...")
    results = []
    for root, dirs, files in os.walk(root_dir):
        if module_name in dirs:
            module_path = os.path.join(root, module_name)
            print(f"  Found potential module directory: {module_path}")
            print(f"  Contents: {os.listdir(module_path)}")
            if "__init__.py" in os.listdir(module_path):
                print(f"  ✓ Valid Python package: contains __init__.py")
                results.append(module_path)
            else:
                print(f"  ✗ Not a valid Python package: missing __init__.py")
    return results

if __name__ == "__main__":
    print("\n=== Python Environment Information ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print("\n=== Python Path ===")
    for i, path in enumerate(sys.path):
        print(f"{i+1}. {path} {'(exists)' if os.path.exists(path) else '(not found)'}")
    
    print("\n=== Module Check ===")
    modules_to_check = ["app", "app.main", "fastapi", "uvicorn", "gunicorn"]
    for module in modules_to_check:
        check_module(module)
    
    print("\n=== Directory Structure ===")
    print(f"Contents of current directory: {os.listdir('.')}")
    
    print("\n=== Module Search ===")
    find_module_files(os.getcwd(), "app")
    
    print("\n=== Attempting Module Import ===")
    print("Trying to import app.main and get app...")
    try:
        # Try modifying system path and importing
        possible_dirs = [".", "..", "../..", "app", "dreamapp-auth"]
        for d in possible_dirs:
            if os.path.exists(d):
                abs_path = os.path.abspath(d)
                print(f"Adding {abs_path} to sys.path")
                sys.path.insert(0, abs_path)
        
        from app.main import app
        print("✓ Successfully imported app.main.app!")
        print(f"App type: {type(app)}")
    except ImportError as e:
        print(f"✗ Failed to import app.main: {e}")
        
    print("\nDiagnostic complete.")