from .pychrome import patch_pychrome


def patch_all():
    """Apply all custom patches."""
    patch_pychrome()
