# ------------------------------------------------------------
# LEVEL-70 PLUGIN LOADER
# ------------------------------------------------------------
# Automatically loads custom plugin files.
# If plugin missing or broken → system safely falls back
# to default implementation (NO CRASH).
# ------------------------------------------------------------

import importlib

def load_plugin(name, default):
    try:
        module = importlib.import_module(f"plugins.{name}")
        if hasattr(module, name):
            return getattr(module, name)
        return default
    except Exception:
        return default
