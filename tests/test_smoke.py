import importlib
import pkgutil
import pytest

import archon


def test_package_importable():
    assert archon is not None


def test_import_all_submodules():
    errors = []
    for mod in pkgutil.walk_packages(archon.__path__, archon.__name__ + "."):
        try:
            importlib.import_module(mod.name)
        except Exception as exc:
            errors.append(f"{mod.name}: {exc}")
    if errors:
        pytest.fail("Submodule import failures:\n" + "\n".join(errors))
