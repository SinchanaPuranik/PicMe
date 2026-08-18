import sys
import os
sys.path.insert(0, os.getcwd())

print("Testing imports...")
try:
    print("1. Importing Flask...")
    from flask import Flask
    print("   OK")
    
    print("2. Importing config...")
    from config import config
    print("   OK")
    
    print("3. Importing app package...")
    import app
    print("   OK")
    
    print("4. Creating app...")
    from app import create_app
    application = create_app('development')
    print("   OK - App created!")
    
except Exception as e:
    import traceback
    print(f"\nERROR: {e}")
    traceback.print_exc()
