import os

# Extend package search path to include backend/app
_backend_app = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", "app")
if os.path.exists(_backend_app) and _backend_app not in __path__:
    __path__.append(_backend_app)
