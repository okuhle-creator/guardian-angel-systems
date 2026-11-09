import sys
import os

# Automatically add backend/ to sys.path so 'import app' resolves directly to backend/app
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
if os.path.exists(backend_dir) and backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
