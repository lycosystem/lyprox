"""Make the `SITES` available in every template, e.g. for the navbar dropdown."""

from typing import Any

from lyprox.sites.views import SITES


def sites(_request) -> dict[str, Any]:
    """Return the defined sites for use in the templates."""
    return {"navbar_sites": SITES}
