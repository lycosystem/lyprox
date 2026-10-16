"""Code that Django needs to register and load the app.

Like the `DataExplorerConfig`, the `SitesConfig` sets ``add_to_navbar`` to ``True``,
which tells the `lyprox.context_processors.navbar_apps` context processor to include
this app's ``sites/navbar.html`` template in the main navigation bar.
"""

from django.apps import AppConfig


class SitesConfig(AppConfig):
    """Configuration for the sites app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "lyprox.sites"
    add_to_navbar = True
    """Tell the navbar context processor to add an entry for this app."""
