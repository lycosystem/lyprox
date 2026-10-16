"""Views and metadata for the tumor sites beyond head and neck.

The `SITES` dictionary is the single place where a site is defined. Its keys are used
in the URLs (e.g. ``/sites/breast/``) and its entries are used to render both the
"Other Sites" dropdown in the navbar and the site's landing page. Adding a new site
therefore only requires adding an entry here and writing its introduction text in
``templates/sites/intro/<site>.html``.
"""

from django.http import Http404
from django.shortcuts import render

from lyprox.views import add_publications_to_context

SITES = {
    "breast": {
        "name": "Breast",
        "title": "Breast Cancer",
        "cancer_type": "breast cancer",
        "description": "Patterns of lymphatic progression in breast cancer patients.",
        "repo_name": "lycosystem/lydata-breast",
        "image": None,
        "card_image": None,
        "references": [],
    },
    "prostate": {
        "name": "Prostate",
        "title": "Prostate Cancer",
        "cancer_type": "prostate cancer",
        "description": "Patterns of lymphatic progression in prostate cancer patients.",
        "repo_name": "lycosystem/lydata-prostate",
        "image": "Pelvic_LNLs.svg",
        "card_image": "Pelvic_LNLs.svg",
        "references": [],
    },
}
"""All sites that get their own landing page, keyed by their URL slug.

Each entry may define an ``image`` (path relative to the static files, e.g.
``"breast-lymph-schematic.png"``) shown next to the introduction, and a list of
``references`` (DOIs) that are rendered as publications at the bottom of the page.
The optional ``card_image`` (also relative to the static files, ideally in a 2:1
aspect ratio) is shown on the card linking to the site from the main landing page.
"""


def landing(request, site: str):
    """Render the landing page of the given ``site``.

    Raise a 404 error if the ``site`` is not defined in `SITES`. Django's `render`
    accepts a list of template names and uses the first one that exists. This way, a
    site may provide its own ``sites/landing/<site>.html`` template, but falls back to
    the generic ``sites/landing/default.html`` otherwise.

    The site's ``references`` are resolved to publications via Crossref, using the
    same (cached) function as the main landing page.
    """
    if site not in SITES:
        raise Http404(f"Site '{site}' does not exist.")

    context = {"site_key": site, "site": SITES[site]}
    context = add_publications_to_context(
        context=context,
        dois=SITES[site]["references"],
    )
    templates = [f"sites/landing/{site}.html", "sites/landing/default.html"]
    return render(request, templates, context)
