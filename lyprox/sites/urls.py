"""Defines the URLs of the sites app.

There is only one URL pattern, ``/sites/<site>/``, which renders the landing page of
the given site via the `landing` view. The ``<slug:site>`` part captures the site's key
from the URL (e.g. ``breast``) and passes it to the view as the ``site`` argument.
"""

from django.urls import path

from lyprox.sites import views

app_name = "sites"
urlpatterns = [
    path("<slug:site>/", views.landing, name="landing"),
]
