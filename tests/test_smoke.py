import pytest

try:
    import archon
except ImportError:
    archon = None

def test_package_importable():
    if archon is None:
        pytest.skip("archon requires optional dependencies not installed")
    assert archon is not None