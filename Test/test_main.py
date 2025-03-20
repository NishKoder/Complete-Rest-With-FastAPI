# Python
from storeapi import main


def test_main_import():
    assert hasattr(main, "__name__")
