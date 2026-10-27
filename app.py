"""
Compatibility shim: forwards all 'app.*' imports to 'backend.*'
so that old references continue to work seamlessly.
"""
import sys
from importlib.abc import MetaPathFinder

class AppRedirectFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "app" or fullname.startswith("app."):
            backend_name = "backend" + fullname[3:]
            mod = __import__(backend_name, fromlist=["*"])
            sys.modules[fullname] = sys.modules[backend_name]
            return getattr(sys.modules[backend_name], "__spec__", None)
        return None

if not any(isinstance(f, AppRedirectFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, AppRedirectFinder())

try:
    import backend
    sys.modules["app"] = backend
except Exception:
    pass
