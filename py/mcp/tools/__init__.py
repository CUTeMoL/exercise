import importlib
import logging
import pkgutil

logger = logging.getLogger(__name__)


def register_all_tools(mcp):
    for _, name, _ in pkgutil.iter_modules(__path__):
        try:
            module = importlib.import_module(f"{__name__}.{name}")
            if hasattr(module, "register_tools"):
                module.register_tools(mcp)
        except Exception as e:
            logger.warning("skipping %s: %s", name, e)
