"""
Compatibility shim: forwards all 'backend.*' imports to 'app.*'
so that any references continue to work seamlessly.
"""
import sys
from importlib.abc import MetaPathFinder

class BackendRedirectFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "backend" or fullname.startswith("backend."):
            app_name = "app" + fullname[7:]
            mod = __import__(app_name, fromlist=["*"])
            sys.modules[fullname] = sys.modules[app_name]
            return getattr(sys.modules[app_name], "__spec__", None)
        return None

if not any(isinstance(f, BackendRedirectFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, BackendRedirectFinder())

try:
    import app
    sys.modules["backend"] = app
except Exception:
    pass
