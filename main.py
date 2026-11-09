import sys
import os

# Ensure backend folder is in Python path whether executed from root or backend/
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if os.path.exists(backend_path) and backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
